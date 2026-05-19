from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.dashboard, name='analytics-dashboard'),
    path('sales/', views.sales_chart, name='sales-chart'),
]
