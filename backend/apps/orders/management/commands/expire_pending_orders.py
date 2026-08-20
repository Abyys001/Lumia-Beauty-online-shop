from django.core.management.base import BaseCommand

from apps.orders.services import expire_stale_pending_orders, expiry_days


class Command(BaseCommand):
    help = 'Cancel card-to-card orders whose payment window has passed'

    def add_arguments(self, parser):
        parser.add_argument(
            '--days',
            type=int,
            default=None,
            help=f'Payment window in days (default: PENDING_ORDER_EXPIRY_DAYS = {expiry_days()})',
        )

    def handle(self, *args, **options):
        count = expire_stale_pending_orders(days=options['days'])
        self.stdout.write(self.style.SUCCESS(f'Expired orders: {count}'))
