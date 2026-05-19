from rest_framework import serializers
from .models import Order, OrderItem


class OrderItemSerializer(serializers.ModelSerializer):
    subtotal = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'product_name', 'product_image', 'quantity', 'unit_price', 'subtotal']


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    payment_status_display = serializers.CharField(source='get_payment_status_display', read_only=True)

    class Meta:
        model = Order
        fields = [
            'id', 'order_number', 'user_id', 'user_email',
            'status', 'status_display', 'payment_status', 'payment_status_display',
            'razorpay_order_id', 'razorpay_payment_id',
            'subtotal', 'shipping_cost', 'tax', 'total',
            'shipping_name', 'shipping_address', 'shipping_city',
            'shipping_postal_code', 'shipping_phone',
            'items', 'created_at', 'updated_at'
        ]
        read_only_fields = ['order_number', 'razorpay_order_id', 'razorpay_payment_id']


class OrderCreateSerializer(serializers.Serializer):
    shipping_name = serializers.CharField(max_length=200)
    shipping_address = serializers.CharField()
    shipping_city = serializers.CharField(max_length=100)
    shipping_postal_code = serializers.CharField(max_length=20)
    shipping_phone = serializers.CharField(max_length=20, required=False, default='')
    user_email = serializers.EmailField(required=False, default='')
