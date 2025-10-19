from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from math import floor
from django.views.generic import DetailView
from django.http import JsonResponse
from decimal import Decimal, InvalidOperation
from .models import Product, Wishlist, Category, Artisan, Story, Order, OrderItem, Customer


# -------------------- HOME --------------------
def home(request):
    query = request.GET.get("q", "")
    search_type = request.GET.get("type", "all")

    stories = Story.objects.all()[:3]
    categories = Category.objects.all()
    products = Product.objects.all().order_by("-created_at")  # no slicing yet
    artisans = Artisan.objects.all()
    filtered_categories = categories

    if query:
        if search_type == "product":
            products = products.filter(Q(name__icontains=query) | Q(description__icontains=query))
        elif search_type == "category":
            filtered_categories = categories.filter(name__icontains=query)
        elif search_type == "artisan":
            artisans = artisans.filter(Q(shop_name__icontains=query) | Q(bio__icontains=query))
        else:
            products = products.filter(Q(name__icontains=query) | Q(description__icontains=query))
            filtered_categories = categories.filter(name__icontains=query)
            artisans = artisans.filter(Q(shop_name__icontains=query) | Q(bio__icontains=query))

    # Slice AFTER filtering
    products = products[:8]

    context = {
        "stories": stories,
        "products": products,
        "categories": filtered_categories,
        "artisans": artisans,
        "is_authenticated": request.user.is_authenticated,
        "total_products": Product.objects.count(),
        "query": query,
        "search_type": search_type,
    }
    return render(request, "home.html", context)



# -------------------- PRODUCTS LIST --------------------
def product_list(request):
    products = Product.objects.all().order_by('-created_at')
    categories = Category.objects.all()

    # Search Filter
    query = request.GET.get('q', '').strip()
    if query:
        products = products.filter(
            Q(name__icontains=query) |
            Q(description__icontains=query) |
            Q(category__name__icontains=query) |
            Q(artisan__shop_name__icontains=query)
        )

    # Category Filter
    category_id = request.GET.get('category')
    if category_id:
        products = products.filter(category_id=category_id)

    # Sorting
    sort_option = request.GET.get('sort')
    if sort_option == 'price_asc':
        products = products.order_by('discount_price', 'price')
    elif sort_option == 'price_desc':
        products = products.order_by('-discount_price', '-price')
    elif sort_option == 'newest':
        products = products.order_by('-created_at')
    elif sort_option == 'best_rated':
        products = products.order_by('-rating')

    # Pagination
    paginator = Paginator(products, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Star Ratings
    for product in page_obj:
        full_stars = int(floor(product.rating))
        half_star = 1 if (product.rating - full_stars) >= 0.5 else 0
        empty_stars = 5 - full_stars - half_star
        product.star_list = {
            'full': range(full_stars),
            'half': range(half_star),
            'empty': range(empty_stars),
        }

    user_wishlist_ids = []
    if request.user.is_authenticated:
        customer = Customer.objects.filter(user=request.user).first()
        if customer:
            user_wishlist_ids = Wishlist.objects.filter(customer=customer).values_list('product_id', flat=True)

    context = {
        'products': page_obj,
        'categories': categories,
        'query': query,
        'user_wishlist_ids': list(user_wishlist_ids),
    }

    return render(request, "products.html", context)


# -------------------- PRODUCT DETAIL --------------------
def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    related_products = Product.objects.filter(category=product.category).exclude(id=product.id)[:4]

    # --- Compute savings and discount percent safely ---
    savings = None
    discount_percent = None
    try:
        if product.discount_price and product.price:
            base = Decimal(str(product.price))
            disc = Decimal(str(product.discount_price))
            savings = base - disc
            if base > 0:
                discount_percent = int((savings / base * 100).quantize(Decimal('1')))
    except (InvalidOperation, TypeError, ValueError):
        pass

    context = {
        "product": product,
        "related_products": related_products,
        "savings": savings,
        "discount_percent": discount_percent,
    }
    return render(request, "product_detail.html", context)

# -------------------- ARTISAN DETAIL --------------------
class ArtisanDetailView(DetailView):
    model = Artisan
    template_name = "artisan_detail.html"
    context_object_name = "artisan"

    def get_object(self):
        artisan_id = self.kwargs.get("artisan_id")
        return get_object_or_404(Artisan, id=artisan_id)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        artisan = self.object
        context["products"] = artisan.products.all()
        context["stories"] = artisan.stories.all()
        return context


# -------------------- CART --------------------
@login_required
def cart_detail(request):
    customer, created = Customer.objects.get_or_create(user=request.user)
    order = Order.objects.filter(customer=customer, status="Pending").first()
    total = 0
    if order:
        for item in order.items.all():
            price = item.product.discount_price if item.product.discount_price else item.product.price
            total += price * item.quantity
    return render(request, "cart_detail.html", {"order": order, "total": total})


def add_to_cart(request, product_id):
    if not request.user.is_authenticated:
        messages.warning(request, "Please log in to add products to your cart.")
        return redirect('login')

    product = get_object_or_404(Product, id=product_id)
    customer = get_object_or_404(Customer, user=request.user)
    order, _ = Order.objects.get_or_create(customer=customer, status="Pending")
    order_item, item_created = OrderItem.objects.get_or_create(order=order, product=product)
    if not item_created:
        order_item.quantity += 1
        order_item.save()
    messages.success(request, f"{product.name} added to cart.")
    return redirect(request.META.get('HTTP_REFERER', 'product_list'))


def remove_from_cart(request, order_item_id):
    if not request.user.is_authenticated:
        messages.warning(request, "Please log in to modify your cart.")
        return redirect('login')

    item = get_object_or_404(OrderItem, id=order_item_id)
    item.delete()
    return redirect('cart_detail')


@login_required
def checkout(request):
    customer = get_object_or_404(Customer, user=request.user)
    order = Order.objects.filter(customer=customer, status="Pending").first()
    if order:
        order.status = "Processing"
        order.save()
        return render(request, "checkout_success.html", {"order": order})
    return redirect("cart_detail")


# -------------------- STATIC PAGES --------------------
def about(request):
    return render(request, "about.html")


def contact(request):
    return render(request, "contact.html")


def faq(request):
    return render(request, "faq.html")


# -------------------- AUTH --------------------
def register(request):
    if request.method == "POST":
        user_type = request.POST.get('user_type')
        full_name = request.POST.get('full_name')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        shop_name = request.POST.get('shop_name')
        phone_number = request.POST.get('phone_number')
        nid_document = request.FILES.get('nid_document')

        if password != confirm_password:
            messages.error(request, "⚠️ Passwords do not match!")
            return render(request, 'register.html')

        if User.objects.filter(username=email).exists():
            messages.error(request, "⚠️ Email is already registered!")
            return render(request, 'register.html')

        user = User.objects.create_user(username=email, email=email, password=password, first_name=full_name)

        if user_type == "artisan":
            if not all([shop_name, phone_number, nid_document]):
                messages.error(request, "⚠️ Please fill in all artisan details!")
                user.delete()
                return render(request, 'register.html')

            Artisan.objects.create(user=user, shop_name=shop_name, phone=phone_number, nid_document=nid_document)
        else:
            Customer.objects.create(user=user, phone=phone_number or "")

        login(request, user)
        messages.success(request, "🎉 Account created successfully!")
        return redirect('home')

    return render(request, 'register.html')


def login_view(request):
    if request.method == "POST":
        email = request.POST.get('email')
        password = request.POST.get('password')
        remember_me = request.POST.get('remember_me')

        try:
            user_obj = User.objects.get(email=email)
            username = user_obj.username
        except User.DoesNotExist:
            messages.error(request, "Invalid email or password")
            return render(request, "login.html")

        user = authenticate(request, username=username, password=password)

        if user is not None:
            if not user.is_active:
                messages.error(request, "Your account is not active. Please verify your email/OTP.")
                return render(request, "login.html")
            login(request, user)
            if not remember_me:
                request.session.set_expiry(0)
            else:
                request.session.set_expiry(None)
            messages.success(request, "Login successful!")
            return redirect('home')
        else:
            messages.error(request, "Invalid email or password")

    return render(request, "login.html")




def logout_view(request):
    logout(request)
    return redirect('home')


# -------------------- STORIES --------------------
def stories_list(request):
    stories = Story.objects.all()
    return render(request, 'stories.html', {'stories': stories})


def story_detail(request, pk):
    story = get_object_or_404(Story, pk=pk)
    return render(request, 'story_detail.html', {'story': story})


# -------------------- ARTISANS --------------------
def artisans_list(request):
    query = request.GET.get("q")
    craft_filter = request.GET.get("craft")
    artisans = Artisan.objects.all()

    if query:
        artisans = artisans.filter(Q(shop_name__icontains=query) | Q(bio__icontains=query))

    if craft_filter and craft_filter != "all":
        artisans = artisans.filter(craft__iexact=craft_filter)

    crafts = Artisan.objects.values_list("craft", flat=True).distinct()

    context = {
        "artisans": artisans,
        "crafts": crafts,
        "selected_craft": craft_filter,
        "query": query,
    }
    return render(request, "artisans.html", context)


# -------------------- DASHBOARD --------------------
@login_required
def dashboard(request):
    customer = Customer.objects.filter(user=request.user).first()
    artisan = Artisan.objects.filter(user=request.user).first()

    total_orders = Order.objects.filter(customer=customer).count() if customer else 0
    active_coupons = []
    recent_orders = Order.objects.filter(customer=customer).order_by('-created_at')[:5] if customer else []

    context = {
        'customer': customer,
        'artisan': artisan,
        'total_orders': total_orders,
        'active_coupons': active_coupons,
        'recent_orders': recent_orders,
    }
    return render(request, 'dashboard.html', context)


@login_required
def profile(request):
    user = request.user

    # Try to get related customer or artisan
    customer = Customer.objects.filter(user=user).first()
    artisan = Artisan.objects.filter(user=user).first()

    context = {
        "user": user,
        "customer": customer,
        "artisan": artisan,
    }
    return render(request, "profile.html", context)





# Add these placeholder views
@login_required
def wishlist_view(request):
    customer = get_object_or_404(Customer, user=request.user)
    wishlist_items = Wishlist.objects.filter(customer=customer).select_related('product')
    return render(request, 'wishlist.html', {'wishlist_items': wishlist_items})

@login_required
def add_to_wishlist(request, product_id):
    customer = get_object_or_404(Customer, user=request.user)
    product = get_object_or_404(Product, id=product_id)
    Wishlist.objects.get_or_create(customer=customer, product=product)
    return redirect('wishlist')

@login_required
def remove_from_wishlist(request, product_id):
    customer = get_object_or_404(Customer, user=request.user)
    Wishlist.objects.filter(customer=customer, product_id=product_id).delete()
    return redirect('wishlist')

@login_required
def settings(request):
    messages.info(request, "Settings page coming soon!")
    return redirect('dashboard')

@login_required
def become_seller(request):
    messages.info(request, "Seller registration coming soon!")
    return redirect('dashboard')

@login_required
def seller_dashboard(request):
    messages.info(request, "Seller dashboard coming soon!")
    return redirect('dashboard')


