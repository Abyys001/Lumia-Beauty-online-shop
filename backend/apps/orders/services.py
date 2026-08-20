"""Housekeeping for card-to-card orders that were never confirmed."""

import logging
from datetime import timedelta

from django.conf import settings
from django.core.cache import cache
from django.utils import timezone

from apps.payments.models import Payment

from .models import Order

logger = logging.getLogger(__name__)

SWEEP_CACHE_KEY = 'orders:expiry-sweep'
SWEEP_INTERVAL_SECONDS = 3600


def expiry_days() -> int:
    return getattr(settings, 'PENDING_ORDER_EXPIRY_DAYS', 7)


def expires_at(order: Order):
    """Deadline for paying an order, or None once it is no longer pending."""
    if order.status != Order.STATUS_PENDING:
        return None
    return order.created_at + timedelta(days=expiry_days())


def expire_stale_pending_orders(days: int | None = None) -> int:
    """Cancel pending orders whose payment window has passed.

    Stock is only decremented when the seller confirms the transfer, so an
    expired order has nothing to release — only its status has to reflect that
    the purchase code is no longer good.
    """
    cutoff = timezone.now() - timedelta(days=days if days is not None else expiry_days())
    stale = Order.objects.filter(status=Order.STATUS_PENDING, created_at__lt=cutoff)
    order_ids = list(stale.values_list('id', flat=True))
    if not order_ids:
        return 0

    Payment.objects.filter(order_id__in=order_ids, status=Payment.STATUS_PENDING).update(
        status=Payment.STATUS_FAILED,
    )
    count = Order.objects.filter(id__in=order_ids, status=Order.STATUS_PENDING).update(
        status=Order.STATUS_CANCELLED,
    )
    logger.info('Expired %s unpaid orders older than the payment window', count)
    return count


def maybe_expire_stale_orders() -> None:
    """Run the sweep at most once an hour, from whichever request gets there first.

    The project has no scheduler; the management command covers cron setups and
    this keeps statuses honest on deployments that have none.
    """
    if not cache.add(SWEEP_CACHE_KEY, '1', SWEEP_INTERVAL_SECONDS):
        return
    try:
        expire_stale_pending_orders()
    except Exception:
        logger.exception('Pending-order expiry sweep failed')
