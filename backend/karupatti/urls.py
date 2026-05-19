from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.views.generic import TemplateView
from django.shortcuts import redirect


def checkout_view(request):
    """Checkout requires login — instant server-side redirect if not authenticated."""
    if not request.session.get('user_id'):
        return redirect('/auth?redirect=/checkout')
    return TemplateView.as_view(template_name='checkout.html')(request)


def profile_view(request):
    """Profile requires login — instant server-side redirect if not authenticated."""
    if not request.session.get('user_id'):
        return redirect('/auth?redirect=/profile')
    return TemplateView.as_view(template_name='profile.html')(request)


urlpatterns = [
    path('django-admin/', admin.site.urls),
    
    # API endpoints
    path('api/', include('products.urls')),
    path('api/cart/', include('cart.urls')),
    path('api/orders/', include('orders.urls')),
    path('api/accounts/', include('accounts.urls')),
    path('api/payments/', include('payments.urls')),
    path('api/analytics/', include('analytics.urls')),
    
    # Serve frontend HTML pages via Django
    path('', TemplateView.as_view(template_name='index.html'), name='home'),
    path('collection', TemplateView.as_view(template_name='collection.html'), name='collection'),
    path('product', TemplateView.as_view(template_name='product.html'), name='product'),
    path('checkout', checkout_view, name='checkout'),
    path('auth', TemplateView.as_view(template_name='auth.html'), name='auth'),
    path('profile', profile_view, name='profile'),
    path('admin-panel', TemplateView.as_view(template_name='admin.html'), name='admin-panel'),
]

# Also serve static HTML files directly
from django.conf.urls.static import static
if settings.DEBUG:
    urlpatterns += static('/js/', document_root=settings.FRONTEND_DIR / 'js')
    urlpatterns += static('/video/', document_root=settings.FRONTEND_DIR / 'video')
