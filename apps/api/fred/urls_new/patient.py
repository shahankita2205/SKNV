"""
Patient URL Patterns

Contains URL patterns for patient-related endpoints.
"""
from django.urls import path
from rest_framework.routers import DefaultRouter

# TODO: Import views when ready
# from fred.views.patient import PatientViewSet

router = DefaultRouter()
# router.register(r'', PatientViewSet, basename='patient')

app_name = 'patient'

urlpatterns = [
    # Add custom URL patterns here
] + router.urls
