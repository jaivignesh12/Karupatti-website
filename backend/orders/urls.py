from django.urls import path
from . import views

urlpatterns = [
    path('', views.list_orders, name='list-orders'),
    path('create/', views.create_order, name='create-order'),
    path('<uuid:order_id>/', views.order_detail, name='order-detail'),
    # Admin
    path('admin/', views.admin_list_orders, name='admin-orders'),
    path('admin/<uuid:order_id>/status/', views.update_order_status, name='update-order-status'),
]
