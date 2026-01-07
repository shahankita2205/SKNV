import json
from django.shortcuts import render
from .models import Hooks_Queue
from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils.decorators import method_decorator
from typing import Any, Dict, Optional
from django.conf import settings
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
import logging
from .utils.hook_utils import HookQueueDuplicateManager

logger = logging.getLogger(__name__)


def create_queue_record(name, request) -> Optional[Hooks_Queue]:
    """
    Create an event record for the webhook call with duplicate checking

    Returns:
        Event instance or None if duplicate detected
    """
    if request.method == "POST":
        payload = json.loads(request.body.decode("utf-8"))
    elif request.method == "GET":
        payload = request.META["QUERY_STRING"]
    else:
        payload = {}

    # Use the utility class to create event with duplicate checking
    hdm = HookQueueDuplicateManager()
    event = hdm.create_queue_entry_with_duplicate_check(
        name=name, payload=payload, window_seconds=5
    )
    return event


@csrf_exempt
@api_view(["POST"])
@permission_classes([AllowAny])
def new_script_received(request) -> HttpResponse:
    try:
        create_queue_record(name="new-script-received", request=request)
        return HttpResponse("OK")
    except (ValueError, KeyError) as e:
        logger.error(f"Error in New Script Received: {str(e)}")
