"""
vi URL Patterns

Contains URL patterns for vi-related endpoints.
"""
from django.urls import path
from rest_framework.routers import DefaultRouter

# TODO: Import views when ready
# from fred.views.vi import *

router = DefaultRouter()
# Register viewsets with router here

app_name = 'vi'

urlpatterns = [
    # Add custom URL patterns here
] + router.urls
