import hashlib
import uuid
import logging
import os
import time
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.conf import settings
from .models import UserProfile, Address, Wishlist
from .serializers import (
    UserProfileSerializer, AddressSerializer, WishlistSerializer,
    LoginSerializer, SignupSerializer
)
from products.models import Product

# ==================== OWASP A09: SECURITY LOGGING & MONITORING ====================
logger = logging.getLogger('security')
logger.setLevel(logging.INFO)
logger.propagate = False

log_file_path = os.path.join(settings.BASE_DIR, 'security.log')
file_handler = logging.FileHandler(log_file_path)
formatter = logging.Formatter('%(asctime)s - [OWASP A09 Audit Log] - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
if not logger.handlers:
    logger.addHandler(file_handler)

# ==================== OWASP A07: BRUTE FORCE PROTECTION (RATE LIMITING) ====================
LOGIN_ATTEMPTS = {}

def check_login_rate_limit(email):
    now = time.time()
    attempts = LOGIN_ATTEMPTS.get(email, [])
    # Keep attempts in the last 60 seconds
    attempts = [t for t in attempts if now - t < 60]
    LOGIN_ATTEMPTS[email] = attempts
    if len(attempts) >= 5:
        return False
    return True

def record_login_attempt(email, success):
    if success:
        if email in LOGIN_ATTEMPTS:
            del LOGIN_ATTEMPTS[email]
    else:
        now = time.time()
        if email not in LOGIN_ATTEMPTS:
            LOGIN_ATTEMPTS[email] = []
        LOGIN_ATTEMPTS[email].append(now)

# ==================== OWASP A02: CRYPTOGRAPHIC PASSWORD HASHING ====================
def check_user_password(password, hashed_password):
    if not hashed_password:
        return False
    # Backward compatible check for old sha256 hash (64 character hex string)
    if len(hashed_password) == 64 and all(c in '0123456789abcdefABCDEF' for c in hashed_password):
        legacy_hash = hashlib.sha256(password.encode()).hexdigest()
        return legacy_hash == hashed_password
    # Standard cryptographically secure PBKDF2 check
    from django.contrib.auth.hashers import check_password
    return check_password(password, hashed_password)


# ---- Auth ----

@api_view(['POST'])
def signup(request):
    serializer = SignupSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    data = serializer.validated_data
    email = data['email']

    if UserProfile.objects.filter(email=email).exists():
        logger.warning(f"Signup failed: Email {email} already registered from IP {request.META.get('REMOTE_ADDR')}")
        return Response({'error': 'Email already registered'}, status=status.HTTP_400_BAD_REQUEST)

    user_id = str(uuid.uuid4())
    profile = UserProfile.objects.create(
        user_id=user_id,
        email=email,
        full_name=data['full_name'],
        phone=data.get('phone', ''),
    )
    # Secure password hashing (PBKDF2 with SHA-256 salt)
    from django.contrib.auth.hashers import make_password
    profile.password_hash = make_password(data['password'])
    profile.save()

    logger.info(f"Successful signup: User {email} registered from IP {request.META.get('REMOTE_ADDR')}")

    # Set session
    request.session['user_id'] = user_id
    request.session['is_admin'] = False
    request.session.save()

    return Response({
        'user': UserProfileSerializer(profile).data,
        'message': 'Account created successfully'
    }, status=status.HTTP_201_CREATED)


@api_view(['POST'])
def login(request):
    serializer = LoginSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    data = serializer.validated_data
    email = data['email']

    # Rate limiting check
    if not check_login_rate_limit(email):
        logger.warning(f"Rate limit breached: Login blocked for {email} from IP {request.META.get('REMOTE_ADDR')}")
        return Response({'error': 'Too many failed login attempts. Please try again after 60 seconds.'}, status=status.HTTP_429_TOO_MANY_REQUESTS)

    try:
        profile = UserProfile.objects.get(email__iexact=email)
    except UserProfile.DoesNotExist:
        record_login_attempt(email, False)
        logger.warning(f"Failed login attempt: Email {email} not found from IP {request.META.get('REMOTE_ADDR')}")
        return Response({'error': 'Invalid email or password'}, status=status.HTTP_401_UNAUTHORIZED)
        
    if not check_user_password(data['password'], profile.password_hash):
        record_login_attempt(email, False)
        logger.warning(f"Failed login attempt: Incorrect password for user {email} from IP {request.META.get('REMOTE_ADDR')}")
        return Response({'error': 'Invalid email or password'}, status=status.HTTP_401_UNAUTHORIZED)

    # Success
    record_login_attempt(email, True)
    logger.info(f"Successful login: User {email} authenticated from IP {request.META.get('REMOTE_ADDR')}")

    # Set session
    request.session['user_id'] = profile.user_id
    request.session['is_admin'] = profile.is_admin
    request.session.save()

    return Response({
        'user': UserProfileSerializer(profile).data,
        'message': 'Login successful'
    })


@api_view(['POST'])
def admin_login(request):
    serializer = LoginSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    data = serializer.validated_data
    email = data['email']

    # Rate limiting check
    if not check_login_rate_limit(email):
        logger.warning(f"Rate limit breached: Admin login blocked for {email} from IP {request.META.get('REMOTE_ADDR')}")
        return Response({'error': 'Too many failed login attempts. Please try again after 60 seconds.'}, status=status.HTTP_429_TOO_MANY_REQUESTS)

    try:
        profile = UserProfile.objects.get(email__iexact=email, is_admin=True)
    except UserProfile.DoesNotExist:
        record_login_attempt(email, False)
        logger.warning(f"Failed admin login attempt: Admin email {email} not found or not authorized from IP {request.META.get('REMOTE_ADDR')}")
        return Response({'error': 'Invalid admin credentials'}, status=status.HTTP_401_UNAUTHORIZED)

    if not check_user_password(data['password'], profile.password_hash):
        record_login_attempt(email, False)
        logger.warning(f"Failed admin login attempt: Incorrect password for admin {email} from IP {request.META.get('REMOTE_ADDR')}")
        return Response({'error': 'Invalid admin credentials'}, status=status.HTTP_401_UNAUTHORIZED)

    # Success
    record_login_attempt(email, True)
    logger.info(f"Successful admin login: Admin {email} authenticated from IP {request.META.get('REMOTE_ADDR')}")

    request.session['user_id'] = profile.user_id
    request.session['is_admin'] = True
    request.session.save()

    return Response({
        'user': UserProfileSerializer(profile).data,
        'message': 'Admin login successful'
    })


@api_view(['POST'])
def logout(request):
    request.session.flush()
    return Response({'message': 'Logged out'})


@api_view(['GET'])
def me(request):
    user_id = getattr(request, 'user_id', None)
    if not user_id:
        return Response({'user': None})
    try:
        profile = UserProfile.objects.get(user_id=user_id)
        return Response({'user': UserProfileSerializer(profile).data})
    except UserProfile.DoesNotExist:
        return Response({'user': None})


# ---- Profile ----

@api_view(['GET', 'PATCH'])
def profile(request):
    user_id = getattr(request, 'user_id', None)
    if not user_id:
        return Response({'error': 'Auth required'}, status=status.HTTP_401_UNAUTHORIZED)
    
    try:
        prof = UserProfile.objects.get(user_id=user_id)
    except UserProfile.DoesNotExist:
        return Response({'error': 'Profile not found'}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'PATCH':
        serializer = UserProfileSerializer(prof, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
    
    return Response(UserProfileSerializer(prof).data)


# ---- Addresses ----

@api_view(['GET', 'POST'])
def addresses(request):
    user_id = getattr(request, 'user_id', None)
    if not user_id:
        return Response({'error': 'Auth required'}, status=status.HTTP_401_UNAUTHORIZED)

    if request.method == 'POST':
        serializer = AddressSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(user_id=user_id)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    addrs = Address.objects.filter(user_id=user_id)
    return Response(AddressSerializer(addrs, many=True).data)


@api_view(['PATCH', 'DELETE'])
def address_detail(request, address_id):
    user_id = getattr(request, 'user_id', None)
    if not user_id:
        return Response({'error': 'Auth required'}, status=status.HTTP_401_UNAUTHORIZED)

    try:
        addr = Address.objects.get(id=address_id, user_id=user_id)
    except Address.DoesNotExist:
        return Response({'error': 'Address not found'}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'DELETE':
        addr.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    serializer = AddressSerializer(addr, data=request.data, partial=True)
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response(serializer.data)


# ---- Wishlist ----

@api_view(['GET'])
def wishlist(request):
    user_id = getattr(request, 'user_id', None)
    if not user_id:
        return Response({'error': 'Auth required'}, status=status.HTTP_401_UNAUTHORIZED)
    items = Wishlist.objects.filter(user_id=user_id).select_related('product')
    return Response(WishlistSerializer(items, many=True).data)


@api_view(['POST'])
def add_to_wishlist(request):
    user_id = getattr(request, 'user_id', None)
    if not user_id:
        return Response({'error': 'Auth required'}, status=status.HTTP_401_UNAUTHORIZED)

    product_id = request.data.get('product_id')
    try:
        product = Product.objects.get(id=product_id)
    except Product.DoesNotExist:
        return Response({'error': 'Product not found'}, status=status.HTTP_404_NOT_FOUND)

    obj, created = Wishlist.objects.get_or_create(user_id=user_id, product=product)
    if not created:
        obj.delete()
        return Response({'message': 'Removed from wishlist', 'in_wishlist': False})
    return Response({'message': 'Added to wishlist', 'in_wishlist': True}, status=status.HTTP_201_CREATED)


@api_view(['DELETE'])
def remove_from_wishlist(request, item_id):
    user_id = getattr(request, 'user_id', None)
    if not user_id:
        return Response({'error': 'Auth required'}, status=status.HTTP_401_UNAUTHORIZED)
    try:
        Wishlist.objects.get(id=item_id, user_id=user_id).delete()
    except Wishlist.DoesNotExist:
        pass
    return Response(status=status.HTTP_204_NO_CONTENT)


# ---- Admin: Users ----

@api_view(['GET'])
def admin_list_users(request):
    users = UserProfile.objects.all().order_by('-created_at')
    search = request.query_params.get('search')
    if search:
        users = users.filter(email__icontains=search) | users.filter(full_name__icontains=search)
    return Response(UserProfileSerializer(users, many=True).data)
