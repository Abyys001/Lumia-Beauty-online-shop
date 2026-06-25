from rest_framework.response import Response
from rest_framework.views import APIView

from apps.catalog.models import Review
from apps.orders.models import Order

from ..permissions import IsStaff
from ..services.inventory import count_low_stock_products


class AdminNotificationsSummaryView(APIView):
    permission_classes = [IsStaff]

    def get(self, request):
        try:
            threshold = int(request.query_params.get('threshold', 5))
        except (TypeError, ValueError):
            threshold = 5

        return Response({
            'pending_orders': Order.objects.filter(
                status__in=[Order.STATUS_PAID, Order.STATUS_PROCESSING],
            ).count(),
            'pending_reviews': Review.objects.filter(is_approved=False).count(),
            'low_stock_count': count_low_stock_products(threshold),
        })
