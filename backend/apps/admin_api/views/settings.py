from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.catalog.models import StoreSettings

from ..permissions import IsStaff
from ..serializers import AdminStoreSettingsSerializer


class AdminStoreSettingsView(APIView):
    permission_classes = [IsStaff]

    def _get_instance(self):
        obj, _ = StoreSettings.objects.get_or_create(pk=1)
        return obj

    def get(self, request):
        return Response(AdminStoreSettingsSerializer(self._get_instance()).data)

    def patch(self, request):
        instance = self._get_instance()
        serializer = AdminStoreSettingsSerializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
