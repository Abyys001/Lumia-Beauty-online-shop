"""Guards for the media URL contract the frontend depends on.

Every image URL in an API payload must be a root-relative `/media/...` path: the
browser only ever talks to the frontend origin, which proxies those two prefixes
to Django (nginx on the VPS, the Liara edge proxy, or server/routes/media in the
Nuxt server). An absolute backend URL here would point the browser at a host it
cannot reach and break every image on the site.
"""

from io import BytesIO

from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from PIL import Image
from rest_framework.test import APIClient

from apps.blog.models import Post, PostCategory
from apps.catalog.models import Category, Product, ProductImage
from apps.cms.models import HomeHero


def image_file(name='test.png'):
    buffer = BytesIO()
    Image.new('RGB', (10, 10), 'white').save(buffer, format='PNG')
    return SimpleUploadedFile(name, buffer.getvalue(), content_type='image/png')


class MediaUrlContractTests(TestCase):
    def setUp(self):
        # Product lists and the CMS home payload are cached; another test's response
        # would otherwise be served here.
        cache.clear()
        self.client = APIClient()
        self.category = Category.objects.create(name='پوست', slug='skin')
        self.product = Product.objects.create(
            name='کرم تست',
            slug='test-cream',
            description='توضیح تست',
            category=self.category,
            price=100000,
            stock=5,
            sku='TEST-CREAM',
            is_featured=True,
        )
        self.image = ProductImage.objects.create(
            product=self.product, image=image_file(), is_primary=True,
        )

    def assertRelativeMedia(self, url):
        self.assertTrue(url, 'image url is empty')
        self.assertTrue(
            url.startswith('/media/'),
            f'expected a root-relative /media/... path, got {url!r}',
        )

    def test_product_list_and_detail_return_relative_media_paths(self):
        response = self.client.get('/api/products/')
        self.assertEqual(response.status_code, 200)
        self.assertRelativeMedia(response.data['results'][0]['primary_image'])

        response = self.client.get(f'/api/products/{self.product.slug}/')
        self.assertEqual(response.status_code, 200)
        self.assertRelativeMedia(response.data['primary_image'])
        self.assertRelativeMedia(response.data['images'][0]['image'])

    def test_blog_post_cover_is_a_relative_media_path(self):
        category = PostCategory.objects.create(name='مقالات', slug='articles')
        post = Post.objects.create(
            title='مقاله تست',
            slug='test-post',
            excerpt='خلاصه',
            content='متن',
            category=category,
            cover_image=image_file('cover.png'),
            is_published=True,
        )
        response = self.client.get(f'/api/blog/posts/{post.slug}/')
        self.assertEqual(response.status_code, 200)
        self.assertRelativeMedia(response.data['cover_image'])

    def test_home_hero_images_are_relative_media_paths(self):
        HomeHero.objects.create(
            headline='تیتر تست',
            fallback_image=image_file('hero.png'),
            video_poster=image_file('poster.png'),
            is_active=True,
        )
        response = self.client.get('/api/cms/home/')
        self.assertEqual(response.status_code, 200)
        hero = response.data['hero']
        self.assertRelativeMedia(hero['fallback_image_url'])
        self.assertRelativeMedia(hero['video_poster_url'])

    def test_uploaded_product_image_is_served_by_django(self):
        response = self.client.get(f'/api/products/{self.product.slug}/')
        path = response.data['primary_image']

        served = self.client.get(path)
        self.assertEqual(served.status_code, 200, f'Django does not serve {path}')
