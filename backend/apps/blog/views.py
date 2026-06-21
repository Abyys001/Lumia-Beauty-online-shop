from rest_framework import generics

from .models import Post
from .serializers import PostDetailSerializer, PostListSerializer


class PostListView(generics.ListAPIView):
    serializer_class = PostListSerializer
    pagination_class = None

    def get_queryset(self):
        return Post.objects.filter(is_published=True).select_related('category')


class PostDetailView(generics.RetrieveAPIView):
    serializer_class = PostDetailSerializer
    lookup_field = 'slug'

    def get_queryset(self):
        return Post.objects.filter(is_published=True).select_related('category', 'author').prefetch_related('tags')
