from django.core.cache import cache
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from .models import Brand, Category, Product, ProductImage, ProductAttribute, Review


def invalidate_product_cache(product_id=None, slug=None):
    if product_id:
        cache.delete(f'product_detail:{product_id}')
    if slug:
        cache.delete(f'product_detail_slug:{slug}')
        cache.delete(f'product_related:{slug}')
    cache.delete('products_featured')
    try:
        cache.delete_pattern('products_list:*')
        cache.delete_pattern('search:*')
    except AttributeError:
        pass


def invalidate_catalog_taxonomy_cache():
    cache.delete('categories_list')
    cache.delete('brands_list')


@receiver(post_save, sender=Product)
def product_saved(sender, instance, **kwargs):
    invalidate_product_cache(product_id=instance.id, slug=instance.slug)


@receiver(post_delete, sender=Product)
def product_deleted(sender, instance, **kwargs):
    invalidate_product_cache(product_id=instance.id, slug=instance.slug)


@receiver(post_save, sender=ProductImage)
@receiver(post_delete, sender=ProductImage)
def product_image_changed(sender, instance, **kwargs):
    if instance.product:
        invalidate_product_cache(product_id=instance.product.id, slug=instance.product.slug)


@receiver(post_save, sender=ProductAttribute)
@receiver(post_delete, sender=ProductAttribute)
def product_attribute_changed(sender, instance, **kwargs):
    if instance.product:
        invalidate_product_cache(product_id=instance.product.id, slug=instance.product.slug)


@receiver(post_save, sender=Review)
@receiver(post_delete, sender=Review)
def review_changed(sender, instance, **kwargs):
    if instance.product:
        invalidate_product_cache(product_id=instance.product.id, slug=instance.product.slug)


@receiver(post_save, sender=Category)
@receiver(post_delete, sender=Category)
def category_changed(sender, instance, **kwargs):
    invalidate_catalog_taxonomy_cache()


@receiver(post_save, sender=Brand)
@receiver(post_delete, sender=Brand)
def brand_changed(sender, instance, **kwargs):
    invalidate_catalog_taxonomy_cache()

