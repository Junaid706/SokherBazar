from django.contrib import admin
from django.urls import path
from Rari import views
from Rari.views import ArtisanDetailView
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name="home"),

    # Products
    path('products/', views.product_list, name="product_list"),
    path('products/category/<int:category_id>/', views.product_list, name="product_list_by_category"),
    path('products/<int:product_id>/', views.product_detail, name="product_detail"),

    # Cart & Checkout
    path('cart/', views.cart_detail, name="cart_detail"),
    path('cart/add/<int:product_id>/', views.add_to_cart, name="add_to_cart"),
    path('remove-from-cart/<int:order_item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('checkout/', views.checkout, name="checkout"),

    # Pages
    path('about/', views.about, name="about"),
    path('contact/', views.contact, name="contact"),
    path('faq/', views.faq, name='faq'),

    # Auth
    path('register/', views.register, name="register"),
    path('login/', views.login_view, name="login"),
    path('logout/', views.logout_view, name='logout'),

    # Stories
    path('stories/', views.stories_list, name='stories'),
    path('stories/<int:pk>/', views.story_detail, name='story_detail'),

    # Artisans
    path('artisans/', views.artisans_list, name="artisans"),
    path('artisan/<int:artisan_id>/', ArtisanDetailView.as_view(), name="artisan_detail"),

    # Dashboard
    path('dashboard/', views.dashboard, name='dashboard'),

    path("profile/", views.profile, name="profile"),

# Add these to your existing urlpatterns
    path('profile/wishlist/', views.wishlist_view, name='wishlist'),
    path('wishlist/add/<int:product_id>/', views.add_to_wishlist, name='add_to_wishlist'),
    path('wishlist/remove/<int:product_id>/', views.remove_from_wishlist, name='remove_from_wishlist'),
path('profile/settings/', views.settings, name='settings'),

# Placeholder URLs for future features
path('profile/become-seller/', views.become_seller, name='become_seller'),
path('seller/dashboard/', views.seller_dashboard, name='seller_dashboard'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
