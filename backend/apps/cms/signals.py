from django.core.cache import cache
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from .models import HomeHero, TrustBadge


def invalidate_cms_home_cache():
    cache.delete('cms_home')


@receiver(post_save, sender=HomeHero)
@receiver(post_delete, sender=HomeHero)
def home_hero_changed(sender, instance, **kwargs):
    invalidate_cms_home_cache()


@receiver(post_save, sender=TrustBadge)
@receiver(post_delete, sender=TrustBadge)
def trust_badge_changed(sender, instance, **kwargs):
    invalidate_cms_home_cache()
