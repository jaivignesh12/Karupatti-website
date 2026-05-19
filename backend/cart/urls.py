from django.urls import path
from . import views

urlpatterns = [
    path('', views.get_cart, name='get-cart'),
    path('add/', views.add_to_cart, name='add-to-cart'),
    path('items/<uuid:item_id>/', views.update_cart_item, name='update-cart-item'),
    path('items/<uuid:item_id>/remove/', views.remove_cart_item, name='remove-cart-item'),
    path('clear/', views.clear_cart, name='clear-cart'),
]
