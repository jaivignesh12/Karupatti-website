from datetime import timedelta
from django.utils import timezone
from django.db.models import Sum, Count, F, Q
from rest_framework.decorators import api_view
from rest_framework.response import Response
from orders.models import Order, OrderItem
from products.models import Product
from accounts.models import UserProfile


@api_view(['GET'])
def dashboard(request):
    """Admin dashboard KPIs"""
    total_revenue = Order.objects.filter(payment_status='paid').aggregate(total=Sum('total'))['total'] or 0
    total_orders = Order.objects.count()
    pending_orders = Order.objects.filter(status='pending').count()
    total_products = Product.objects.filter(is_active=True).count()
    total_users = UserProfile.objects.count()
    low_stock = Product.objects.filter(stock__lte=10, is_active=True).count()
    
    # Recent orders
    recent_orders = Order.objects.order_by('-created_at')[:5].values(
        'id', 'order_number', 'total', 'status', 'payment_status', 'created_at'
    )
    
    # Low stock products
    low_stock_products = Product.objects.filter(stock__lte=10, is_active=True).values(
        'id', 'name', 'stock', 'price'
    )[:10]

    return Response({
        'total_revenue': float(total_revenue),
        'total_orders': total_orders,
        'pending_orders': pending_orders,
        'total_products': total_products,
        'total_users': total_users,
        'low_stock_count': low_stock,
        'recent_orders': list(recent_orders),
        'low_stock_products': list(low_stock_products),
    })


@api_view(['GET'])
def sales_chart(request):
    """Sales data for charting"""
    days = int(request.query_params.get('days', 30))
    start_date = timezone.now() - timedelta(days=days)
    
    orders = Order.objects.filter(
        created_at__gte=start_date,
        payment_status='paid'
    ).order_by('created_at')

    # Group by date
    daily_data = {}
    for order in orders:
        date_str = order.created_at.strftime('%Y-%m-%d')
        if date_str not in daily_data:
            daily_data[date_str] = {'revenue': 0, 'orders': 0}
        daily_data[date_str]['revenue'] += float(order.total)
        daily_data[date_str]['orders'] += 1

    # Top products
    top_products = OrderItem.objects.filter(
        order__payment_status='paid',
        order__created_at__gte=start_date
    ).values('product_name').annotate(
        total_sold=Sum('quantity'),
        total_revenue=Sum(F('unit_price') * F('quantity'))
    ).order_by('-total_sold')[:5]

    # Order status breakdown
    status_breakdown = Order.objects.values('status').annotate(count=Count('id'))

    return Response({
        'daily_data': daily_data,
        'top_products': list(top_products),
        'status_breakdown': list(status_breakdown),
    })
