from django.urls import path
from . import views

urlpatterns = [
    # Auth
    path('signup/', views.signup, name='signup'),
    path('login/', views.login, name='login'),
    path('admin-login/', views.admin_login, name='admin-login'),
    path('logout/', views.logout, name='logout'),
    path('me/', views.me, name='me'),
    # Profile
    path('profile/', views.profile, name='profile'),
    # Addresses
    path('addresses/', views.addresses, name='addresses'),
    path('addresses/<uuid:address_id>/', views.address_detail, name='address-detail'),
    # Wishlist
    path('wishlist/', views.wishlist, name='wishlist'),
    path('wishlist/toggle/', views.add_to_wishlist, name='toggle-wishlist'),
    path('wishlist/<uuid:item_id>/', views.remove_from_wishlist, name='remove-wishlist'),
    # Admin
    path('admin/users/', views.admin_list_users, name='admin-users'),
]
