from rest_framework import viewsets, permissions, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.core.cache import cache
from .models import Category, Product, ProductImage
from .serializers import CategorySerializer, ProductSerializer, ProductAdminSerializer


class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    lookup_field = 'slug'


class ProductViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = ProductSerializer
    lookup_field = 'slug'

    def get_queryset(self):
        qs = Product.objects.filter(is_active=True).select_related('category').prefetch_related('images')
        
        # Filter by category
        category = self.request.query_params.get('category')
        if category:
            qs = qs.filter(category__slug=category)
        
        # Filter by featured
        featured = self.request.query_params.get('featured')
        if featured == 'true':
            qs = qs.filter(is_featured=True)
        
        # Search
        search = self.request.query_params.get('search')
        if search:
            qs = qs.filter(name__icontains=search)
        
        # Sort
        sort = self.request.query_params.get('sort', '-created_at')
        valid_sorts = ['price', '-price', 'name', '-name', '-created_at', 'created_at']
        if sort in valid_sorts:
            qs = qs.order_by(sort)
        
        return qs

    def list(self, request, *args, **kwargs):
        # High-performance caching based on query parameters
        category = request.query_params.get('category', '')
        featured = request.query_params.get('featured', '')
        search = request.query_params.get('search', '')
        sort = request.query_params.get('sort', '-created_at')
        page = request.query_params.get('page', '1')
        
        cache_key = f"products_list_{category}_{featured}_{search}_{sort}_{page}"
        cached_data = cache.get(cache_key)
        if cached_data is not None:
            return Response(cached_data)

        response = super().list(request, *args, **kwargs)
        # Cache product lists for 60 seconds (1 minute) to ensure fast repeat loads
        cache.set(cache_key, response.data, timeout=60)
        return response

    def retrieve(self, request, *args, **kwargs):
        # Cache single product detail checks
        slug = kwargs.get('slug', '')
        cache_key = f"product_detail_{slug}"
        cached_data = cache.get(cache_key)
        if cached_data is not None:
            return Response(cached_data)

        response = super().retrieve(request, *args, **kwargs)
        cache.set(cache_key, response.data, timeout=60)
        return response

    @action(detail=False, methods=['get'])
    def featured(self, request):
        cache_key = "products_featured"
        cached_data = cache.get(cache_key)
        if cached_data is not None:
            return Response(cached_data)

        featured = Product.objects.filter(is_active=True, is_featured=True)[:6]
        serializer = self.get_serializer(featured, many=True)
        data = serializer.data
        cache.set(cache_key, data, timeout=60)
        return Response(data)


class ProductAdminViewSet(viewsets.ModelViewSet):
    """Admin-only product management"""
    queryset = Product.objects.all().select_related('category').prefetch_related('images')
    serializer_class = ProductAdminSerializer

    def perform_create(self, serializer):
        serializer.save()
        cache.clear() # Invalidate cache on new product

    def perform_update(self, serializer):
        serializer.save()
        cache.clear() # Invalidate cache on product modification

    def perform_destroy(self, instance):
        instance.delete()
        cache.clear() # Invalidate cache on product deletion

    def get_queryset(self):
        qs = super().get_queryset()
        search = self.request.query_params.get('search')
        if search:
            qs = qs.filter(name__icontains=search)
        return qs

    @action(detail=True, methods=['post'])
    def toggle_active(self, request, pk=None):
        product = self.get_object()
        product.is_active = not product.is_active
        product.save()
        cache.clear() # Invalidate products cache
        return Response({'is_active': product.is_active})

    @action(detail=True, methods=['post'])
    def update_stock(self, request, pk=None):
        product = self.get_object()
        stock = request.data.get('stock')
        if stock is not None:
            product.stock = int(stock)
            product.save()
            cache.clear() # Invalidate products cache
        return Response({'stock': product.stock})
