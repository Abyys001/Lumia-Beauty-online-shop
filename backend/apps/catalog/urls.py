from django.urls import path

from .views import (
    BrandListView,
    CategoryListView,
    FeaturedProductsView,
    ProductDetailView,
    ProductListView,
    ProductReviewCreateView,
    ProductSearchView,
    RelatedProductsView,
    ShippingSettingsView,
    StoreContactView,
)
from .sitemap import SitemapAPIView

urlpatterns = [
    path('products/', ProductListView.as_view(), name='product-list'),
    path('products/featured/', FeaturedProductsView.as_view(), name='product-featured'),
    path('products/search/', ProductSearchView.as_view(), name='product-search'),
    path('products/<slug:slug>/', ProductDetailView.as_view(), name='product-detail'),
    path('products/<slug:slug>/related/', RelatedProductsView.as_view(), name='product-related'),
    path('products/<slug:slug>/reviews/', ProductReviewCreateView.as_view(), name='product-review'),
    path('categories/', CategoryListView.as_view(), name='category-list'),
    path('brands/', BrandListView.as_view(), name='brand-list'),
    path('store/shipping/', ShippingSettingsView.as_view(), name='store-shipping'),
    path('store/contact/', StoreContactView.as_view(), name='store-contact'),
    path('sitemap-urls/', SitemapAPIView.as_view(), name='sitemap-urls'),
]
