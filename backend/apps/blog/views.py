from rest_framework import generics, permissions

from .models import Post
from .serializers import PostDetailSerializer, PostListSerializer


class PostListView(generics.ListAPIView):
    serializer_class = PostListSerializer
    pagination_class = None
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        return Post.objects.filter(is_published=True).select_related('category').order_by('-is_featured', '-published_at')


class PostDetailView(generics.RetrieveAPIView):
    serializer_class = PostDetailSerializer
    lookup_field = 'slug'
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        return Post.objects.filter(is_published=True).select_related('category', 'author').prefetch_related('tags')
