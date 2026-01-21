"""
communication URL Patterns

Contains URL patterns for communication-related endpoints.
"""
from django.urls import path
from rest_framework.routers import DefaultRouter

# TODO: Import views when ready
# from fred.views.communication import *

router = DefaultRouter()
# Register viewsets with router here

app_name = 'communication'

urlpatterns = [
    # Add custom URL patterns here
] + router.urls
