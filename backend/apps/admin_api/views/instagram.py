from rest_framework import generics

from apps.cms.models import InstagramPage

from ..permissions import IsStaff
from ..serializers_cms import AdminInstagramPageSerializer


class AdminInstagramListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsStaff]
    queryset = InstagramPage.objects.all().order_by('sort_order', 'username')
    serializer_class = AdminInstagramPageSerializer


class AdminInstagramDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsStaff]
    queryset = InstagramPage.objects.all()
    serializer_class = AdminInstagramPageSerializer
    lookup_field = 'id'
