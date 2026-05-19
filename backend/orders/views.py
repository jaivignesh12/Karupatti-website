from decimal import Decimal
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Order, OrderItem
from .serializers import OrderSerializer, OrderCreateSerializer
from cart.views import get_or_create_cart


@api_view(['GET'])
def list_orders(request):
    user_id = getattr(request, 'user_id', None)
    if not user_id:
        return Response({'error': 'Authentication required'}, status=status.HTTP_401_UNAUTHORIZED)
    orders = Order.objects.filter(user_id=user_id).prefetch_related('items')
    serializer = OrderSerializer(orders, many=True)
    return Response(serializer.data)


@api_view(['GET'])
def order_detail(request, order_id):
    try:
        order = Order.objects.prefetch_related('items').get(id=order_id)
    except Order.DoesNotExist:
        return Response({'error': 'Order not found'}, status=status.HTTP_404_NOT_FOUND)
    serializer = OrderSerializer(order)
    return Response(serializer.data)


@api_view(['POST'])
def create_order(request):
    cart = get_or_create_cart(request)
    cart_items = cart.items.select_related('product').all()

    if not cart_items.exists():
        return Response({'error': 'Cart is empty'}, status=status.HTTP_400_BAD_REQUEST)

    serializer = OrderCreateSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    data = serializer.validated_data

    # Calculate totals
    subtotal = sum(item.product.price * item.quantity for item in cart_items)
    shipping = Decimal('0.00') if subtotal >= 500 else Decimal('50.00')
    tax = (subtotal * Decimal('0.05')).quantize(Decimal('0.01'))
    total = subtotal + shipping + tax

    user_id = getattr(request, 'user_id', None)

    order = Order.objects.create(
        user_id=user_id,
        user_email=data.get('user_email', ''),
        subtotal=subtotal,
        shipping_cost=shipping,
        tax=tax,
        total=total,
        shipping_name=data['shipping_name'],
        shipping_address=data['shipping_address'],
        shipping_city=data['shipping_city'],
        shipping_postal_code=data['shipping_postal_code'],
        shipping_phone=data.get('shipping_phone', ''),
    )

    # Create order items and reduce stock
    for item in cart_items:
        OrderItem.objects.create(
            order=order,
            product=item.product,
            product_name=item.product.name,
            product_image=item.product.image_url,
            quantity=item.quantity,
            unit_price=item.product.price,
        )
        item.product.stock -= item.quantity
        item.product.save()

    # Clear cart
    cart.items.all().delete()

    result = OrderSerializer(order)
    return Response(result.data, status=status.HTTP_201_CREATED)


# ---- Admin endpoints ----

@api_view(['GET'])
def admin_list_orders(request):
    """List all orders for admin"""
    orders = Order.objects.all().prefetch_related('items')
    
    status_filter = request.query_params.get('status')
    if status_filter:
        orders = orders.filter(status=status_filter)
    
    search = request.query_params.get('search')
    if search:
        orders = orders.filter(order_number__icontains=search)
    
    serializer = OrderSerializer(orders, many=True)
    return Response(serializer.data)


@api_view(['PATCH'])
def update_order_status(request, order_id):
    """Admin: update order status"""
    try:
        order = Order.objects.get(id=order_id)
    except Order.DoesNotExist:
        return Response({'error': 'Order not found'}, status=status.HTTP_404_NOT_FOUND)
    
    new_status = request.data.get('status')
    valid_statuses = [s[0] for s in Order.STATUS_CHOICES]
    if new_status not in valid_statuses:
        return Response({'error': f'Invalid status. Must be one of: {valid_statuses}'}, status=status.HTTP_400_BAD_REQUEST)
    
    order.status = new_status
    order.save()
    serializer = OrderSerializer(order)
    return Response(serializer.data)
