"""
customer service URL Patterns

Contains URL patterns for customer service-related endpoints.
"""
from django.urls import path
from rest_framework.routers import DefaultRouter

# TODO: Import views when ready
# from fred.views.customer_service import *

router = DefaultRouter()
# Register viewsets with router here

app_name = 'customer_service'

urlpatterns = [
    # Add custom URL patterns here
] + router.urls
