from django.core.management.base import BaseCommand

from apps.payments.services import process_unverified_payments, run_reconciliation


class Command(BaseCommand):
    help = 'Process unverified Zarinpal payments and optionally run reconciliation'

    def handle(self, *args, **options):
        result = process_unverified_payments()
        self.stdout.write(self.style.SUCCESS(f'Unverified: {result}'))

        reconcile = run_reconciliation()
        if not reconcile.get('skipped'):
            self.stdout.write(self.style.SUCCESS(f'Reconciliation: {reconcile}'))
