from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, generics

from apps.blog.models import Post, PostCategory, Tag

from ..permissions import IsStaff
from ..serializers import AdminPostCategorySerializer, AdminPostSerializer, AdminTagSerializer


class AdminPostListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsStaff]
    serializer_class = AdminPostSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['is_published', 'category']
    search_fields = ['title', 'content']
    ordering_fields = ['created_at', 'published_at']
    ordering = ['-created_at']

    def get_queryset(self):
        return Post.objects.select_related('category', 'author').prefetch_related('tags')


class AdminPostDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsStaff]
    serializer_class = AdminPostSerializer
    lookup_field = 'id'

    def get_queryset(self):
        return Post.objects.select_related('category', 'author').prefetch_related('tags')


class AdminPostCategoryListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsStaff]
    queryset = PostCategory.objects.all().order_by('name')
    serializer_class = AdminPostCategorySerializer


class AdminTagListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsStaff]
    queryset = Tag.objects.all().order_by('name')
    serializer_class = AdminTagSerializer
