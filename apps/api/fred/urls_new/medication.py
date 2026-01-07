"""
medication URL Patterns

Contains URL patterns for medication-related endpoints.
"""
from django.urls import path
from rest_framework.routers import DefaultRouter

# TODO: Import views when ready
# from fred.views.medication import *

router = DefaultRouter()
# Register viewsets with router here

app_name = 'medication'

urlpatterns = [
    # Add custom URL patterns here
] + router.urls
