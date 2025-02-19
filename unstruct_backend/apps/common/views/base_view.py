from rest_framework import viewsets
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import IsAuthenticated

from apps.common.serializers import NBaseSerializer
from apps.common.auth.simple_auth import SimpleAuthentication


class StandardResultsSetPagination(LimitOffsetPagination):
    pass


class NBaselViewSet(viewsets.ModelViewSet):
    name = ""
    pagination_class = StandardResultsSetPagination
    serializer_class = NBaseSerializer
    authentication_classes = [SimpleAuthentication]
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(
            created_by=self.request.user,
            updated_by=self.request.user
        )

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)
