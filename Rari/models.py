from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify

# Artisan (Seller Profile)
class Artisan(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    shop_name = models.CharField(max_length=150)
    phone = models.CharField(max_length=20)
    nid_document = models.ImageField(upload_to="nid_documents/")
    bio = models.TextField(blank=True)
    location = models.CharField(max_length=100, blank=True)
    profile_picture = models.ImageField(upload_to="artisans/", blank=True, null=True)
    joined_date = models.DateTimeField(auto_now_add=True)
    craft = models.CharField(max_length=100, blank=True)  # NEW FIELD
    website = models.URLField(blank=True, null=True)
    is_verified = models.BooleanField(default=False)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.user.username


# Customer (Buyer Profile)
class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=15, blank=True)
    address = models.TextField(blank=True)
    joined_date = models.DateTimeField(auto_now_add=True)
    profile_picture = models.ImageField(upload_to="customers/", blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.user.username


# Category
class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='category_images/', blank=True, null=True)  # 👈 new field
    slug = models.SlugField(max_length=255, blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name)
            slug = base_slug
            counter = 1
            while Category.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


# Product
class Product(models.Model):
    artisan = models.ForeignKey(Artisan, on_delete=models.CASCADE, related_name="products")
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    name = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField(default=1)
    image = models.ImageField(upload_to="products/", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_featured = models.BooleanField(default=False)
    discount_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    is_new = models.BooleanField(default=False)
    is_on_sale = models.BooleanField(default=False)
    rating = models.FloatField(default=0.0)
    rating_count = models.PositiveIntegerField(default=0)
    slug = models.SlugField(max_length=255, blank=True, null=True)  # allow null for now

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name)
            slug = base_slug
            counter = 1
            while Product.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} - {self.artisan.shop_name}"


# Order
class Order(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name="orders")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    STATUS_CHOICES = [
        ("Pending", "Pending"),
        ("Processing", "Processing"),
        ("Shipped", "Shipped"),
        ("Delivered", "Delivered"),
        ("Cancelled", "Cancelled"),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="Pending")

    def __str__(self):
        return f"Order #{self.id} by {self.customer.user.username}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price_at_purchase = models.DecimalField(max_digits=10, decimal_places=2, default=0)  # new field

    def __str__(self):
        return f"{self.quantity} x {self.product.name}"



# Artisan Stories (Storytelling Feature)
class Story(models.Model):
    artisan = models.ForeignKey(Artisan, on_delete=models.CASCADE, related_name="stories")
    title = models.CharField(max_length=200)
    content = models.TextField()
    image = models.ImageField(upload_to="stories/", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    tags = models.CharField(max_length=200, blank=True)  # comma-separated

    def __str__(self):
        return f"{self.title} by {self.artisan.shop_name}"


class Wishlist(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name="wishlists")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('customer', 'product')

    def __str__(self):
        return f"{self.customer.user.username} - {self.product.name}"


class Review(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="reviews")
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    rating = models.PositiveIntegerField(default=5)
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.product.name} - {self.customer.user.username}"

