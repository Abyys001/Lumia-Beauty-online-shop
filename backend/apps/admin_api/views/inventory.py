from django.core.paginator import Paginator
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.catalog.models import Product, StockMovement
from apps.catalog.serializers import ProductListSerializer

from ..permissions import IsStaff
from ..serializers import (
    AdminInventoryAdjustSerializer,
    AdminInventoryProductSerializer,
    StockMovementSerializer,
)
from ..services.inventory import (
    InventoryAdjustmentError,
    adjust_product_stock,
    filter_inventory_products,
    get_inventory_summary,
)


def _serialize_product(product):
    data = AdminInventoryProductSerializer(product).data
    data['primary_image'] = ProductListSerializer(product).data.get('primary_image')
    return data


class InventorySummaryView(APIView):
    permission_classes = [IsStaff]

    def get(self, request):
        return Response(get_inventory_summary())


class InventoryListView(APIView):
    permission_classes = [IsStaff]

    def get(self, request):
        try:
            threshold = int(request.query_params.get('threshold', 0)) or None
        except (TypeError, ValueError):
            threshold = None

        status_filter = request.query_params.get('status', 'all')
        q = request.query_params.get('q', '').strip()
        category_id = request.query_params.get('category') or None
        brand_id = request.query_params.get('brand') or None
        page = max(1, int(request.query_params.get('page', 1)))
        page_size = min(max(1, int(request.query_params.get('page_size', 20))), 100)

        products = filter_inventory_products(
            q=q,
            category_id=category_id,
            brand_id=brand_id,
            status=status_filter,
            threshold_override=threshold,
        )

        if isinstance(products, list):
            paginator = Paginator(products, page_size)
            page_obj = paginator.get_page(page)
            results = [_serialize_product(p) for p in page_obj.object_list]
            return Response({
                'count': paginator.count,
                'page': page,
                'page_size': page_size,
                'total_pages': paginator.num_pages,
                'results': results,
            })

        paginator = Paginator(products, page_size)
        page_obj = paginator.get_page(page)
        results = [_serialize_product(p) for p in page_obj.object_list]
        return Response({
            'count': paginator.count,
            'page': page,
            'page_size': page_size,
            'total_pages': paginator.num_pages,
            'results': results,
        })


class InventoryAdjustView(APIView):
    permission_classes = [IsStaff]

    def post(self, request):
        serializer = AdminInventoryAdjustSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        try:
            product, movement = adjust_product_stock(
                data['product_id'],
                mode=data['mode'],
                pack_size=data.get('pack_size'),
                pack_count=data.get('pack_count'),
                delta=data.get('delta'),
                absolute_stock=data.get('absolute_stock'),
                note=data.get('note', ''),
                reason=data.get('reason', StockMovement.REASON_MANUAL),
                created_by=request.user,
            )
        except InventoryAdjustmentError as exc:
            return Response({'detail': exc.message, 'code': exc.code}, status=status.HTTP_400_BAD_REQUEST)

        return Response({
            'stock': product.stock,
            'movement': StockMovementSerializer(movement).data,
            'product': _serialize_product(product),
        })


class InventoryMovementsView(APIView):
    permission_classes = [IsStaff]

    def get(self, request):
        limit = min(max(1, int(request.query_params.get('limit', 20))), 100)
        product_id = request.query_params.get('product_id')

        qs = StockMovement.objects.select_related('product', 'created_by').order_by('-created_at')
        if product_id:
            qs = qs.filter(product_id=product_id)

        movements = qs[:limit]
        return Response({
            'results': StockMovementSerializer(movements, many=True).data,
        })


class LowStockInventoryView(APIView):
    """Backward-compatible endpoint used by older clients."""

    permission_classes = [IsStaff]

    def get(self, request):
        try:
            threshold = int(request.query_params.get('threshold', 5))
        except (TypeError, ValueError):
            threshold = 5
        threshold = max(1, min(threshold, 100))

        products = filter_inventory_products(status='low', threshold_override=threshold)
        return Response({
            'threshold': threshold,
            'count': len(products),
            'results': [_serialize_product(p) for p in products],
        })
