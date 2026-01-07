"""
logs Serializers Module

Contains serializers related to logs domain.
"""
from rest_framework import serializers
from fred.models import Failedfulfilllog

class FredFailedfulfillogSerializer(serializers.ModelSerializer):
    class Meta:
        model = Failedfulfilllog
        fields = "__all__"

__all__ = [
    'FredFailedfulfillogSerializer'
]
