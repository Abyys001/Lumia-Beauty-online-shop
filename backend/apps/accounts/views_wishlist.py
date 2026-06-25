from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.catalog.models import Product
from apps.catalog.serializers import ProductListSerializer

from .models import WishlistItem


class WishlistListCreateView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        items = (
            WishlistItem.objects.filter(user=request.user)
            .select_related('product', 'product__brand', 'product__category')
            .prefetch_related('product__images')
        )
        products = [item.product for item in items if item.product.is_active]
        return Response(ProductListSerializer(products, many=True).data)

    def post(self, request):
        product_id = request.data.get('product_id')
        if not product_id:
            return Response({'detail': 'شناسه محصول الزامی است'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            product = Product.objects.get(id=product_id, is_active=True)
        except Product.DoesNotExist:
            return Response({'detail': 'محصول یافت نشد'}, status=status.HTTP_404_NOT_FOUND)
        WishlistItem.objects.get_or_create(user=request.user, product=product)
        return Response({'detail': 'به علاقه‌مندی‌ها اضافه شد'}, status=status.HTTP_201_CREATED)


class WishlistIdsView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        ids = list(
            WishlistItem.objects.filter(user=request.user, product__is_active=True)
            .values_list('product_id', flat=True)
        )
        return Response([str(pid) for pid in ids])


class WishlistDetailView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request, product_id):
        deleted, _ = WishlistItem.objects.filter(user=request.user, product_id=product_id).delete()
        if not deleted:
            return Response({'detail': 'در لیست علاقه‌مندی‌ها نبود'}, status=status.HTTP_404_NOT_FOUND)
        return Response(status=status.HTTP_204_NO_CONTENT)
