from collections import defaultdict
from datetime import timedelta
from decimal import Decimal, InvalidOperation

import requests
from django.conf import settings
from django.http import JsonResponse
from django.utils import timezone
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import authenticate
from .models import User
from .permissions import HasRole
import posthog
from fred.models import Office, Payment, Rx, Rxfill

QUICK_RANGES = [
    {"id": "24h", "label": "24 hours"},
    {"id": "7d", "label": "7 days"},
    {"id": "30d", "label": "30 days"},
]

PRESCRIPTION_SECTION_BASE = {
    "id": "prescriptions",
    "title": "Prescriptions",
    "description": "Inbound scripts and refill requests by channel",
}

PAYMENT_SECTION_BASE = {
    "id": "payments",
    "title": "Payments",
    "description": "Cleared encounters and patient responsibility",
}

SOURCE_LABELS = ("PC Direct", "PC Delivers", "In-Office")
PAYMENT_SOURCE_LABELS = ("PC Direct", "PC Delivers")

TIMEFRAME_CONFIG = {
    "24h": {
        "duration": timedelta(hours=24),
        "comparison": "Prior 24h",
        "change_suffix": "vs prior day",
    },
    "7d": {
        "duration": timedelta(days=7),
        "comparison": "Prior 7 days",
        "change_suffix": "vs prior week",
    },
    "30d": {
        "duration": timedelta(days=30),
        "comparison": "Prior 30 days",
        "change_suffix": "vs prior 30 days",
    },
}


def _zeroed_source_values():
    return {range_info["id"]: 0 for range_info in QUICK_RANGES}


def _format_change_and_trend(
    current_value, previous_value, suffix, *, previous_has_activity=False, comparison_value=None
):
    baseline = comparison_value if comparison_value is not None else previous_value
    if baseline == 0:
        if current_value == 0:
            return f"No change {suffix}", "up"
        if previous_has_activity:
            trend = "up" if current_value >= 0 else "down"
            return f"Net zero prior period {suffix}", trend
        return f"New volume {suffix}", "up"

    difference = current_value - previous_value
    percent_change = (difference / baseline) * 100
    trend = "up" if percent_change >= 0 else "down"
    return f"{percent_change:+.1f}% {suffix}", trend


def _build_prescription_section():
    now = timezone.now()
    timeframe_data = {}
    source_total_by_label = {label: _zeroed_source_values() for label in SOURCE_LABELS}
    pc_direct_office_ids = set(
        Office.objects.filter(officetypeid=2).values_list("id", flat=True)
    )
    pc_delivers_office_ids = set(
        Office.objects.filter(officetypeid=1).values_list("id", flat=True)
    )
    tracked_office_ids = pc_direct_office_ids | pc_delivers_office_ids

    for range_info in QUICK_RANGES:
        range_id = range_info["id"]
        config = TIMEFRAME_CONFIG.get(range_id)
        if not config:
            continue

        duration = config["duration"]
        current_start = now - duration
        previous_start = current_start - duration

        current_qs = Rx.objects.filter(created__gte=current_start, created__lt=now)
        previous_qs = Rx.objects.filter(
            created__gte=previous_start, created__lt=current_start
        )

        current_total = current_qs.count()
        previous_total = previous_qs.count()
        change_text, trend = _format_change_and_trend(
            current_total, previous_total, config["change_suffix"]
        )

        timeframe_data[range_id] = {
            "value": current_total,
            "change": change_text,
            "trend": trend,
            "comparison": config["comparison"],
        }

        if current_total == 0:
            in_office_rx_ids = []
        else:
            in_office_rx_ids = list(
                Rxfill.objects.filter(
                    status="dispensedInOffice",
                    rxid__in=current_qs.values_list("id", flat=True),
                )
                .values_list("rxid", flat=True)
                .distinct()
            )
        source_total_by_label["In-Office"][range_id] = len(in_office_rx_ids)

        non_in_office_qs = current_qs.exclude(id__in=in_office_rx_ids)
        pc_direct_count = non_in_office_qs.filter(
            officeid__in=pc_direct_office_ids
        ).count()
        pc_delivers_count = non_in_office_qs.filter(
            officeid__in=pc_delivers_office_ids
        ).count()
        other_count = non_in_office_qs.exclude(officeid__in=tracked_office_ids).count()
        source_total_by_label["PC Direct"][range_id] = pc_direct_count
        source_total_by_label["PC Delivers"][range_id] = (
            pc_delivers_count + other_count
        )

    sources = [
        {"label": label, "values": values}
        for label, values in source_total_by_label.items()
    ]

    return {
        **PRESCRIPTION_SECTION_BASE,
        "timeframeData": timeframe_data,
        "sources": sources,
    }


def _safe_decimal(value):
    if value is None:
        return Decimal("0")
    if isinstance(value, Decimal):
        return value
    try:
        return Decimal(str(value))
    except (InvalidOperation, ValueError, TypeError):
        return Decimal("0")


def _decimal_to_number(value):
    return float(value)


def _build_payment_section():
    now = timezone.now()
    timeframe_data = {}
    source_totals = {label: _zeroed_source_values() for label in PAYMENT_SOURCE_LABELS}
    pc_direct_types = {"pos", "rxportal"}

    for range_info in QUICK_RANGES:
        range_id = range_info["id"]
        config = TIMEFRAME_CONFIG.get(range_id)
        if not config:
            continue

        duration = config["duration"]
        current_start = now - duration
        previous_start = current_start - duration

        current_rows = list(
            Payment.objects.filter(created__gte=current_start, created__lt=now).values_list(
                "type", "amount"
            )
        )
        previous_rows = list(
            Payment.objects.filter(created__gte=previous_start, created__lt=current_start).values_list(
                "type", "amount"
            )
        )

        current_entries = [
            (payment_type, _safe_decimal(amount)) for payment_type, amount in current_rows
        ]
        previous_amounts = [_safe_decimal(amount) for _, amount in previous_rows]

        current_total = sum((amount for _, amount in current_entries), Decimal("0"))
        previous_total = sum(previous_amounts, Decimal("0"))
        previous_volume = sum((abs(amount) for amount in previous_amounts), Decimal("0"))
        comparison_baseline = (
            previous_total if previous_total != 0 else previous_volume
        )

        change_text, trend = _format_change_and_trend(
            current_total,
            previous_total,
            config["change_suffix"],
            previous_has_activity=bool(previous_rows),
            comparison_value=comparison_baseline if comparison_baseline != 0 else None,
        )

        timeframe_data[range_id] = {
            "value": _decimal_to_number(current_total),
            "change": change_text,
            "trend": trend,
            "comparison": config["comparison"],
        }

        for payment_type, amount in current_entries:
            normalized_type = (payment_type or "").lower()
            label = (
                "PC Direct" if normalized_type in pc_direct_types else "PC Delivers"
            )
            source_totals[label][range_id] += _decimal_to_number(amount)

    sources = [
        {"label": label, "values": values} for label, values in source_totals.items()
    ]

    return {
        **PAYMENT_SECTION_BASE,
        "timeframeData": timeframe_data,
        "sources": sources,
    }


def index(request):
    return JsonResponse({})


def get_status(request):
    test_flag = posthog.feature_enabled(
        "test", "anonymous" if request.user.is_anonymous else request.user.email
    )
    return JsonResponse({"status": "success", "features": {"test": bool(test_flag)}})


@api_view(["POST"])
@permission_classes([AllowAny])
def register(request):
    email = request.data.get("email")
    password = request.data.get("password")

    if not email or not password:
        return Response(
            {"error": "Email and password are required."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    if User.objects.filter(email=email).exists():
        return Response(
            {"error": "Email already exists."}, status=status.HTTP_400_BAD_REQUEST
        )

    user = User.objects.create_user(email=email, password=password)
    token, created = Token.objects.get_or_create(user=user)

    return Response({"token": token.key}, status=status.HTTP_201_CREATED)


@api_view(["POST"])
@permission_classes([AllowAny])
def login(request):
    email = request.data.get("email")
    password = request.data.get("password")

    if not email or not password:
        return Response(
            {"error": "Email and password are required."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    user = authenticate(email=email, password=password)

    if not user:
        # Try Fred login
        try:
            fred_response = requests.post(
                f"{settings.FRED_API}/login",
                json={"email": email, "pass": password},
            )
            if fred_response.status_code == 200:
                fred_user = fred_response.json().get("data").get("user")
                if fred_user:
                    user = User.objects.create_user(email=email, password=password)
                    user.first_name = fred_user.get("first_name", "")
                    user.last_name = fred_user.get("last_name", "")
                    user.save()
                    token, _ = Token.objects.get_or_create(user=user)
                    return Response({"token": token.key})
        except Exception:
            pass
        return Response(
            {"error": "Invalid credentials."},
            status=status.HTTP_401_UNAUTHORIZED,
        )

    token, _ = Token.objects.get_or_create(user=user)
    return Response({"token": token.key})


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def logout(request):
    request.user.auth_token.delete()
    return Response({"detail": "Successfully logged out."}, status=status.HTTP_200_OK)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def me(request):
    user = request.user
    navigation = [
        {
            "section": "Dashboard",
            "links": [
                {"label": "Overview", "href": "/", "icon": "layout-dashboard"},
                {"label": "Reports", "href": "/reports", "icon": "line-chart"},
                {"label": "Tasks", "href": "/tasks", "icon": "check"},
            ],
        },
        {
            "section": "Manage",
            "links": [
                {"label": "Offices", "href": "/offices", "icon": "building"},
                {"label": "Doctors", "href": "/doctors", "icon": "stethoscope"},
            ],
        },
    ]
    return Response(
        {
            "id": user.id,
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "navigation": navigation,
        },
        status=status.HTTP_200_OK,
    )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def stats(request):
    """Return dashboard metric data for prescriptions and payments."""

    metrics = [
        _build_prescription_section(),
        _build_payment_section(),
    ]
    return Response({"ranges": QUICK_RANGES, "metrics": metrics})


@api_view(["GET"])
@permission_classes([IsAuthenticated, HasRole])
def test(request):
    test.allowed_roles = ["admin"]
    return JsonResponse(
        {"message": "Test endpoint is working."}, status=status.HTTP_200_OK
    )
