from django.urls import path

from .views.blog import (
    AdminPostCategoryListCreateView,
    AdminPostDetailView,
    AdminPostListCreateView,
    AdminTagListCreateView,
)
from .views.brands import AdminBrandDetailView, AdminBrandListCreateView
from .views.categories import AdminCategoryDetailView, AdminCategoryListCreateView
from .views.cms import AdminHomeHeroView, AdminTrustBadgeDetailView, AdminTrustBadgeListCreateView
from .views.coupons import AdminCouponDetailView, AdminCouponListCreateView
from .views.dashboard import DashboardStatsView
from .views.instagram import AdminInstagramDetailView, AdminInstagramListCreateView
from .views.inventory import (
    InventoryAdjustView,
    InventoryListView,
    InventoryMovementsView,
    InventorySummaryView,
    LowStockInventoryView,
)
from .views.notifications import AdminNotificationsSummaryView
from .views.orders import (
    AdminOrderDetailView,
    AdminOrderListView,
    AdminOrderLookupView,
    AdminOrderMarkPaidView,
)
from .views.products import (
    AdminProductDetailView,
    AdminProductImageUploadView,
    AdminProductListCreateView,
)
from .views.reviews import AdminReviewDetailView, AdminReviewListView
from .views.settings import AdminStoreSettingsView
from .views.zarinpal import (
    AdminPaymentDetailView,
    AdminPaymentInquiryView,
    AdminPaymentListView,
    AdminPaymentRefundView,
    AdminPaymentReverseView,
    AdminZarinpalReconciliationsView,
    AdminZarinpalSessionsView,
    AdminZarinpalSettingsView,
    AdminZarinpalTestView,
)
from .views.auth import AdminAuthAuditLogListView, AdminAuthSettingsView
from .views.users import (
    AdminUserDetailView,
    AdminUserDeviceView,
    AdminUserListCreateView,
    AdminUserRevokeSessionsView,
    AdminUserRolesView,
    AdminUserSetPasswordView,
)

urlpatterns = [
    path('dashboard/', DashboardStatsView.as_view()),
    path('notifications/summary/', AdminNotificationsSummaryView.as_view()),
    path('inventory/summary/', InventorySummaryView.as_view()),
    path('inventory/', InventoryListView.as_view()),
    path('inventory/adjust/', InventoryAdjustView.as_view()),
    path('inventory/movements/', InventoryMovementsView.as_view()),
    path('inventory/low-stock/', LowStockInventoryView.as_view()),

    path('cms/hero/', AdminHomeHeroView.as_view()),
    path('cms/trust-badges/', AdminTrustBadgeListCreateView.as_view()),
    path('cms/trust-badges/<uuid:id>/', AdminTrustBadgeDetailView.as_view()),

    path('products/', AdminProductListCreateView.as_view()),
    path('products/<uuid:id>/', AdminProductDetailView.as_view()),
    path('products/<uuid:id>/images/', AdminProductImageUploadView.as_view()),
    path('products/<uuid:id>/images/<uuid:img_id>/', AdminProductImageUploadView.as_view()),

    path('categories/', AdminCategoryListCreateView.as_view()),
    path('categories/<uuid:id>/', AdminCategoryDetailView.as_view()),

    path('brands/', AdminBrandListCreateView.as_view()),
    path('brands/<uuid:id>/', AdminBrandDetailView.as_view()),

    path('orders/', AdminOrderListView.as_view()),
    path('orders/lookup/', AdminOrderLookupView.as_view()),
    path('orders/<uuid:id>/', AdminOrderDetailView.as_view()),
    path('orders/<uuid:id>/mark-paid/', AdminOrderMarkPaidView.as_view()),

    path('users/', AdminUserListCreateView.as_view()),
    path('users/<uuid:id>/', AdminUserDetailView.as_view()),
    path('users/<uuid:id>/set-password/', AdminUserSetPasswordView.as_view()),
    path('users/<uuid:id>/roles/', AdminUserRolesView.as_view()),
    path('users/<uuid:id>/revoke-sessions/', AdminUserRevokeSessionsView.as_view()),
    path('users/<uuid:id>/devices/', AdminUserDeviceView.as_view()),
    path('users/<uuid:id>/devices/<uuid:device_id>/', AdminUserDeviceView.as_view()),

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

    path('payments/', AdminPaymentListView.as_view()),
    path('payments/<uuid:payment_id>/', AdminPaymentDetailView.as_view()),
    path('payments/<uuid:payment_id>/inquiry/', AdminPaymentInquiryView.as_view()),
    path('payments/<uuid:payment_id>/reverse/', AdminPaymentReverseView.as_view()),
    path('payments/<uuid:payment_id>/refund/', AdminPaymentRefundView.as_view()),

    path('zarinpal/settings/', AdminZarinpalSettingsView.as_view()),
    path('zarinpal/settings/test/', AdminZarinpalTestView.as_view()),
    path('zarinpal/sessions/', AdminZarinpalSessionsView.as_view()),
    path('zarinpal/reconciliations/', AdminZarinpalReconciliationsView.as_view()),

    path('auth/settings/', AdminAuthSettingsView.as_view()),
    path('auth/audit-logs/', AdminAuthAuditLogListView.as_view()),
]
