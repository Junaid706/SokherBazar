from django.contrib import admin
from .models import Artisan, Customer, Category, Product, Order, OrderItem, Story


# Inline Order Items (so they show inside Order)
class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 1




# Artisan Admin
@admin.register(Artisan)
class ArtisanAdmin(admin.ModelAdmin):
    list_display = (
        "shop_name",
        "user",
        "phone",
        "craft",
        "location",
        "joined_date",
    )
    search_fields = (
        "shop_name",
        "user__username",
        "phone",
        "craft",
        "location",
    )
    list_filter = ("joined_date", "craft", "location")

    # Fields visible in the form (admin detail page)
    fieldsets = (
        ("Basic Info", {
            "fields": ("user", "shop_name", "phone", "craft", "location")
        }),
        ("Profile Details", {
            "fields": ("bio", "profile_picture")
        }),
        ("Verification", {
            "fields": ("nid_document",)
        }),
        ("System", {
            "fields": ("joined_date",),
        }),
    )
    readonly_fields = ("joined_date",)



# Customer Admin
@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ("user", "phone", "joined_date")
    search_fields = ("user__username", "phone")
    list_filter = ("joined_date",)


# Category Admin
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "description")
    search_fields = ("name",)

    def image_preview(self, obj):
        if obj.image:
            return f"<img src='{obj.image.url}' width='50' height='50' style='object-fit:cover;' />"
        return "No Image"

    image_preview.allow_tags = True
    image_preview.short_description = "Preview"


# Product Admin
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "artisan", "category", "price", "stock", "created_at")
    search_fields = ("name", "artisan__shop_name")
    list_filter = ("category", "created_at")
    list_editable = ("price", "stock")


# Order Admin
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "customer", "status", "created_at", "updated_at")
    search_fields = ("customer__user__username",)
    list_filter = ("status", "created_at")
    inlines = [OrderItemInline]  # Show OrderItems inside Orders


# Order Item Admin (not needed separately, but registered for completeness)
@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ("order", "product", "quantity")


# Story Admin
@admin.register(Story)
class StoryAdmin(admin.ModelAdmin):
    list_display = ("title", "artisan", "created_at")
    search_fields = ("title", "artisan__shop_name")
    list_filter = ("created_at",)
