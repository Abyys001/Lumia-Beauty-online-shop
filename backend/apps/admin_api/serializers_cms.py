from rest_framework import serializers

from apps.catalog.media_utils import relative_media_url
from apps.cms.models import HomeHero, InstagramPage, TrustBadge


class AdminHomeHeroSerializer(serializers.ModelSerializer):
    video_webm_url = serializers.SerializerMethodField()
    video_poster_url = serializers.SerializerMethodField()
    fallback_image_url = serializers.SerializerMethodField()

    class Meta:
        model = HomeHero
        fields = [
            'id', 'headline', 'subheadline', 'description',
            'cta_text', 'cta_url', 'cta_secondary_text', 'cta_secondary_url',
            'badge_text', 'is_active',
            'video_webm', 'video_poster', 'fallback_image',
            'video_webm_url', 'video_poster_url', 'fallback_image_url',
            'updated_at',
        ]
        read_only_fields = ['id', 'updated_at']

    def _rel(self, obj, field):
        return relative_media_url(getattr(obj, field, None))

    def get_video_webm_url(self, obj):
        return self._rel(obj, 'video_webm')

    def get_video_poster_url(self, obj):
        return self._rel(obj, 'video_poster')

    def get_fallback_image_url(self, obj):
        return self._rel(obj, 'fallback_image')


class AdminTrustBadgeSerializer(serializers.ModelSerializer):
    class Meta:
        model = TrustBadge
        fields = ['id', 'icon', 'title', 'description', 'sort_order', 'is_active']
        read_only_fields = ['id']


class AdminInstagramPageSerializer(serializers.ModelSerializer):
    profile_url = serializers.SerializerMethodField()

    class Meta:
        model = InstagramPage
        fields = ['id', 'username', 'label', 'sort_order', 'is_active', 'profile_url']
        read_only_fields = ['id', 'profile_url']

    def get_profile_url(self, obj):
        return obj.profile_url

    def validate_username(self, value):
        cleaned = (value or '').strip().lstrip('@')
        if not cleaned:
            raise serializers.ValidationError('آیدی اینستاگرام الزامی است.')
        return cleaned
