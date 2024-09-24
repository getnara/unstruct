from rest_framework import viewsets
from rest_framework.pagination import LimitOffsetPagination

from apps.common.serializers import NBaseSerializer


class StandardResultsSetPagination(LimitOffsetPagination):
    pass


class NBaselViewSet(viewsets.ModelViewSet):
    name = ""
    pagination_class = StandardResultsSetPagination
    serializer_class = NBaseSerializer
