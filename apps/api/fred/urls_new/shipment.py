"""
shipment URL Patterns

Contains URL patterns for shipment-related endpoints.
"""
from django.urls import path
from rest_framework.routers import DefaultRouter

# TODO: Import views when ready
# from fred.views.shipment import *

router = DefaultRouter()
# Register viewsets with router here

app_name = 'shipment'

urlpatterns = [
    # Add custom URL patterns here
] + router.urls
