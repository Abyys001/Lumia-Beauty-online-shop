from django.urls import path

from .views import HomeCMSView

urlpatterns = [
    path('home/', HomeCMSView.as_view(), name='cms-home'),
]
