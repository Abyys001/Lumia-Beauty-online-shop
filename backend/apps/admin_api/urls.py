from django.urls import path

from .views.blog import (
    AdminPostCategoryListCreateView,
    AdminPostDetailView,
    AdminPostListCreateView,
    AdminTagListCreateView,
)
from .views.brands import AdminBrandDetailView, AdminBrandListCreateView
from .views.categories import AdminCategoryDetailView, AdminCategoryListCreateView
from .views.coupons import AdminCouponDetailView, AdminCouponListCreateView
from .views.dashboard import DashboardStatsView
from .views.instagram import AdminInstagramDetailView, AdminInstagramListCreateView
from .views.orders import AdminOrderDetailView, AdminOrderListView
from .views.products import (
    AdminProductDetailView,
    AdminProductImageUploadView,
    AdminProductListCreateView,
)
from .views.reviews import AdminReviewDetailView, AdminReviewListView
from .views.settings import AdminStoreSettingsView
from .views.sms import (
    AdminAuthAuditLogListView,
    AdminAuthSettingsView,
    AdminOtpSettingsView,
    AdminOtpTemplateActivateView,
    AdminOtpTemplateDetailView,
    AdminOtpTemplateListCreateView,
    AdminOtpTemplatePreviewView,
    AdminOtpTemplateSetDefaultView,
    AdminSmsLogListView,
    AdminSmsProviderStatusView,
    AdminSmsProviderTestView,
    AdminSmsProviderView,
)
from .views.users import AdminUserDetailView, AdminUserListView

urlpatterns = [
    path('dashboard/', DashboardStatsView.as_view()),

    path('products/', AdminProductListCreateView.as_view()),
    path('products/<uuid:id>/', AdminProductDetailView.as_view()),
    path('products/<uuid:id>/images/', AdminProductImageUploadView.as_view()),
    path('products/<uuid:id>/images/<uuid:img_id>/', AdminProductImageUploadView.as_view()),

    path('categories/', AdminCategoryListCreateView.as_view()),
    path('categories/<uuid:id>/', AdminCategoryDetailView.as_view()),

    path('brands/', AdminBrandListCreateView.as_view()),
    path('brands/<uuid:id>/', AdminBrandDetailView.as_view()),

    path('orders/', AdminOrderListView.as_view()),
    path('orders/<uuid:id>/', AdminOrderDetailView.as_view()),

    path('users/', AdminUserListView.as_view()),
    path('users/<uuid:id>/', AdminUserDetailView.as_view()),

    path('coupons/', AdminCouponListCreateView.as_view()),
    path('coupons/<uuid:id>/', AdminCouponDetailView.as_view()),

    path('blog/posts/', AdminPostListCreateView.as_view()),
    path('blog/posts/<uuid:id>/', AdminPostDetailView.as_view()),
    path('blog/categories/', AdminPostCategoryListCreateView.as_view()),
    path('blog/tags/', AdminTagListCreateView.as_view()),

    path('reviews/', AdminReviewListView.as_view()),
    path('reviews/<uuid:id>/', AdminReviewDetailView.as_view()),

    path('instagram/', AdminInstagramListCreateView.as_view()),
    path('instagram/<uuid:id>/', AdminInstagramDetailView.as_view()),

    path('settings/', AdminStoreSettingsView.as_view()),

    path('sms/provider/', AdminSmsProviderView.as_view()),
    path('sms/provider/test/', AdminSmsProviderTestView.as_view()),
    path('sms/provider/status/', AdminSmsProviderStatusView.as_view()),
    path('sms/templates/', AdminOtpTemplateListCreateView.as_view()),
    path('sms/templates/preview/', AdminOtpTemplatePreviewView.as_view()),
    path('sms/templates/<uuid:id>/', AdminOtpTemplateDetailView.as_view()),
    path('sms/templates/<uuid:id>/activate/', AdminOtpTemplateActivateView.as_view()),
    path('sms/templates/<uuid:id>/set-default/', AdminOtpTemplateSetDefaultView.as_view()),
    path('otp/settings/', AdminOtpSettingsView.as_view()),
    path('auth/settings/', AdminAuthSettingsView.as_view()),
    path('sms/logs/', AdminSmsLogListView.as_view()),
    path('auth/audit-logs/', AdminAuthAuditLogListView.as_view()),
]
