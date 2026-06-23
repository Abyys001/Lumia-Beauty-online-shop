from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import HomeHero, TrustBadge
from .serializers import HomeHeroSerializer, TrustBadgeSerializer


class HomeCMSView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        hero = HomeHero.get_active()
        badges = TrustBadge.objects.filter(is_active=True)

        data = {
            'hero': HomeHeroSerializer(hero, context={'request': request}).data if hero else None,
            'trust_badges': TrustBadgeSerializer(badges, many=True).data,
        }
        return Response(data)
