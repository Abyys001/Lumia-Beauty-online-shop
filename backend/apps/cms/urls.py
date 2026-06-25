from django.urls import path

from .views import HomeCMSView, InstagramPageListView

urlpatterns = [
    path('home/', HomeCMSView.as_view(), name='cms-home'),
    path('instagram-pages/', InstagramPageListView.as_view(), name='cms-instagram-pages'),
]
