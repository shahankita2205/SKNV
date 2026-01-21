"""
payment URL Patterns

Contains URL patterns for payment-related endpoints.
"""
from django.urls import path
from rest_framework.routers import DefaultRouter

# TODO: Import views when ready
# from fred.views.payment import *

router = DefaultRouter()
# Register viewsets with router here

app_name = 'payment'

urlpatterns = [
    # Add custom URL patterns here
] + router.urls
