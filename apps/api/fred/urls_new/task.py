"""
task URL Patterns

Contains URL patterns for task-related endpoints.
"""
from django.urls import path
from rest_framework.routers import DefaultRouter

# TODO: Import views when ready
# from fred.views.task import *

router = DefaultRouter()
# Register viewsets with router here

app_name = 'task'

urlpatterns = [
    # Add custom URL patterns here
] + router.urls
