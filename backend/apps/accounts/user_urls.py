from django.urls import path

from apps.orders.views import UserOrderListView

from .views import ChangePasswordView, ProfileView, TrustedDeviceDetailView, TrustedDeviceListView
from .views_addresses import AddressDetailView, AddressListCreateView
from .views_wishlist import WishlistDetailView, WishlistIdsView, WishlistListCreateView

urlpatterns = [
    path('profile/', ProfileView.as_view(), name='user-profile'),
    path('password/', ChangePasswordView.as_view(), name='user-password'),
    path('devices/', TrustedDeviceListView.as_view(), name='user-devices'),
    path('devices/<uuid:pk>/', TrustedDeviceDetailView.as_view(), name='user-device-detail'),
    path('addresses/', AddressListCreateView.as_view(), name='user-addresses'),
    path('addresses/<uuid:pk>/', AddressDetailView.as_view(), name='user-address-detail'),
    path('orders/', UserOrderListView.as_view(), name='user-orders'),
    path('wishlist/', WishlistListCreateView.as_view(), name='user-wishlist'),
    path('wishlist/ids/', WishlistIdsView.as_view(), name='user-wishlist-ids'),
    path('wishlist/<uuid:product_id>/', WishlistDetailView.as_view(), name='user-wishlist-detail'),
]
