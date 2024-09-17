from rest_framework import viewsets

from apps.core.models import Asset
from apps.core.serializers import AssetSerializer


class AssetViewSet(viewsets.ModelViewSet):
    name = "asset"
    serializer_class = AssetSerializer

    def get_queryset(self):
        return Asset.objects.all()
