"""
reference URL Patterns

Contains URL patterns for reference-related endpoints.
"""
from django.urls import path
from rest_framework.routers import DefaultRouter

# TODO: Import views when ready
# from fred.views.reference import *

router = DefaultRouter()
# Register viewsets with router here

app_name = 'reference'

urlpatterns = [
    # Add custom URL patterns here
] + router.urls
