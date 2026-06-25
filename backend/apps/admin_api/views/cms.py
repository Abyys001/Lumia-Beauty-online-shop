from rest_framework import generics, status
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.cms.models import HomeHero, TrustBadge

from ..permissions import IsStaff
from ..serializers_cms import AdminHomeHeroSerializer, AdminTrustBadgeSerializer


class AdminHomeHeroView(APIView):
    permission_classes = [IsStaff]
    parser_classes = [MultiPartParser, FormParser]

    def get(self, request):
        hero = HomeHero.get_active() or HomeHero.objects.order_by('-updated_at').first()
        if not hero:
            return Response(None)
        return Response(AdminHomeHeroSerializer(hero, context={'request': request}).data)

    def patch(self, request):
        hero = HomeHero.get_active() or HomeHero.objects.order_by('-updated_at').first()
        if not hero:
            hero = HomeHero.objects.create(headline='لومیا بیوتی')
        serializer = AdminHomeHeroSerializer(hero, data=request.data, partial=True, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(AdminHomeHeroSerializer(hero, context={'request': request}).data)


class AdminTrustBadgeListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsStaff]
    serializer_class = AdminTrustBadgeSerializer
    pagination_class = None

    def get_queryset(self):
        return TrustBadge.objects.all().order_by('sort_order', 'title')

    def get_serializer_context(self):
        ctx = super().get_serializer_context()
        ctx['request'] = self.request
        return ctx


class AdminTrustBadgeDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsStaff]
    serializer_class = AdminTrustBadgeSerializer
    lookup_field = 'id'
    queryset = TrustBadge.objects.all()

    def get_serializer_context(self):
        ctx = super().get_serializer_context()
        ctx['request'] = self.request
        return ctx

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)
