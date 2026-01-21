"""
order URL Patterns

Contains URL patterns for order-related endpoints.
"""
from django.urls import path
from rest_framework.routers import DefaultRouter

# TODO: Import views when ready
# from fred.views.order import *

router = DefaultRouter()
# Register viewsets with router here

app_name = 'order'

urlpatterns = [
    # Add custom URL patterns here
] + router.urls
