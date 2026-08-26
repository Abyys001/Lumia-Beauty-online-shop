from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from .serializers import EpochTokenRefreshSerializer
from .views import DeviceLoginView, LoginView, LogoutView, RegisterView, RememberDevicePolicyView

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('device/login/', DeviceLoginView.as_view(), name='device-login'),
    path('device/policy/', RememberDevicePolicyView.as_view(), name='device-policy'),
    path(
        'token/refresh/',
        TokenRefreshView.as_view(serializer_class=EpochTokenRefreshSerializer),
        name='token-refresh',
    ),
]
