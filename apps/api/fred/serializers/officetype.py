from rest_framework import serializers
from fred.models.office import (
    Officetype,
)


class OfficeTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Officetype
        fields = ["id", "type"]
