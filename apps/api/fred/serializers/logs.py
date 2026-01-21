"""
logs Serializers Module

Contains serializers related to logs domain.
"""
from rest_framework import serializers

from fred.models import Failedfulfilllog, Logs

class FredFailedfulfillogSerializer(serializers.ModelSerializer):
    class Meta:
        model = Failedfulfilllog
        fields = "__all__"

class FredLogsByTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Logs
        fields = (
            "id",
            "msg",
            "recordid",
            "recordtype",
            "type",
            "userid",
            "created",
        )


class FredLogsSessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Logs
        fields = (
            "userid",
            "msg",
            "created",
        )


class FredLogsTextErrorsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Logs
        fields = (
            "type",
            "recordtype",
            "recordid",
            "msg",
            "created",
        )


class FredLogsMedSwitchSerializer(serializers.Serializer):
    recordid = serializers.CharField(allow_null=True)
    msg = serializers.CharField(allow_null=True)
    created = serializers.DateTimeField(allow_null=True)
    first_name = serializers.CharField(allow_null=True)
    last_name = serializers.CharField(allow_null=True)


class FredLogsRphQueueSerializer(serializers.Serializer):
    recordid = serializers.CharField(allow_null=True)
    msg = serializers.CharField(allow_null=True)
    created = serializers.DateTimeField(allow_null=True)
    first_name = serializers.CharField(allow_null=True)
    last_name = serializers.CharField(allow_null=True)


class FredLogsPatientNoteSerializer(serializers.Serializer):
    note = serializers.CharField(allow_blank=True, allow_null=True)


class FredLogsPaySerializer(serializers.Serializer):
    token = serializers.CharField()
    error = serializers.JSONField(required=False)

__all__ = [
    "FredFailedfulfillogSerializer",
    "FredLogsByTypeSerializer",
    "FredLogsSessionSerializer",
    "FredLogsTextErrorsSerializer",
    "FredLogsMedSwitchSerializer",
    "FredLogsRphQueueSerializer",
    "FredLogsPatientNoteSerializer",
    "FredLogsPaySerializer",
]
