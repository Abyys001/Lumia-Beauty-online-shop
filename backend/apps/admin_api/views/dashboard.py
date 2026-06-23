from datetime import timedelta

from django.db.models import Sum
from django.utils import timezone
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.models import User
from apps.catalog.models import Product
from apps.orders.models import Order

from ..permissions import IsStaff


class DashboardStatsView(APIView):
    permission_classes = [IsStaff]

    def get(self, request):
        today = timezone.localtime(timezone.now()).date()
        week_start = today - timedelta(days=7)

        paid_orders = Order.objects.filter(status=Order.STATUS_PAID)

        today_income = Order.objects.filter(
            status=Order.STATUS_PAID,
            created_at__date=today,
        ).aggregate(s=Sum('total'))['s'] or 0

        weekly_income = Order.objects.filter(
            status=Order.STATUS_PAID,
            created_at__date__gte=week_start,
        ).aggregate(s=Sum('total'))['s'] or 0

        recent_orders = Order.objects.select_related('user').order_by('-created_at')[:10]

        return Response({
            'new_orders_count': paid_orders.count(),
            'today_income': today_income,
            'weekly_income': weekly_income,
            'total_orders': Order.objects.count(),
            'total_users': User.objects.count(),
            'total_products': Product.objects.filter(is_active=True).count(),
            'low_stock_count': Product.objects.filter(stock__lt=5, is_active=True).count(),
            'recent_orders': [
                {
                    'id': str(o.id),
                    'order_number': o.order_number,
                    'user_phone': o.user.phone,
                    'status': o.status,
                    'total': o.total,
                    'created_at': o.created_at,
                }
                for o in recent_orders
            ],
        })
