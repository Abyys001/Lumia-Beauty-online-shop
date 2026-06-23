from rest_framework import serializers

from .models import HomeHero, TrustBadge


class HomeHeroSerializer(serializers.ModelSerializer):
    video_webm_url = serializers.SerializerMethodField()
    video_poster_url = serializers.SerializerMethodField()
    fallback_image_url = serializers.SerializerMethodField()

    class Meta:
        model = HomeHero
        fields = [
            'headline', 'subheadline', 'description',
            'cta_text', 'cta_url', 'cta_secondary_text', 'cta_secondary_url',
            'badge_text', 'video_webm_url', 'video_poster_url', 'fallback_image_url',
        ]

    def _rel(self, obj, field):
        f = getattr(obj, field, None)
        return f.url if f else None

    def get_video_webm_url(self, obj):
        return self._rel(obj, 'video_webm')

    def get_video_poster_url(self, obj):
        return self._rel(obj, 'video_poster')

    def get_fallback_image_url(self, obj):
        return self._rel(obj, 'fallback_image')


class TrustBadgeSerializer(serializers.ModelSerializer):
    class Meta:
        model = TrustBadge
        fields = ['icon', 'title', 'description', 'sort_order']
