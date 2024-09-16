from rest_framework import serializers

from apps.core.models import Action


class ActionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Action
        fields = "__all__"
