"""
Dashboard Views Module

Contains views/viewsets related to dashboard and reporting.

Legacy Controller Mapping: DashboardController

Note: This is a cross-cutting module that pulls from many domains.
"""
from datetime import timedelta
from decimal import Decimal, ROUND_HALF_UP
from zoneinfo import ZoneInfo

from django.db.models import Avg, Count, DecimalField, Exists, OuterRef, Sum
from django.db.models.functions import Cast, TruncDate, TruncMonth
from django.utils import timezone
from rest_framework.response import Response
from rest_framework.views import APIView

from fred.models import Office, Payment, Rx, Rxfill, Shipment, Task, Textsent
from fred.serializers.dashboard import (
    DashboardFulfillmentReportSerializer,
    DashboardProgramReportSerializer,
    DashboardRefillsReportSerializer,
    DashboardSmsReportSerializer,
    DashboardSumsReportSerializer,
    DashboardTrendsReportSerializer,
    DashboardTotalPaymentsReportSerializer,
    DashboardTotalRxReportSerializer,
)

EASTERN_TZ = ZoneInfo("America/New_York")
UTC = ZoneInfo("UTC")


def _count_rx(start, end=None, office_type=None, rxfill_status=None):
    """Return RX counts filtered by the given parameters."""

    qs = Rx.objects.using("fred")

    if start is not None:
        qs = qs.filter(created__gt=start)
    if end is not None:
        qs = qs.filter(created__lt=end)

    if office_type is not None:
        office_exists = Office.objects.using("fred").filter(
            id=OuterRef("officeid"),
            officetypeid_id=office_type,
        )
        qs = qs.annotate(_office_match=Exists(office_exists)).filter(
            _office_match=True
        )

    if rxfill_status is not None:
        rxfill_exists = Rxfill.objects.using("fred").filter(
            rxid=OuterRef("id"),
            status=rxfill_status,
        )
        qs = qs.annotate(_rxfill_match=Exists(rxfill_exists)).filter(
            _rxfill_match=True
        )

    return qs.count()


def _sum_payments(start, end=None, include_types=None, exclude_types=None):
    """Return payment totals filtered by the given parameters."""

    qs = Payment.objects.using("fred")

    if start is not None:
        qs = qs.filter(created__gt=start)
    if end is not None:
        qs = qs.filter(created__lt=end)

    if include_types:
        qs = qs.filter(type__in=include_types)
    if exclude_types:
        qs = qs.exclude(type__in=exclude_types)

    total = qs.aggregate(
        total=Sum(
            Cast(
                "amount",
                output_field=DecimalField(max_digits=18, decimal_places=2),
            )
        )
    )["total"]

    return total or Decimal("0.00")


def _format_money(amount):
    if amount is None:
        amount = Decimal("0.00")
    if not isinstance(amount, Decimal):
        amount = Decimal(str(amount))

    rounded = amount.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    return f"${rounded:,.2f}"


def _sms_time_range(report_type):
    now_utc = timezone.now().astimezone(UTC)

    if report_type == "24hr":
        start = now_utc - timedelta(hours=24)
        end = now_utc
    elif report_type == "thisMonth":
        start = now_utc.replace(
            day=1, hour=0, minute=0, second=0, microsecond=0
        )
        end = now_utc
    elif report_type == "lastMonth":
        this_month_start = now_utc.replace(
            day=1, hour=0, minute=0, second=0, microsecond=0
        )
        start = (this_month_start - timedelta(days=1)).replace(day=1)
        end = this_month_start - timedelta(microseconds=1)
    else:
        raise ValueError(f"Unsupported SMS report type: {report_type}")

    return start, end


def _count_sms_tasks(start, end, status=None):
    qs = Task.objects.using("fred").filter(
        type="failed-text",
        created__range=(start, end),
    )

    if status is not None:
        qs = qs.filter(status=status)

    return qs.values("id").distinct().count()


def _count_sms_texts(start, end, status=None):
    qs = Textsent.objects.using("fred").filter(
        datecreated__range=(start, end)
    )

    if status is not None:
        qs = qs.filter(status=status)

    return qs.values("id").distinct().count()


def _sms_dashboard_report(report_type):
    start, end = _sms_time_range(report_type)

    return {
        "tasksComplete": _count_sms_tasks(start, end, status="complete"),
        "tasks": _count_sms_tasks(start, end),
        "success": _count_sms_texts(start, end, status="delivered"),
        "attempted": _count_sms_texts(start, end),
    }


def _program_office_queryset(is_direct):
    qs = Office.objects.using("fred")

    if is_direct:
        return qs.filter(officetypeid_id=2)

    return qs.exclude(officetypeid_id=2).filter(officetypeid_id__isnull=False)


def _program_report(is_direct):
    office_qs = _program_office_queryset(is_direct)
    rx_qs = Rx.objects.using("fred").filter(
        officeid__in=office_qs.values("id")
    )
    rx_ids = rx_qs.values("id")

    return {
        "program": "PCDirect" if is_direct else "PCDelivers",
        "totalRx": rx_qs.count(),
        "shipped": Rxfill.objects.using("fred")
        .filter(rxid__in=rx_ids, status="shipped")
        .count(),
        "offices": office_qs.count(),
        "unpaid": Rxfill.objects.using("fred")
        .filter(rxid__in=rx_ids, status="paymentHold")
        .count(),
    }


def _trend_series(queryset, lookback):
    now_eastern = timezone.now().astimezone(EASTERN_TZ)
    today_start = now_eastern.replace(
        hour=0, minute=0, second=0, microsecond=0
    )
    start_range = (today_start - timedelta(days=lookback)).astimezone(UTC)
    end_range = (today_start + timedelta(days=1)).astimezone(UTC)

    counts = (
        queryset.filter(created__gt=start_range, created__lt=end_range)
        .annotate(day=TruncDate("created", tzinfo=EASTERN_TZ))
        .values("day")
        .annotate(total=Count("id"))
        .values_list("day", "total")
    )
    count_map = {day: total for day, total in counts}

    series = []
    for offset in range(lookback, -1, -1):
        day_start = today_start - timedelta(days=offset)
        label = day_start.strftime("%Y-%m-%d (%a)")
        series.append([label, count_map.get(day_start.date(), 0)])

    return series


def _month_start(date_value, months_back=0):
    total_months = date_value.year * 12 + (date_value.month - 1) - months_back
    year = total_months // 12
    month = total_months % 12 + 1
    return date_value.replace(
        year=year, month=month, day=1, hour=0, minute=0, second=0, microsecond=0
    )


def _sum_series(queryset, lookback):
    now_eastern = timezone.now().astimezone(EASTERN_TZ)
    this_month_start = _month_start(now_eastern)
    start_range = _month_start(this_month_start, months_back=lookback).astimezone(
        UTC
    )
    end_range = this_month_start.astimezone(UTC)

    counts = (
        queryset.filter(created__gt=start_range, created__lt=end_range)
        .annotate(month=TruncMonth("created", tzinfo=EASTERN_TZ))
        .values("month")
        .annotate(total=Count("id"))
        .values_list("month", "total")
    )
    count_map = {
        (month.year, month.month): total for month, total in counts
    }

    series = []
    for offset in range(lookback, 0, -1):
        month_start = _month_start(this_month_start, months_back=offset)
        label = month_start.strftime("'%y %b")
        series.append(
            [
                label,
                count_map.get((month_start.year, month_start.month), 0),
            ]
        )

    return series


def _compute_time_bounds():
    now_eastern = timezone.now().astimezone(EASTERN_TZ)
    today = now_eastern.replace(hour=0, minute=0, second=0, microsecond=0)
    this_month = today.replace(day=1)
    last_month = (this_month - timedelta(days=1)).replace(day=1)

    return (
        today.astimezone(UTC),
        this_month.astimezone(UTC),
        last_month.astimezone(UTC),
    )


class DashboardTotalRxReportView(APIView):
    """Dashboard endpoint that mirrors the legacy totalRxReport logic."""

    def get(self, request, *args, **kwargs):
        today_start, this_month_start, last_month_start = _compute_time_bounds()

        payload = {
            "rxToday": _count_rx(today_start),
            "rxTodayDirect": _count_rx(today_start, office_type=2),
            "rxTodayDelivers": _count_rx(today_start, office_type=1),
            "rxTodayInOffice": _count_rx(
                today_start, rxfill_status="dispensedInOffice"
            ),
            "rxThisMonth": _count_rx(this_month_start),
            "rxThisMonthDirect": _count_rx(this_month_start, office_type=2),
            "rxThisMonthDelivers": _count_rx(this_month_start, office_type=1),
            "rxThisMonthInOffice": _count_rx(
                this_month_start, rxfill_status="dispensedInOffice"
            ),
            "rxLastMonth": _count_rx(
                last_month_start, end=this_month_start
            ),
            "rxLastMonthDirect": _count_rx(
                last_month_start, end=this_month_start, office_type=2
            ),
            "rxLastMonthInOffice": _count_rx(
                last_month_start,
                end=this_month_start,
                rxfill_status="dispensedInOffice",
            ),
        }

        serializer = DashboardTotalRxReportSerializer(payload)
        return Response(serializer.data)


class DashboardTotalPaymentsReportView(APIView):
    """Dashboard endpoint that mirrors the legacy totalPaymentReport logic."""

    def get(self, request, *args, **kwargs):
        today_start, this_month_start, last_month_start = _compute_time_bounds()

        payment_today = _sum_payments(
            today_start, exclude_types=["corrector"]
        )
        payment_today_direct = _sum_payments(
            today_start, include_types=["pos", "rxportal"]
        )
        payment_today_delivers = (
            Decimal("0.00")
            if payment_today == payment_today_direct
            else payment_today - payment_today_direct
        )

        payment_this_month = _sum_payments(
            this_month_start, exclude_types=["corrector"]
        )
        payment_this_month_direct = _sum_payments(
            this_month_start, include_types=["pos", "rxportal"]
        )
        payment_this_month_delivers = (
            Decimal("0.00")
            if payment_this_month == payment_this_month_direct
            else payment_this_month - payment_this_month_direct
        )

        payment_last_month = _sum_payments(
            last_month_start,
            end=this_month_start,
            exclude_types=["corrector"],
        )
        payment_last_month_direct = _sum_payments(
            last_month_start,
            end=this_month_start,
            include_types=["pos", "rxportal"],
        )
        payment_last_month_delivers = (
            Decimal("0.00")
            if payment_last_month == payment_last_month_direct
            else payment_last_month - payment_last_month_direct
        )

        payload = {
            "paymentToday": _format_money(payment_today),
            "paymentTodayDirect": _format_money(payment_today_direct),
            "paymentTodayDelivers": _format_money(payment_today_delivers),
            "paymentThisMonth": _format_money(payment_this_month),
            "paymentThisMonthDirect": _format_money(
                payment_this_month_direct
            ),
            "paymentThisMonthDelivers": _format_money(
                payment_this_month_delivers
            ),
            "paymentLastMonth": _format_money(payment_last_month),
            "paymentLastMonthDirect": _format_money(
                payment_last_month_direct
            ),
            "paymentLastMonthDelivers": _format_money(
                payment_last_month_delivers
            ),
        }

        serializer = DashboardTotalPaymentsReportSerializer(payload)
        return Response(serializer.data)


class DashboardSmsReportView(APIView):
    """Dashboard endpoint that mirrors the legacy SMS report logic."""

    def get(self, request, *args, **kwargs):
        payload = {
            "twentyFourHours": _sms_dashboard_report("24hr"),
            "thisMonth": _sms_dashboard_report("thisMonth"),
            "lastMonth": _sms_dashboard_report("lastMonth"),
        }

        serializer = DashboardSmsReportSerializer(payload)
        return Response(serializer.data)


class DashboardRefillsReportView(APIView):
    """Dashboard endpoint that mirrors the legacy refillReport logic."""

    def get(self, request, *args, **kwargs):
        _, this_month_start, last_month_start = _compute_time_bounds()

        rx_aggregate = Rx.objects.using("fred").filter(status="ok").aggregate(
            potentialRefills=Sum("refills"),
            avgRefills=Avg("refills"),
        )
        potential_refills = rx_aggregate["potentialRefills"] or 0
        avg_refills = (
            float(rx_aggregate["avgRefills"])
            if rx_aggregate["avgRefills"] is not None
            else 0.0
        )

        refills = Rxfill.objects.using("fred").filter(type="refill")
        unpaid_refills = refills.filter(status="paymentHold")
        shipped_refills = refills.filter(status="shipped")

        shipments_this_month = Shipment.objects.using("fred").filter(
            created__gt=this_month_start
        )
        shipments_last_month = Shipment.objects.using("fred").filter(
            created__gt=last_month_start,
            created__lt=this_month_start,
        )

        payload = {
            "potentialRefills": int(potential_refills),
            "avgRefills": avg_refills,
            "totalRefills": refills.count(),
            "unpaidRefills": unpaid_refills.count(),
            "unpaidRefillsThisMonth": unpaid_refills.filter(
                created__gt=this_month_start
            ).count(),
            "unpaidRefillsLastMonth": unpaid_refills.filter(
                created__gt=last_month_start,
                created__lt=this_month_start,
            ).count(),
            "shippedRefills": shipped_refills.count(),
            "shippedRefillsThisMonth": shipped_refills.filter(
                shipmentid__in=shipments_this_month.values("id")
            ).count(),
            "shippedRefillsLastMonth": shipped_refills.filter(
                shipmentid__in=shipments_last_month.values("id")
            ).count(),
        }

        serializer = DashboardRefillsReportSerializer(payload)
        return Response(serializer.data)


class DashboardProgramReportView(APIView):
    """Dashboard endpoint that mirrors the legacy programReport logic."""

    def get(self, request, *args, **kwargs):
        payload = {
            "pcdelivers": _program_report(False),
            "pcdirect": _program_report(True),
        }

        serializer = DashboardProgramReportSerializer(payload)
        return Response(serializer.data)


class DashboardFulfillmentReportView(APIView):
    """Dashboard endpoint that mirrors the legacy fulfillmentReport logic."""

    def get(self, request, *args, **kwargs):
        rxfill_qs = Rxfill.objects.using("fred")

        payload = {
            "toFill": rxfill_qs.filter(status="toFill").count(),
            "inFill": rxfill_qs.filter(status="inFill").count(),
            "shipped": rxfill_qs.filter(status="shipped")
            .exclude(type="corrector")
            .count(),
            "inNS": rxfill_qs.filter(nsso__isnull=False).count(),
        }

        serializer = DashboardFulfillmentReportSerializer(payload)
        return Response(serializer.data)


class DashboardTrendsReportView(APIView):
    """Dashboard endpoint that combines legacy trend reports."""

    def get(self, request, *args, **kwargs):
        lookback = 60
        rx_qs = Rx.objects.using("fred")
        payment_qs = Payment.objects.using("fred")
        shipment_qs = Shipment.objects.using("fred")

        payload = {
            "rx": _trend_series(rx_qs, lookback),
            "shipments": _trend_series(shipment_qs, lookback),
            "payments": _trend_series(payment_qs, lookback),
        }

        serializer = DashboardTrendsReportSerializer(payload)
        return Response(serializer.data)


class DashboardSumsReportView(APIView):
    """Dashboard endpoint that combines legacy sum reports."""

    def get(self, request, *args, **kwargs):
        lookback = 18
        rx_qs = Rx.objects.using("fred")
        payment_qs = Payment.objects.using("fred")
        shipment_qs = Shipment.objects.using("fred")

        payload = {
            "rx": _sum_series(rx_qs, lookback),
            "shipments": _sum_series(shipment_qs, lookback),
            "payments": _sum_series(payment_qs, lookback),
        }

        serializer = DashboardSumsReportSerializer(payload)
        return Response(serializer.data)


__all__ = [
    "DashboardTotalRxReportView",
    "DashboardTotalPaymentsReportView",
    "DashboardSmsReportView",
    "DashboardRefillsReportView",
    "DashboardProgramReportView",
    "DashboardFulfillmentReportView",
    "DashboardTrendsReportView",
    "DashboardSumsReportView",
]
