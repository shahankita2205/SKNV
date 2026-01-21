"""
doctor URL Patterns

Contains URL patterns for doctor-related endpoints.
"""

from django.urls import path
from rest_framework.routers import DefaultRouter

# TODO: Import views when ready
# from fred.views.doctor import *

router = DefaultRouter()
# Register viewsets with router here

app_name = "doctor"

urlpatterns = [
    # Add custom URL patterns here
] + router.urls
