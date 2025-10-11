"""
URL configuration for myDjangoApp project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls.static import static

from django.contrib import admin
from django.urls import path
from Rari import views as views
from django.urls import path

from Rari.views import ArtisanDetailView

urlpatterns = [
    path('admin/', admin.site.urls),

    # Home
    path('', views.home, name="home"),

    # Products
    path('products/', views.product_list, name="product_list"),
    path('products/category/<int:category_id>/', views.product_list, name="product_list_by_category"),
    path('products/<int:product_id>/', views.product_detail, name="product_detail"),

    # Cart & Checkout
    path('cart/', views.cart_detail, name="cart_detail"),
    path('cart/add/<int:product_id>/', views.add_to_cart, name="add_to_cart"),
    path('checkout/', views.checkout, name="checkout"),
    path('about/', views.about, name="about"),
    path("contact/", views.contact, name="contact"),
    path("register/", views.register, name="register"),
    path("login/", views.login_view, name="login"),
    path("products/", views.products, name="products"),
    path('stories/', views.stories_list, name='stories'),  # All stories page
    path('stories/<int:pk>/', views.story_detail, name='story_detail'),  # Single story page
    path("artisans/", views.artisans_list, name="artisans"),
    path('artisan/<int:artisan_id>/', ArtisanDetailView.as_view(), name="artisan_detail"),
    path("products/category/<int:category_id>/", views.product_list, name="product_list"),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

