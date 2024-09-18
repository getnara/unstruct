from rest_framework import viewsets
from rest_framework.pagination import LimitOffsetPagination


class StandardResultsSetPagination(LimitOffsetPagination):
    pass


class BaseModelViewSet(viewsets.ModelViewSet):
    name = ""
    pagination_class = StandardResultsSetPagination
