from django.urls import path

from .views import (
    BrandListView,
    CategoryListView,
    FeaturedProductsView,
    InstagramPostListView,
    ProductDetailView,
    ProductListView,
    ProductReviewCreateView,
    ProductSearchView,
)
from .sitemap import SitemapAPIView

urlpatterns = [
    path('products/', ProductListView.as_view(), name='product-list'),
    path('products/featured/', FeaturedProductsView.as_view(), name='product-featured'),
    path('products/search/', ProductSearchView.as_view(), name='product-search'),
    path('products/<slug:slug>/', ProductDetailView.as_view(), name='product-detail'),
    path('products/<slug:slug>/reviews/', ProductReviewCreateView.as_view(), name='product-review'),
    path('categories/', CategoryListView.as_view(), name='category-list'),
    path('brands/', BrandListView.as_view(), name='brand-list'),
    path('instagram/', InstagramPostListView.as_view(), name='instagram-list'),
    path('sitemap-urls/', SitemapAPIView.as_view(), name='sitemap-urls'),
]
