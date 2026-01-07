"""
inventory URL Patterns

Contains URL patterns for inventory-related endpoints.
"""
from django.urls import path
from rest_framework.routers import DefaultRouter

# TODO: Import views when ready
# from fred.views.inventory import *

router = DefaultRouter()
# Register viewsets with router here

app_name = 'inventory'

urlpatterns = [
    # Add custom URL patterns here
] + router.urls
