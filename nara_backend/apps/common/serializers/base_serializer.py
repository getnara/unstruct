from rest_framework import serializers

from apps.common.models import NBaseModel


class NBaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = NBaseModel
        fields = "__all__"
