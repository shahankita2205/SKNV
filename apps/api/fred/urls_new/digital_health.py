"""
digital health URL Patterns

Contains URL patterns for digital health-related endpoints.
"""
from django.urls import path
from rest_framework.routers import DefaultRouter

# TODO: Import views when ready
# from fred.views.digital_health import *

router = DefaultRouter()
# Register viewsets with router here

app_name = 'digital_health'

urlpatterns = [
    # Add custom URL patterns here
] + router.urls
