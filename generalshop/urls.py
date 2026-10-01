from django.urls import path

from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("products/<int:pk>/", views.product_detail, name="product-detail"),
    path("products/new/", views.create_product, name="create-product"),
    path("videos/new/", views.add_video, name="add-video"),
    path("cart/", views.cart, name="cart"),
    path("cart/update/", views.update_cart, name="update-cart"),
    path("petty-costs/", views.petty_costs, name="petty-costs"),
]
