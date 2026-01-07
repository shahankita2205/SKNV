"""
user URL Patterns

Contains URL patterns for user-related endpoints.
"""
from django.urls import path
from rest_framework.routers import DefaultRouter

# TODO: Import views when ready
# from fred.views.user import *

router = DefaultRouter()
# Register viewsets with router here

app_name = 'user'

urlpatterns = [
    # Add custom URL patterns here
] + router.urls
