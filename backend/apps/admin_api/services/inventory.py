from django.db import transaction

from apps.catalog.models import Product, StockMovement, StoreSettings


class InventoryAdjustmentError(Exception):
    def __init__(self, message, code='invalid'):
        self.message = message
        self.code = code
        super().__init__(message)


def get_default_threshold():
    return StoreSettings.get_settings().default_low_stock_threshold


def get_inventory_summary():
    products = Product.objects.filter(is_active=True)
    out_of_stock = products.filter(stock=0).count()
    total = products.count()

    low_stock = 0
    healthy = 0
    for product in products.only('stock', 'low_stock_threshold'):
        threshold = product.get_effective_low_stock_threshold()
        if product.stock == 0:
            continue
        if product.stock < threshold:
            low_stock += 1
        else:
            healthy += 1

    return {
        'out_of_stock': out_of_stock,
        'low_stock': low_stock,
        'healthy': healthy,
        'total': total,
        'default_threshold': get_default_threshold(),
    }


def count_low_stock_products(threshold_override=None):
    count = 0
    for product in Product.objects.filter(is_active=True).only('stock', 'low_stock_threshold'):
        if is_low_stock(product, threshold_override):
            count += 1
    return count


def is_low_stock(product, threshold_override=None):
    if product.stock == 0:
        return False
    threshold = threshold_override if threshold_override is not None else product.get_effective_low_stock_threshold()
    return product.stock < threshold


def filter_inventory_products(
    *,
    q='',
    category_id=None,
    brand_id=None,
    status='all',
    threshold_override=None,
):
    qs = Product.objects.filter(is_active=True).select_related('category', 'brand').prefetch_related('images')

    if q:
        qs = qs.filter(models_q_filter(q))

    if category_id:
        qs = qs.filter(category_id=category_id)
    if brand_id:
        qs = qs.filter(brand_id=brand_id)

    if status == 'out':
        qs = qs.filter(stock=0)
    elif status in ('low', 'ok'):
        # Filter in Python for per-product thresholds
        products = list(qs.order_by('stock', 'name'))
        if status == 'low':
            products = [p for p in products if is_low_stock(p, threshold_override)]
        else:
            products = [
                p for p in products
                if p.stock > 0 and not is_low_stock(p, threshold_override)
            ]
        return products

    return qs.order_by('stock', 'name')


def models_q_filter(q):
    from django.db.models import Q
    return Q(name__icontains=q) | Q(sku__icontains=q)


@transaction.atomic
def adjust_product_stock(
    product_id,
    *,
    mode,
    pack_size=None,
    pack_count=None,
    delta=None,
    absolute_stock=None,
    note='',
    reason=StockMovement.REASON_MANUAL,
    created_by=None,
):
    try:
        product = Product.objects.select_for_update().get(pk=product_id, is_active=True)
    except Product.DoesNotExist:
        raise InventoryAdjustmentError('محصول یافت نشد', 'not_found')

    stock_before = product.stock
    allowed_sizes = product.get_effective_pack_sizes()

    if mode == 'pack':
        if pack_size is None or pack_count is None:
            raise InventoryAdjustmentError('اندازه و تعداد بسته الزامی است')
        pack_size = int(pack_size)
        pack_count = int(pack_count)
        if pack_size not in allowed_sizes and pack_size != 1:
            raise InventoryAdjustmentError('اندازه بسته برای این محصول مجاز نیست')
        if pack_count == 0:
            raise InventoryAdjustmentError('تعداد بسته نمی‌تواند صفر باشد')
        computed_delta = pack_size * pack_count
    elif mode == 'delta':
        if delta is None:
            raise InventoryAdjustmentError('مقدار تغییر الزامی است')
        computed_delta = int(delta)
        pack_size = None
        pack_count = None
    elif mode == 'set':
        if absolute_stock is None:
            raise InventoryAdjustmentError('مقدار دقیق موجودی الزامی است')
        target = max(0, int(absolute_stock))
        computed_delta = target - stock_before
        pack_size = None
        pack_count = None
    else:
        raise InventoryAdjustmentError('نوع تعدیل نامعتبر است')

    stock_after = max(0, stock_before + computed_delta)
    if stock_after == stock_before and mode != 'set':
        raise InventoryAdjustmentError('تغییری در موجودی ایجاد نشد')

    product.stock = stock_after
    product.save(update_fields=['stock', 'updated_at'])

    movement = StockMovement.objects.create(
        product=product,
        delta=computed_delta,
        stock_before=stock_before,
        stock_after=stock_after,
        pack_size=pack_size if mode == 'pack' else None,
        pack_count=pack_count if mode == 'pack' else None,
        reason=reason,
        note=note or '',
        created_by=created_by,
    )

    return product, movement
