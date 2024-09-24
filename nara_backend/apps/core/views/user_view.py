from apps.common.views import NBaselViewSet
from apps.core.models import User
from apps.core.serializers import UserSerializer


class UserViewSet(NBaselViewSet):
    name = "user"
    serializer_class = UserSerializer

    def get_queryset(self):
        return User.objects.all()
