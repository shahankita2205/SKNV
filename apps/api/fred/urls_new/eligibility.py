"""
eligibility URL Patterns

Contains URL patterns for eligibility-related endpoints.
"""
from django.urls import path
from rest_framework.routers import DefaultRouter

# TODO: Import views when ready
# from fred.views.eligibility import *

router = DefaultRouter()
# Register viewsets with router here

app_name = 'eligibility'

urlpatterns = [
    # Add custom URL patterns here
] + router.urls
