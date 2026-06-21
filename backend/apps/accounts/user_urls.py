from django.urls import path

from apps.orders.views import UserOrderListView

from .views import ProfileView
from .views_addresses import AddressDetailView, AddressListCreateView

urlpatterns = [
    path('profile/', ProfileView.as_view(), name='user-profile'),
    path('addresses/', AddressListCreateView.as_view(), name='user-addresses'),
    path('addresses/<uuid:pk>/', AddressDetailView.as_view(), name='user-address-detail'),
    path('orders/', UserOrderListView.as_view(), name='user-orders'),
]
