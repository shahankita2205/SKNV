"""
lots URL Patterns

Contains URL patterns for lots-related endpoints.
"""
from django.urls import path
from rest_framework.routers import DefaultRouter

# TODO: Import views when ready
# from fred.views.lots import *

router = DefaultRouter()
# Register viewsets with router here

app_name = 'lots'

urlpatterns = [
    # Add custom URL patterns here
] + router.urls
