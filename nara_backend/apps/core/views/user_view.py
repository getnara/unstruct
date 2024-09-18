from apps.core.models import User
from apps.core.serializers import UserSerializer
from apps.core.views.base_view import BaseModelViewSet


class UserViewSet(BaseModelViewSet):
    name = "user"
    serializer_class = UserSerializer

    def get_queryset(self):
        return User.objects.all()
