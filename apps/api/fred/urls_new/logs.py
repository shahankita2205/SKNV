"""
logs URL Patterns

Contains URL patterns for logs-related endpoints.
"""
from django.urls import path
from rest_framework.routers import DefaultRouter

# TODO: Import views when ready
# from fred.views.logs import *

router = DefaultRouter()
# Register viewsets with router here

app_name = 'logs'

urlpatterns = [
    # Add custom URL patterns here
] + router.urls
