from apps.common.serializers import NBaseSerializer
from apps.core.models import Asset


class AssetSerializer(NBaseSerializer):
    class Meta:
        model = Asset
        fields = "__all__"
