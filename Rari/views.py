from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Product, Category, Artisan, Story, Order, OrderItem, Customer
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth import logout
from django.shortcuts import redirect
from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from django.shortcuts import render
from .models import Story, Product, Category

from django.db.models import Q

def home(request):
    query = request.GET.get("q", "")
    search_type = request.GET.get("type", "all")

    stories = Story.objects.all()[:3]
    categories = Category.objects.all()

    # Start with all products
    products = Product.objects.all().order_by("-created_at")
    artisans = Artisan.objects.all()
    filtered_categories = categories

    # Apply search only if query exists
    if query:
        if search_type == "product":
            products = products.filter(Q(name__icontains=query) | Q(description__icontains=query))
        elif search_type == "category":
            filtered_categories = categories.filter(name__icontains=query)
        elif search_type == "artisan":
            artisans = artisans.filter(Q(shop_name__icontains=query) | Q(bio__icontains=query))
        else:  # "all" searches everything
            products = products.filter(Q(name__icontains=query) | Q(description__icontains=query))
            filtered_categories = categories.filter(name__icontains=query)
            artisans = artisans.filter(Q(shop_name__icontains=query) | Q(bio__icontains=query))

    # Slice products for homepage display
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




from math import floor

from math import floor
from django.core.paginator import Paginator
from django.shortcuts import render
from .models import Product, Category

def product_list(request):
    products = Product.objects.all()
    categories = Category.objects.all()

    # ----- Filtering by category -----
    category_id = request.GET.get('category')
    if category_id:
        products = products.filter(category_id=category_id)

    # ----- Sorting -----
    sort_option = request.GET.get('sort')
    if sort_option == 'price_asc':
        products = products.order_by('discount_price', 'price')
    elif sort_option == 'price_desc':
        products = products.order_by('-discount_price', '-price')
    elif sort_option == 'newest':
        products = products.order_by('-created_at')
    elif sort_option == 'best_rated':
        products = products.order_by('-rating')

    # ----- Pagination -----
    products = products.order_by('id')
    paginator = Paginator(products, 12)  # 12 products per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # ----- Prepare star lists for each product -----
    for product in page_obj:
        full_stars = int(floor(product.rating))
        half_star = 1 if (product.rating - full_stars) >= 0.5 else 0
        empty_stars = 5 - full_stars - half_star
        product.star_list = {
            'full': range(full_stars),
            'half': range(half_star),
            'empty': range(empty_stars),
        }

    context = {
        'products': page_obj,
        'categories': categories,
    }
    return render(request, 'products.html', context)




# Product Detail Page
def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    return render(request, "product_detail.html", {"product": product})


from django.views.generic import DetailView
from django.shortcuts import get_object_or_404
from .models import Artisan

class ArtisanDetailView(DetailView):
    model = Artisan
    template_name = "artisan_detail.html"
    context_object_name = "artisan"

    def get_object(self):
        # Fetch artisan by ID from URL
        artisan_id = self.kwargs.get("artisan_id")
        return get_object_or_404(Artisan, id=artisan_id)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        artisan = self.object
        # Assuming related_name='products' and 'stories' in related models
        context["products"] = artisan.products.all()
        context["stories"] = artisan.stories.all()
        return context



# Add Product to Cart
@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    customer = get_object_or_404(Customer, user=request.user)
    order, created = Order.objects.get_or_create(customer=customer, status="Pending")

    # If item already in cart, increase quantity
    order_item, item_created = OrderItem.objects.get_or_create(order=order, product=product)
    if not item_created:
        order_item.quantity += 1
        order_item.save()

    return redirect("cart_detail")


# View Cart
@login_required
def cart_detail(request):
    customer = get_object_or_404(Customer, user=request.user)
    order = Order.objects.filter(customer=customer, status="Pending").first()
    return render(request, "cart_detail.html", {"order": order})


# Checkout (basic version)
@login_required
def checkout(request):
    customer = get_object_or_404(Customer, user=request.user)
    order = Order.objects.filter(customer=customer, status="Pending").first()

    if order:
        order.status = "Processing"
        order.save()
        # Later: integrate payment gateway here
        return render(request, "checkout_success.html", {"order": order})

    return redirect("cart_detail")
from django.shortcuts import render

# Create your views here.
def about(request):
    return render(request, "about.html")
def contact(request):
    return render(request, "contact.html")


# views.py
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib import messages


from django.contrib.auth import login

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

        # Password validation
        if password != confirm_password:
            messages.error(request, "Passwords do not match!")
            return render(request, 'register.html')

        # Check if user already exists
        if User.objects.filter(username=email).exists():
            messages.error(request, "Email is already registered!")
            return render(request, 'register.html')

        # Create user
        user = User.objects.create_user(
            username=email,
            email=email,
            password=password,
            first_name=full_name
        )
        user.save()

        # 🔹 Auto login after register
        login(request, user)

        messages.success(request, "Account created successfully!")
        return redirect('home')   # directly go to home page

    return render(request, 'register.html')




def login_view(request):
    if request.method == "POST":
        email = request.POST.get('email')
        password = request.POST.get('password')

        user = authenticate(request, username=email, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, "Login successful!")
            return redirect('home')  # make sure 'home' exists in urls
        else:
            messages.error(request, "Invalid email or password")

    return render(request, "login.html")





def logout_view(request):
    logout(request)  # সেশন / লগইন শেষ করে দিবে
    return redirect('login')


from django.shortcuts import render
from django.core.paginator import Paginator
from .models import Product

def products(request):
    all_products = Product.objects.all().order_by('-created_at')
    paginator = Paginator(all_products, 12)  # 12 products per page
    page_number = request.GET.get('page')
    products_page = paginator.get_page(page_number)

    context = {
        "products": products_page
    }
    return render(request, "products.html", context)




from django.shortcuts import render, get_object_or_404
from .models import Story

def stories_list(request):
    stories = Story.objects.all()
    return render(request, 'stories.html', {'stories': stories})

def story_detail(request, pk):
    story = get_object_or_404(Story, pk=pk)
    return render(request, 'story_detail.html', {'story': story})

# views.py
from django.shortcuts import render
from .models import Artisan

def artisans_list(request):
    query = request.GET.get("q")  # search term
    craft_filter = request.GET.get("craft")  # filter by craft

    artisans = Artisan.objects.all()

    if query:
        artisans = artisans.filter(shop_name__icontains=query) | artisans.filter(bio__icontains=query)

    if craft_filter and craft_filter != "all":
        artisans = artisans.filter(craft__iexact=craft_filter)

    crafts = Artisan.objects.values_list("craft", flat=True).distinct()  # for filter dropdown

    context = {
        "artisans": artisans,
        "crafts": crafts,
        "selected_craft": craft_filter,
        "query": query,
    }
    return render(request, "artisans.html", context)


