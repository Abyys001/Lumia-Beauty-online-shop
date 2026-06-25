from datetime import timedelta

from django.db.models import Count, Sum
from django.db.models.functions import TruncDate
from django.utils import timezone
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.models import User
from apps.catalog.models import Product, Review
from apps.orders.models import Order

from ..permissions import IsStaff
from ..services.inventory import count_low_stock_products


class DashboardStatsView(APIView):
    permission_classes = [IsStaff]

    def get(self, request):
        today = timezone.localtime(timezone.now()).date()
        week_start = today - timedelta(days=7)
        month_start = today - timedelta(days=29)

        paid_statuses = [
            Order.STATUS_PAID,
            Order.STATUS_PROCESSING,
            Order.STATUS_SHIPPED,
            Order.STATUS_DELIVERED,
        ]

        today_income = Order.objects.filter(
            status__in=paid_statuses,
            created_at__date=today,
        ).aggregate(s=Sum('total'))['s'] or 0

        weekly_income = Order.objects.filter(
            status__in=paid_statuses,
            created_at__date__gte=week_start,
        ).aggregate(s=Sum('total'))['s'] or 0

        recent_orders = Order.objects.select_related('user').order_by('-created_at')[:10]

        daily_revenue_qs = (
            Order.objects.filter(status__in=paid_statuses, created_at__date__gte=month_start)
            .annotate(day=TruncDate('created_at'))
            .values('day')
            .annotate(revenue=Sum('total'), order_count=Count('id'))
            .order_by('day')
        )
        daily_map = {row['day']: row for row in daily_revenue_qs}
        daily_revenue = []
        for i in range(30):
            day = month_start + timedelta(days=i)
            row = daily_map.get(day)
            daily_revenue.append({
                'date': day.isoformat(),
                'revenue': row['revenue'] if row else 0,
                'order_count': row['order_count'] if row else 0,
            })

        top_products = list(
            Product.objects.filter(is_active=True, sales_count__gt=0)
            .order_by('-sales_count')[:5]
            .values('id', 'name', 'slug', 'sales_count', 'stock', 'price')
        )

        orders_by_status = {
            row['status']: row['count']
            for row in Order.objects.values('status').annotate(count=Count('id'))
        }

        return Response({
            'new_orders_count': Order.objects.filter(status=Order.STATUS_PAID).count(),
            'today_income': today_income,
            'weekly_income': weekly_income,
            'total_orders': Order.objects.count(),
            'total_users': User.objects.count(),
            'total_products': Product.objects.filter(is_active=True).count(),
            'low_stock_count': count_low_stock_products(),
            'pending_reviews_count': Review.objects.filter(is_approved=False).count(),
            'daily_revenue': daily_revenue,
            'top_products': top_products,
            'orders_by_status': orders_by_status,
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
