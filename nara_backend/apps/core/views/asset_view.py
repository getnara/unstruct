from apps.core.models import Asset
from apps.core.serializers import AssetSerializer
from apps.core.views.base_view import BaseModelViewSet


class AssetViewSet(BaseModelViewSet):
    name = "asset"
    serializer_class = AssetSerializer

    def get_queryset(self):
        return Asset.objects.all()
