from rest_framework import viewsets

from apps.core.models import User
from apps.core.serializers import UserSerializer


class UserViewSet(viewsets.ModelViewSet):
    name = "user"
    serializer_class = UserSerializer

    def get_queryset(self):
        return User.objects.all()
