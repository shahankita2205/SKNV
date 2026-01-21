"""
Logs Views Module

Contains views/viewsets related to audit and logging.

Legacy Controller Mapping: LogsController, FailedfulfilllogController
"""
import os
from datetime import timedelta

from django.conf import settings
from django.utils import timezone
from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Exists, OuterRef, Subquery, IntegerField
from django.db.models.functions import Cast
from django.db.models.fields import CharField
import logging

import json

from fred.models import Failedfulfilllog, Logs, Logspatient, Logsrx, Rx, Rxfill, Token, Users
from fred.serializers import (
    FredFailedfulfillogSerializer,
    FredLogsByTypeSerializer,
    FredLogsSessionSerializer,
    FredLogsTextErrorsSerializer,
    FredLogsMedSwitchSerializer,
    FredLogsRphQueueSerializer,
    FredLogsPatientNoteSerializer,
    FredLogsPaySerializer,
)
from fred.views import StandardResultsSetPagination

logger = logging.getLogger(__name__)


class FredLogsView(generics.ListAPIView):
    """
    List logs filtered by type.

    Migrated from: LogsController::getAction()
    """

    serializer_class = FredLogsByTypeSerializer
    pagination_class = None

    def get_queryset(self):
        log_type = self.request.query_params.get("type")
        if not log_type:
            log_type = ""
        return (
            Logs.objects.using("fred")
            .filter(type=log_type)
            .order_by("-id")
        )


class FredLogsPolView(APIView):
    """
    Health check for logs service.

    Migrated from: LogsController::getPolLogsAction()
    """

    def get(self, request, *args, **kwargs):
        forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR", "")
        if forwarded_for:
            ip_address = forwarded_for.split(",")[0].strip()
        else:
            ip_address = request.META.get("REMOTE_ADDR", "")

        version = (
            getattr(settings, "APP_VER", None)
            or getattr(settings, "APP_VERSION", None)
            or os.getenv("APP_VER", "")
        )

        return Response(
            {
                "connected": True,
                "environment": settings.ENVIRONMENT,
                "version": version,
                "ipAddress": ip_address,
            }
        )


class FredLogsSessionView(generics.ListAPIView):
    """
    List recent session logs.

    Migrated from: LogsController::getSessionLogsAction()
    """

    serializer_class = FredLogsSessionSerializer
    pagination_class = None

    def get_queryset(self):
        ts = timezone.now() - timedelta(hours=1)
        return (
            Logs.objects.using("fred")
            .filter(
                type="app",
                recordtype="user",
                msg__icontains="signed i",
                created__gt=ts,
            )
            .order_by("-id")
        )


class FredLogsTextErrorsView(generics.ListAPIView):
    """
    List recent text error logs.

    Migrated from: LogsController::getTextErrors()
    """

    serializer_class = FredLogsTextErrorsSerializer
    pagination_class = None

    def get_queryset(self):
        ts = timezone.now() - timedelta(days=30)
        return (
            Logs.objects.using("fred")
            .filter(
                msg__icontains="text error",
                created__gt=ts,
            )
            .order_by("-id")
        )


class FredLogsMedSwitchView(generics.ListAPIView):
    """
    List medication switch logs with user names.

    Migrated from: LogsController::getMedSwitchLogs()
    """

    serializer_class = FredLogsMedSwitchSerializer
    pagination_class = None

    def get_queryset(self):
        users_qs = Users.objects.using("fred").filter(
            id=OuterRef("userid_int")
        )

        return (
            Logs.objects.using("fred")
            .annotate(
                userid_int=Cast("userid", output_field=IntegerField()),
                first_name=Subquery(users_qs.values("first_name")[:1]),
                last_name=Subquery(users_qs.values("last_name")[:1]),
            )
            .filter(
                type="hipaa",
                recordtype="rx",
                msg__startswith="Changed medication from ",
            )
            .order_by("-id")
        )


class FredLogsRphQueueView(generics.ListAPIView):
    """
    List RPh queue logs with user names.

    Migrated from: LogsController::getRPhQueueLogsAction()
    """

    serializer_class = FredLogsRphQueueSerializer
    pagination_class = None

    def get_queryset(self):
        users_qs = Users.objects.using("fred").filter(
            id=OuterRef("userid_int")
        )

        return (
            Logs.objects.using("fred")
            .annotate(
                userid_int=Cast("userid", output_field=IntegerField()),
                first_name=Subquery(users_qs.values("first_name")[:1]),
                last_name=Subquery(users_qs.values("last_name")[:1]),
            )
            .filter(
                type="hipaa",
                recordtype="rx",
                msg__endswith="RPh Queue",
            )
            .order_by("-id")
        )


class FredLogsPatientView(APIView):
    """
    List logs for a patient with user names.

    Migrated from: LogsController::getPatientLogsAction()
    """

    def get(self, request, patient_id, *args, **kwargs):
        logs = list(
            Logspatient.objects.using("fred").filter(patientid=patient_id)
        )
        user_ids = set()
        for log in logs:
            if not log.userid or log.userid == "SYS":
                continue
            user_id = str(log.userid).strip()
            if user_id.isdigit():
                user_ids.add(int(user_id))

        users = (
            Users.objects.using("fred")
            .filter(id__in=user_ids)
            .values("id", "first_name", "last_name")
        )
        user_map = {}
        for user in users:
            name_parts = [user.get("first_name") or "", user.get("last_name") or ""]
            name = " ".join(part for part in name_parts if part).strip()
            if name:
                user_map[str(user["id"])] = name

        payload = []
        for log in logs:
            name = "SYS"
            if log.userid and log.userid != "SYS":
                name = user_map.get(str(log.userid).strip(), "SYS")

            payload.append([log.created, name, log.msg])

        return Response(payload)

    def post(self, request, patient_id, *args, **kwargs):
        serializer = FredLogsPatientNoteSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        note = serializer.validated_data.get("note") or ""
        user_id = getattr(request.user, "id", None)
        if not user_id:
            user_id = "SYS"

        created_at = timezone.now()
        msg = f"User note: {note}"

        try:
            Logs.objects.using("fred").create(
                userid=str(user_id),
                recordid=str(patient_id),
                recordtype="patient",
                msg=msg,
                type="note",
                created=created_at,
            )
            Logspatient.objects.using("fred").create(
                userid=str(user_id),
                patientid=patient_id,
                msg=msg,
                created=created_at,
            )
        except Exception:
            logger.exception("Failed to create patient note log")
            return Response(False, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        logger.info(
            "[UID %s][RID %s][TYPE note] %s",
            user_id,
            patient_id,
            msg,
        )
        return Response(True)


class FredLogsPaymentView(APIView):
    """
    List logs for a payment with user names.

    Migrated from: LogsController::getPaymentLogsAction()
    """

    def get(self, request, payment_id, *args, **kwargs):
        logs = list(
            Logs.objects.using("fred").filter(
                recordid=payment_id,
                recordtype="payment",
            )
        )
        user_ids = set()
        for log in logs:
            if not log.userid or log.userid == "SYS":
                continue
            user_id = str(log.userid).strip()
            if user_id.isdigit():
                user_ids.add(int(user_id))

        users = (
            Users.objects.using("fred")
            .filter(id__in=user_ids)
            .values("id", "first_name", "last_name")
        )
        user_map = {}
        for user in users:
            name_parts = [user.get("first_name") or "", user.get("last_name") or ""]
            name = " ".join(part for part in name_parts if part).strip()
            if name:
                user_map[str(user["id"])] = name

        payload = []
        for log in logs:
            name = "SYS"
            if log.userid and log.userid != "SYS":
                name = user_map.get(str(log.userid).strip(), "SYS")

            payload.append([log.created, name, log.msg])

        return Response(payload)

    def post(self, request, payment_id, *args, **kwargs):
        serializer = FredLogsPatientNoteSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        note = serializer.validated_data.get("note") or ""
        user_id = getattr(request.user, "id", None)
        if not user_id:
            user_id = "SYS"

        created_at = timezone.now()
        msg = f"User note: {note}"

        try:
            Logs.objects.using("fred").create(
                userid=str(user_id),
                recordid=str(payment_id),
                recordtype="payment",
                msg=msg,
                type="note",
                created=created_at,
            )
        except Exception:
            logger.exception("Failed to create payment note log")
            return Response(False, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        logger.info(
            "[UID %s][RID %s][TYPE note] %s",
            user_id,
            payment_id,
            msg,
        )
        return Response(True)


class FredLogsRxView(APIView):
    """
    List logs for an RX with user names.

    Migrated from: LogsController::getRxLogsAction()
    """

    def get(self, request, rx_id, *args, **kwargs):
        logs = list(Logsrx.objects.using("fred").filter(rxid=rx_id))
        user_ids = set()
        for log in logs:
            if not log.userid or log.userid == "SYS":
                continue
            user_id = str(log.userid).strip()
            if user_id.isdigit():
                user_ids.add(int(user_id))

        users = (
            Users.objects.using("fred")
            .filter(id__in=user_ids)
            .values("id", "first_name", "last_name")
        )
        user_map = {}
        for user in users:
            name_parts = [user.get("first_name") or "", user.get("last_name") or ""]
            name = " ".join(part for part in name_parts if part).strip()
            if name:
                user_map[str(user["id"])] = name

        payload = []
        for log in logs:
            name = "SYS"
            if log.userid and log.userid != "SYS":
                name = user_map.get(str(log.userid).strip(), "SYS")

            payload.append([log.created, name, log.msg])

        return Response(payload)

    def post(self, request, rx_id, *args, **kwargs):
        serializer = FredLogsPatientNoteSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        note = serializer.validated_data.get("note") or ""
        user_id = getattr(request.user, "id", None)
        if not user_id:
            user_id = "SYS"

        created_at = timezone.now()
        msg = f"User note: {note}"

        try:
            Logs.objects.using("fred").create(
                userid=str(user_id),
                recordid=str(rx_id),
                recordtype="rx",
                msg=msg,
                type="note",
                created=created_at,
            )
            Logsrx.objects.using("fred").create(
                userid=str(user_id),
                rxid=rx_id,
                msg=msg,
                created=created_at,
            )
        except Exception:
            logger.exception("Failed to create rx note log")
            return Response(False, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        logger.info(
            "[UID %s][RID %s][TYPE note] %s",
            user_id,
            rx_id,
            msg,
        )
        return Response(True)


class FredLogsRxByPatientView(APIView):
    """
    List RX logs and notes for a patient.

    Migrated from: LogsController::getRxLogsByPatientIdAction()
    """

    def get(self, request, patient_id, *args, **kwargs):
        try:
            rxs = list(
                Rx.objects.using("fred")
                .filter(patientid=patient_id)
                .order_by("id")
            )
            if not rxs:
                return Response([])

            rx_ids = [rx.id for rx in rxs if rx.id is not None]
            logs = list(
                Logsrx.objects.using("fred").filter(rxid__in=rx_ids)
            )
            user_ids = set()
            for log in logs:
                if not log.userid or log.userid == "SYS":
                    continue
                user_id = str(log.userid).strip()
                if user_id.isdigit():
                    user_ids.add(int(user_id))

            users = (
                Users.objects.using("fred")
                .filter(id__in=user_ids)
                .values("id", "first_name", "last_name")
            )
            user_map = {}
            for user in users:
                name_parts = [user.get("first_name") or "", user.get("last_name") or ""]
                name = " ".join(part for part in name_parts if part).strip()
                if name:
                    user_map[str(user["id"])] = name

            logs_by_rx = {}
            for log in logs:
                name = "SYS"
                if log.userid and log.userid != "SYS":
                    name = user_map.get(str(log.userid).strip(), "SYS")
                logs_by_rx.setdefault(log.rxid, []).append(
                    [log.created, name, log.msg]
                )

            all_logs = []
            for rx in rxs:
                rx_id = rx.id
                if rx_id is None:
                    continue

                rx_note = rx.notes
                if rx_note:
                    all_logs.append(
                        [rx_id, timezone.now(), "Rx Note", rx_note]
                    )

                for log in logs_by_rx.get(rx_id, []):
                    all_logs.append([rx_id] + log)

            return Response(all_logs)
        except Exception:
            logger.exception("Error fetching Rx logs by patient id")
            return Response([])


class FredLogsPayView(APIView):
    """
    Log payment client errors from Square callbacks.

    Migrated from: LogsController::logPayAction()
    """

    def post(self, request, *args, **kwargs):
        serializer = FredLogsPaySerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        token_value = serializer.validated_data["token"]
        error_payload = serializer.validated_data.get("error")

        token = (
            Token.objects.using("fred").filter(token=token_value).first()
        )
        if token and error_payload is not None:
            created_at = timezone.now()
            msg = f"Client Error: {json.dumps(error_payload)}"
            try:
                Logs.objects.using("fred").create(
                    userid="SYS",
                    recordid=str(token.token),
                    recordtype="payment",
                    msg=msg,
                    type="square",
                    created=created_at,
                )
            except Exception:
                logger.exception("Failed to create payment error log")
                return Response(["ok"], status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            logger.info(
                "[UID SYS][RID %s][TYPE square] %s",
                token.token,
                msg,
            )

        return Response(["ok"])


class FredFailedfulfillogView(generics.ListCreateAPIView):
    """
    List and Create view for Failed Fulfillment Logs
    
    Migrated from: FailedfulfilllogController
    """
    queryset = Failedfulfilllog.objects.all().using("fred")
    serializer_class = FredFailedfulfillogSerializer
    pagination_class = StandardResultsSetPagination
    
    def get_queryset(self):
        ffp = self.request.query_params.get('ffp')
        active_param = self.request.query_params.get('active')
        
        if ffp is None and active_param is None:
            return Failedfulfilllog.objects.using("fred")
        
        try:
            queryset = Failedfulfilllog.objects.using("fred")
            
            if ffp:
                queryset = queryset.filter(fulfillmentpartner__icontains=ffp)
            
            if active_param:
                active = active_param.lower() in ['true', '1', 'yes']
                
                if active:
                    matching_rxfills = Rxfill.objects.using("fred").annotate(
                        id_as_string=Cast('id', output_field=CharField())
                    ).filter(
                        id_as_string=OuterRef('rxfillid'),
                        status='other'
                    )
                else:
                    matching_rxfills = Rxfill.objects.using("fred").annotate(
                        id_as_string=Cast('id', output_field=CharField())
                    ).filter(
                        id_as_string=OuterRef('rxfillid')
                    ).exclude(status='other')
                
                queryset = queryset.annotate(
                    has_matching_rxfill=Exists(matching_rxfills)
                ).filter(has_matching_rxfill=True)
            
            return queryset
            
        except Exception as e:
            logger.error(f"Error fetching filtered failed fulfillment logs: {str(e)}", exc_info=True)
            return Failedfulfilllog.objects.none()


class FredFailedfulfillogDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, Update, and Delete view for Failed Fulfillment Logs
    """
    queryset = Failedfulfilllog.objects.all().using("fred")
    serializer_class = FredFailedfulfillogSerializer


__all__ = [
    "FredLogsView",
    "FredLogsPolView",
    "FredLogsSessionView",
    "FredLogsTextErrorsView",
    "FredLogsMedSwitchView",
    "FredLogsRphQueueView",
    "FredLogsPatientView",
    "FredLogsPaymentView",
    "FredLogsRxView",
    "FredLogsRxByPatientView",
    "FredLogsPayView",
    "FredFailedfulfillogView",
    "FredFailedfulfillogDetailView",
]
