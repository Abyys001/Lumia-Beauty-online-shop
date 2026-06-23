from rest_framework import generics

from apps.catalog.models import InstagramPost

from ..permissions import IsStaff
from ..serializers import AdminInstagramPostSerializer


class AdminInstagramListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsStaff]
    queryset = InstagramPost.objects.all().order_by('sort_order', '-id')
    serializer_class = AdminInstagramPostSerializer


class AdminInstagramDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsStaff]
    queryset = InstagramPost.objects.all()
    serializer_class = AdminInstagramPostSerializer
    lookup_field = 'id'
