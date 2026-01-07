from rest_framework import serializers
from ..models.officetype import Officetype


class OfficeTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Officetype
        fields = ["id", "type"]
