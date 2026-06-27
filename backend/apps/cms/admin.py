from django.contrib import admin

from .models import HomeHero, InstagramPage, TrustBadge


@admin.register(HomeHero)
class HomeHeroAdmin(admin.ModelAdmin):
    list_display = ['headline', 'is_active', 'updated_at']
    list_editable = ['is_active']
    fieldsets = (
        ('محتوا', {
            'fields': ('headline', 'subheadline', 'description', 'badge_text', 'is_active'),
        }),
        ('دکمه‌ها', {
            'fields': ('cta_text', 'cta_url', 'cta_secondary_text', 'cta_secondary_url'),
        }),
        ('رسانه', {
            'fields': ('video_webm', 'video_poster', 'fallback_image'),
        }),
    )


@admin.register(TrustBadge)
class TrustBadgeAdmin(admin.ModelAdmin):
    list_display = ['title', 'icon', 'is_active']
    list_editable = ['is_active']
    ordering = ['created_at']


@admin.register(InstagramPage)
class InstagramPageAdmin(admin.ModelAdmin):
    list_display = ['username', 'label', 'is_active']
    list_editable = ['is_active']
    ordering = ['created_at']
