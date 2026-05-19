from rest_framework import serializers
from .models import UserProfile, Address, Wishlist
from products.serializers import ProductSerializer


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['id', 'user_id', 'email', 'full_name', 'phone', 'is_admin', 'created_at']
        read_only_fields = ['user_id', 'is_admin']


class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = ['id', 'label', 'full_name', 'phone', 'address_line', 'city', 'postal_code', 'is_default']


class WishlistSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    product_id = serializers.UUIDField(write_only=True)

    class Meta:
        model = Wishlist
        fields = ['id', 'product', 'product_id', 'created_at']


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()


class SignupSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(min_length=6)
    full_name = serializers.CharField(max_length=200)
    phone = serializers.CharField(max_length=20, required=False, default='')
