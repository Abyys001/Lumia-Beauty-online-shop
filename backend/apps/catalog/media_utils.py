"""Shared helpers for catalog/media serialization."""

from django.conf import settings


def relative_media_url(file_field) -> str | None:
    """Return a browser-safe /media/... path regardless of storage backend."""
    if not file_field:
        return None

    url = file_field.url
    if url.startswith(('http://', 'https://')):
        from urllib.parse import urlparse
        return urlparse(url).path

    if url.startswith('/'):
        return url

    media_prefix = settings.MEDIA_URL.lstrip('/')
    if url.startswith(media_prefix):
        return f'/{url}'

    return f'{settings.MEDIA_URL.rstrip("/")}/{url.lstrip("/")}'
