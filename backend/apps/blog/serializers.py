from rest_framework import serializers

from apps.catalog.serializers import RelativeURLField

from .models import Post, PostCategory, Tag


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['name', 'slug']


class PostCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = PostCategory
        fields = ['name', 'slug']


class PostListSerializer(serializers.ModelSerializer):
    category = PostCategorySerializer(read_only=True)
    cover_image = RelativeURLField(required=False, allow_null=True)

    class Meta:
        model = Post
        fields = [
            'id', 'title', 'slug', 'excerpt', 'content', 'cover_image',
            'category', 'published_at', 'is_featured', 'meta_title', 'meta_description',
        ]


class PostDetailSerializer(PostListSerializer):
    tags = TagSerializer(many=True, read_only=True)
    author_name = serializers.SerializerMethodField()

    class Meta(PostListSerializer.Meta):
        fields = PostListSerializer.Meta.fields + ['content', 'tags', 'author_name', 'updated_at']

    def get_author_name(self, obj):
        return obj.author.full_name if obj.author else 'Lumia Beauty'
