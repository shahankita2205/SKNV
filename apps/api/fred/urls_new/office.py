"""
office URL Patterns

Contains URL patterns for office-related endpoints.
"""
from django.urls import path
from rest_framework.routers import DefaultRouter

# TODO: Import views when ready
# from fred.views.office import *

router = DefaultRouter()
# Register viewsets with router here

app_name = 'office'

urlpatterns = [
    # Add custom URL patterns here
] + router.urls
