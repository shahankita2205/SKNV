"""
dashboard URL Patterns

Contains URL patterns for dashboard-related endpoints.
"""
from django.urls import path
from rest_framework.routers import DefaultRouter

# TODO: Import views when ready
# from fred.views.dashboard import *

router = DefaultRouter()
# Register viewsets with router here

app_name = 'dashboard'

urlpatterns = [
    # Add custom URL patterns here
] + router.urls
