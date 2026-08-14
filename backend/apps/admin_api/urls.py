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
    AdminSmsProviderLoginView,
    AdminSmsProviderProfileActivateView,
    AdminSmsProviderProfileDetailView,
    AdminSmsProviderProfileListView,
    AdminSmsProviderProfileTestView,
    AdminSmsProviderStatusView,
    AdminSmsProviderTestView,
    AdminSmsProviderVerify2faView,
    AdminSmsProviderView,
)
from .views.sms_tools import (
    AdminSmsCreditView,
    AdminSmsErrorCodesView,
    AdminSmsLinesView,
    AdminSmsLiveReportView,
    AdminSmsMessageReportView,
    AdminSmsPackDetailView,
    AdminSmsReceiveLatestView,
    AdminSmsSendPacksView,
    AdminSmsTestVerifyView,
)
from .views.users import AdminUserDetailView, AdminUserListView

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

    path('payments/', AdminPaymentListView.as_view()),
    path('payments/<uuid:payment_id>/', AdminPaymentDetailView.as_view()),
    path('payments/<uuid:payment_id>/inquiry/', AdminPaymentInquiryView.as_view()),
    path('payments/<uuid:payment_id>/reverse/', AdminPaymentReverseView.as_view()),
    path('payments/<uuid:payment_id>/refund/', AdminPaymentRefundView.as_view()),

    path('zarinpal/settings/', AdminZarinpalSettingsView.as_view()),
    path('zarinpal/settings/test/', AdminZarinpalTestView.as_view()),
    path('zarinpal/sessions/', AdminZarinpalSessionsView.as_view()),
    path('zarinpal/reconciliations/', AdminZarinpalReconciliationsView.as_view()),

    path('sms/providers/', AdminSmsProviderProfileListView.as_view()),
    path('sms/providers/<str:provider_type>/', AdminSmsProviderProfileDetailView.as_view()),
    path('sms/providers/<str:provider_type>/activate/', AdminSmsProviderProfileActivateView.as_view()),
    path('sms/providers/<str:provider_type>/test/', AdminSmsProviderProfileTestView.as_view()),
    path('sms/providers/<str:provider_type>/login/', AdminSmsProviderLoginView.as_view()),
    path('sms/providers/<str:provider_type>/verify-2fa/', AdminSmsProviderVerify2faView.as_view()),
    path('sms/provider/', AdminSmsProviderView.as_view()),
    path('sms/provider/test/', AdminSmsProviderTestView.as_view()),
    path('sms/provider/status/', AdminSmsProviderStatusView.as_view()),
    path('sms/provider/login/', AdminSmsProviderLoginView.as_view()),
    path('sms/provider/verify-2fa/', AdminSmsProviderVerify2faView.as_view()),
    path('sms/templates/', AdminOtpTemplateListCreateView.as_view()),
    path('sms/templates/preview/', AdminOtpTemplatePreviewView.as_view()),
    path('sms/templates/<uuid:id>/', AdminOtpTemplateDetailView.as_view()),
    path('sms/templates/<uuid:id>/activate/', AdminOtpTemplateActivateView.as_view()),
    path('sms/templates/<uuid:id>/set-default/', AdminOtpTemplateSetDefaultView.as_view()),
    path('otp/settings/', AdminOtpSettingsView.as_view()),
    path('auth/settings/', AdminAuthSettingsView.as_view()),
    path('sms/logs/', AdminSmsLogListView.as_view()),
    path('sms/credit/', AdminSmsCreditView.as_view()),
    path('sms/lines/', AdminSmsLinesView.as_view()),
    path('sms/test-verify/', AdminSmsTestVerifyView.as_view()),
    path('sms/reports/message/<int:message_id>/', AdminSmsMessageReportView.as_view()),
    path('sms/reports/packs/', AdminSmsSendPacksView.as_view()),
    path('sms/reports/packs/<str:pack_id>/', AdminSmsPackDetailView.as_view()),
    path('sms/reports/live/', AdminSmsLiveReportView.as_view()),
    path('sms/receive/latest/', AdminSmsReceiveLatestView.as_view()),
    path('sms/error-codes/', AdminSmsErrorCodesView.as_view()),
    path('auth/audit-logs/', AdminAuthAuditLogListView.as_view()),
]
