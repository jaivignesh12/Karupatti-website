from decimal import Decimal
from django.conf import settings
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from orders.models import Order


def get_razorpay_client():
    if settings.RAZORPAY_KEY_ID and settings.RAZORPAY_KEY_SECRET and 'placeholder' not in settings.RAZORPAY_KEY_ID:
        try:
            import razorpay
            return razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
        except ImportError:
            return None
    return None


@api_view(['POST'])
def create_payment(request):
    """Create a Razorpay order for payment"""
    order_id = request.data.get('order_id')
    
    try:
        order = Order.objects.get(id=order_id)
    except Order.DoesNotExist:
        return Response({'error': 'Order not found'}, status=status.HTTP_404_NOT_FOUND)

    client = get_razorpay_client()
    
    if client:
        # Real Razorpay integration
        try:
            razorpay_order = client.order.create({
                'amount': int(order.total * 100),  # Amount in paise
                'currency': 'INR',
                'receipt': order.order_number,
                'notes': {
                    'order_id': str(order.id),
                }
            })
            order.razorpay_order_id = razorpay_order['id']
            order.save()

            return Response({
                'razorpay_order_id': razorpay_order['id'],
                'razorpay_key': settings.RAZORPAY_KEY_ID,
                'amount': int(order.total * 100),
                'currency': 'INR',
                'order_number': order.order_number,
            })
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    else:
        # Demo mode — simulate payment
        order.razorpay_order_id = f"demo_order_{order.order_number}"
        order.save()
        return Response({
            'demo_mode': True,
            'razorpay_order_id': order.razorpay_order_id,
            'amount': int(order.total * 100),
            'currency': 'INR',
            'order_number': order.order_number,
            'message': 'Running in demo mode. Payment will be auto-confirmed.'
        })


@api_view(['POST'])
def verify_payment(request):
    """Verify Razorpay payment signature or confirm COD"""
    order_id = request.data.get('order_id')
    razorpay_payment_id = request.data.get('razorpay_payment_id', '')
    razorpay_signature = request.data.get('razorpay_signature', '')
    demo_mode = request.data.get('demo_mode', False)
    is_cod = request.data.get('cod', False)

    try:
        order = Order.objects.get(id=order_id)
    except Order.DoesNotExist:
        return Response({'error': 'Order not found'}, status=status.HTTP_404_NOT_FOUND)

    if is_cod:
        order.payment_status = 'pending'
        order.status = 'confirmed'
        order.razorpay_order_id = 'COD'
        order.save()
        return Response({'status': 'COD Order confirmed', 'order_number': order.order_number})

    client = get_razorpay_client()

    if client and not demo_mode:
        # Real verification
        try:
            client.utility.verify_payment_signature({
                'razorpay_order_id': order.razorpay_order_id,
                'razorpay_payment_id': razorpay_payment_id,
                'razorpay_signature': razorpay_signature,
            })
            order.razorpay_payment_id = razorpay_payment_id
            order.razorpay_signature = razorpay_signature
            order.payment_status = 'paid'
            order.status = 'confirmed'
            order.save()
            return Response({'status': 'Payment verified', 'order_number': order.order_number})
        except Exception as e:
            order.payment_status = 'failed'
            order.save()
            return Response({'error': 'Payment verification failed'}, status=status.HTTP_400_BAD_REQUEST)
    else:
        # Demo mode — auto confirm
        order.payment_status = 'paid'
        order.status = 'confirmed'
        order.razorpay_payment_id = f"demo_pay_{order.order_number}"
        order.save()
        return Response({'status': 'Payment confirmed (demo)', 'order_number': order.order_number})
