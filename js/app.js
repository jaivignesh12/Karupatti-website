/**
 * Karupatti Kadai — Core Application State Manager
 * Handles: Auth, Cart, Wishlist, API calls, Toast notifications
 * Drop-in integration with existing static HTML pages
 */

const KK = (() => {
  const API = '/api';
  let _user = null;
  let _cart = { items: [], total: 0, item_count: 0 };
  let _wishlist = [];
  const _listeners = {};

  // ==================== HELPERS ====================

  function getCookie(name) {
    const v = document.cookie.match('(^|;) ?' + name + '=([^;]*)(;|$)');
    return v ? v[2] : null;
  }

  async function api(endpoint, options = {}) {
    const defaults = {
      headers: { 'Content-Type': 'application/json', 'X-CSRFToken': getCookie('csrftoken') || '' },
      credentials: 'include',
    };
    const config = { ...defaults, ...options };
    if (options.body && typeof options.body === 'object') {
      config.body = JSON.stringify(options.body);
    }
    try {
      const res = await fetch(`${API}${endpoint}`, config);
      if (res.status === 204) return null;
      const data = await res.json();
      if (!res.ok) throw new Error(data.error || data.detail || 'Request failed');
      return data;
    } catch (err) {
      console.error(`API Error [${endpoint}]:`, err);
      throw err;
    }
  }

  function emit(event, data) {
    (_listeners[event] || []).forEach(fn => fn(data));
  }

  function on(event, fn) {
    if (!_listeners[event]) _listeners[event] = [];
    _listeners[event].push(fn);
  }

  // ==================== TOAST NOTIFICATIONS ====================

  function createToastContainer() {
    if (document.getElementById('kk-toast-container')) return;
    const c = document.createElement('div');
    c.id = 'kk-toast-container';
    c.style.cssText = 'position:fixed;top:80px;right:20px;z-index:99999;display:flex;flex-direction:column;gap:8px;pointer-events:none;';
    document.body.appendChild(c);
  }

  function toast(message, type = 'success', duration = 3000) {
    createToastContainer();
    const container = document.getElementById('kk-toast-container');
    const t = document.createElement('div');
    const colors = {
      success: 'background:rgba(131,152,87,0.95);color:#fff;',
      error: 'background:rgba(147,0,10,0.95);color:#ffdad6;',
      info: 'background:rgba(37,31,23,0.95);color:#eee0d3;border:1px solid rgba(255,185,82,0.3);',
    };
    t.style.cssText = `${colors[type] || colors.info}padding:12px 20px;border-radius:12px;font-family:"Be Vietnam Pro",sans-serif;font-size:14px;backdrop-filter:blur(20px);box-shadow:0 8px 32px rgba(0,0,0,0.3);transform:translateX(120%);transition:transform 0.3s ease;pointer-events:auto;max-width:320px;`;
    t.textContent = message;
    container.appendChild(t);
    requestAnimationFrame(() => { t.style.transform = 'translateX(0)'; });
    setTimeout(() => {
      t.style.transform = 'translateX(120%)';
      setTimeout(() => t.remove(), 300);
    }, duration);
  }

  // ==================== AUTH ====================

  async function checkAuth() {
    try {
      const data = await api('/accounts/me/');
      _user = data.user;
      emit('auth', _user);
      if (_user) {
        loadWishlist();
      }
      updateNavAuth();
    } catch (e) {
      _user = null;
    }
    return _user;
  }

  async function login(email, password) {
    const data = await api('/accounts/login/', { method: 'POST', body: { email, password } });
    _user = data.user;
    emit('auth', _user);
    updateNavAuth();
    toast('Welcome back!', 'success');
    loadCart();
    loadWishlist();
    return data;
  }

  async function signup(email, password, full_name, phone) {
    const data = await api('/accounts/signup/', { method: 'POST', body: { email, password, full_name, phone: phone || '' } });
    _user = data.user;
    emit('auth', _user);
    updateNavAuth();
    toast('Account created!', 'success');
    return data;
  }

  async function adminLogin(email, password) {
    const data = await api('/accounts/admin-login/', { method: 'POST', body: { email, password } });
    _user = data.user;
    emit('auth', _user);
    toast('Admin access granted', 'success');
    return data;
  }

  async function logout() {
    await api('/accounts/logout/', { method: 'POST' });
    _user = null;
    _wishlist = [];
    emit('auth', null);
    updateNavAuth();
    toast('Logged out', 'info');
  }

  function getUser() { return _user; }
  function isLoggedIn() { return !!_user; }
  function isAdmin() { return _user && _user.is_admin; }

  // ==================== CART ====================

  async function loadCart() {
    try {
      _cart = await api('/cart/');
      emit('cart', _cart);
      updateCartBadges();
    } catch (e) {
      _cart = { items: [], total: 0, item_count: 0 };
    }
    return _cart;
  }

  async function addToCart(productId, quantity = 1) {
    try {
      _cart = await api('/cart/add/', { method: 'POST', body: { product_id: productId, quantity } });
      emit('cart', _cart);
      updateCartBadges();
      toast('Added to cart!', 'success');
      return _cart;
    } catch (e) {
      toast(e.message || 'Failed to add to cart', 'error');
      throw e;
    }
  }

  async function updateCartItem(itemId, quantity) {
    _cart = await api(`/cart/items/${itemId}/`, { method: 'PATCH', body: { quantity } });
    emit('cart', _cart);
    updateCartBadges();
    return _cart;
  }

  async function removeCartItem(itemId) {
    _cart = await api(`/cart/items/${itemId}/remove/`, { method: 'DELETE' });
    emit('cart', _cart);
    updateCartBadges();
    toast('Item removed', 'info');
    return _cart;
  }

  async function clearCart() {
    _cart = await api('/cart/clear/', { method: 'POST' });
    emit('cart', _cart);
    updateCartBadges();
    return _cart;
  }

  function getCart() { return _cart; }

  function updateCartBadges() {
    document.querySelectorAll('[data-cart-count]').forEach(el => {
      el.textContent = _cart.item_count || 0;
      el.style.display = _cart.item_count > 0 ? 'flex' : 'none';
    });
  }

  // ==================== WISHLIST ====================

  async function loadWishlist() {
    if (!_user) return [];
    try {
      _wishlist = await api('/accounts/wishlist/');
      emit('wishlist', _wishlist);
    } catch (e) { _wishlist = []; }
    return _wishlist;
  }

  async function toggleWishlist(productId) {
    if (!_user) {
      toast('Please login to add to wishlist', 'info');
      window.location.href = '/auth';
      return;
    }
    try {
      const data = await api('/accounts/wishlist/toggle/', { method: 'POST', body: { product_id: productId } });
      await loadWishlist();
      toast(data.in_wishlist ? 'Added to wishlist' : 'Removed from wishlist', 'success');
      return data;
    } catch (e) {
      toast('Failed to update wishlist', 'error');
    }
  }

  function isInWishlist(productId) {
    return _wishlist.some(w => w.product && w.product.id === productId);
  }

  function getWishlist() { return _wishlist; }

  // ==================== PRODUCTS ====================

  async function getProducts(params = {}) {
    const query = new URLSearchParams(params).toString();
    return api(`/products/${query ? '?' + query : ''}`);
  }

  async function getProduct(slug) {
    return api(`/products/${slug}/`);
  }

  async function getCategories() {
    return api('/categories/');
  }

  async function getFeaturedProducts() {
    return api('/products/featured/');
  }

  // ==================== ORDERS ====================

  async function createOrder(shippingData) {
    return api('/orders/create/', { method: 'POST', body: shippingData });
  }

  async function getOrders() {
    return api('/orders/');
  }

  async function getOrder(orderId) {
    return api(`/orders/${orderId}/`);
  }

  // ==================== PAYMENTS ====================

  async function initiatePayment(orderId) {
    return api('/payments/create/', { method: 'POST', body: { order_id: orderId } });
  }

  async function verifyPayment(data) {
    return api('/payments/verify/', { method: 'POST', body: data });
  }

  // ==================== PROFILE ====================

  async function getProfile() {
    return api('/accounts/profile/');
  }

  async function updateProfile(data) {
    return api('/accounts/profile/', { method: 'PATCH', body: data });
  }

  async function getAddresses() {
    return api('/accounts/addresses/');
  }

  async function addAddress(data) {
    return api('/accounts/addresses/', { method: 'POST', body: data });
  }

  async function deleteAddress(id) {
    return api(`/accounts/addresses/${id}/`, { method: 'DELETE' });
  }

  // ==================== ADMIN ====================

  const admin = {
    async getDashboard() { return api('/analytics/dashboard/'); },
    async getSalesChart(days = 30) { return api(`/analytics/sales/?days=${days}`); },
    async getProducts(search = '') { return api(`/admin/products/${search ? '?search=' + search : ''}`); },
    async createProduct(data) { return api('/admin/products/', { method: 'POST', body: data }); },
    async updateProduct(id, data) { return api(`/admin/products/${id}/`, { method: 'PATCH', body: data }); },
    async deleteProduct(id) { return api(`/admin/products/${id}/`, { method: 'DELETE' }); },
    async toggleProduct(id) { return api(`/admin/products/${id}/toggle_active/`, { method: 'POST' }); },
    async updateStock(id, stock) { return api(`/admin/products/${id}/update_stock/`, { method: 'POST', body: { stock } }); },
    async getOrders(params = {}) { 
      const q = new URLSearchParams(params).toString();
      return api(`/orders/admin/${q ? '?' + q : ''}`); 
    },
    async updateOrderStatus(id, status) { return api(`/orders/admin/${id}/status/`, { method: 'PATCH', body: { status } }); },
    async getUsers(search = '') { return api(`/accounts/admin/users/${search ? '?search=' + search : ''}`); },
  };

  // ==================== NAV UPDATES ====================

  function updateNavAuth() {
    // Update all account circle buttons/links across pages
    document.querySelectorAll('[data-auth-trigger]').forEach(el => {
      if (_user) {
        el.setAttribute('href', '/profile');
        el.title = _user.full_name || _user.email;
      } else {
        el.setAttribute('href', '/auth');
        el.title = 'Login';
      }
    });

    // Show/hide admin links
    document.querySelectorAll('[data-admin-only]').forEach(el => {
      el.style.display = isAdmin() ? '' : 'none';
    });
  }

  // ==================== INIT ====================

  async function init() {
    await Promise.allSettled([checkAuth(), loadCart()]);
  }

  // Auto-init on DOM ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }

  // Public API
  return {
    api, toast, on, emit,
    // Auth
    login, signup, adminLogin, logout, checkAuth, getUser, isLoggedIn, isAdmin,
    // Cart
    loadCart, addToCart, updateCartItem, removeCartItem, clearCart, getCart,
    // Wishlist
    loadWishlist, toggleWishlist, isInWishlist, getWishlist,
    // Products
    getProducts, getProduct, getCategories, getFeaturedProducts,
    // Orders
    createOrder, getOrders, getOrder,
    // Payments
    initiatePayment, verifyPayment,
    // Profile
    getProfile, updateProfile, getAddresses, addAddress, deleteAddress,
    // Admin
    admin,
    // Utils
    updateCartBadges, updateNavAuth,
  };
})();
