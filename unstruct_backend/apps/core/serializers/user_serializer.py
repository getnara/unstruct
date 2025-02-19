from apps.common.serializers import NBaseSerializer
from apps.core.models import User


class UserSerializer(NBaseSerializer):
    class Meta:
        model = User
        fields = "__all__"
