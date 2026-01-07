"""
reference Serializers Module

Contains serializers related to reference domain.
"""
from rest_framework import serializers
from fred.models import Faq

class FredFaqSerializer(serializers.ModelSerializer):
    class Meta:
        model = Faq
        fields = "__all__"
    
    def validate_category(self, value):
        """Convert category to lowercase to match legacy PHP behavior"""
        if value:
            return value.lower()
        return value

__all__ = [
    'FredFaqSerializer'
]