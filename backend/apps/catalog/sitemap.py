from django.conf import settings
from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.blog.models import Post
from apps.catalog.models import Category, Product


class SitemapAPIView(APIView):
    """Returns URLs for sitemap generation (products, categories, blog posts)."""
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        base = settings.FRONTEND_URL.rstrip('/')
        urls = [
            {'loc': f'{base}/', 'changefreq': 'daily', 'priority': 1.0},
            {'loc': f'{base}/shop', 'changefreq': 'daily', 'priority': 0.9},
            {'loc': f'{base}/blog', 'changefreq': 'weekly', 'priority': 0.8},
            {'loc': f'{base}/about', 'changefreq': 'monthly', 'priority': 0.5},
            {'loc': f'{base}/contact', 'changefreq': 'monthly', 'priority': 0.5},
            {'loc': f'{base}/faq', 'changefreq': 'monthly', 'priority': 0.5},
        ]

        for category in Category.objects.filter(is_active=True).values('slug', 'created_at'):
            urls.append({
                'loc': f'{base}/shop?category={category["slug"]}',
                'lastmod': category['created_at'].isoformat() if category['created_at'] else None,
                'changefreq': 'weekly',
                'priority': 0.65,
            })

        for product in Product.objects.filter(is_active=True).values('slug', 'updated_at'):
            urls.append({
                'loc': f'{base}/shop/{product["slug"]}',
                'lastmod': product['updated_at'].isoformat() if product['updated_at'] else None,
                'changefreq': 'weekly',
                'priority': 0.7,
            })

        for post in Post.objects.filter(is_published=True).values('slug', 'updated_at'):
            urls.append({
                'loc': f'{base}/blog/{post["slug"]}',
                'lastmod': post['updated_at'].isoformat() if post['updated_at'] else None,
                'changefreq': 'monthly',
                'priority': 0.6,
            })

        return Response(urls)
