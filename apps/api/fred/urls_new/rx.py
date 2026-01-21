"""
rx URL Patterns

Contains URL patterns for rx-related endpoints.
"""
from django.urls import path
from rest_framework.routers import DefaultRouter

# TODO: Import views when ready
# from fred.views.rx import *

router = DefaultRouter()
# Register viewsets with router here

app_name = 'rx'

urlpatterns = [
    # Add custom URL patterns here
] + router.urls
