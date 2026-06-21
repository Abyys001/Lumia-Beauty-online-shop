from django.urls import path

from .views import ZarinpalRequestView, ZarinpalVerifyView

urlpatterns = [
    path('zarinpal/request/', ZarinpalRequestView.as_view(), name='zarinpal-request'),
    path('zarinpal/verify/', ZarinpalVerifyView.as_view(), name='zarinpal-verify'),
]
