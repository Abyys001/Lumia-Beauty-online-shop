from rest_framework import filters, generics

from apps.accounts.models import User

from ..permissions import IsStaff
from ..serializers import AdminUserListSerializer, AdminUserSerializer


class AdminUserListView(generics.ListAPIView):
    permission_classes = [IsStaff]
    serializer_class = AdminUserListSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['phone', 'first_name', 'last_name', 'email']
    ordering_fields = ['date_joined', 'phone']
    ordering = ['-date_joined']

    def get_queryset(self):
        return User.objects.prefetch_related('addresses').order_by('-date_joined')


class AdminUserDetailView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsStaff]
    serializer_class = AdminUserSerializer
    lookup_field = 'id'

    def get_queryset(self):
        return User.objects.prefetch_related('addresses')
