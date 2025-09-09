from django.urls import path
from .views import *

urlpatterns = [
    path("", product_list, name="product_list"),
    path("cart/", cart_list, name="cart_list"),
    path("cart/add/", add_to_cart, name="add_to_cart"),
]