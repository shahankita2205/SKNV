"""
logs URL Patterns

Contains URL patterns for logs-related endpoints.
"""
from django.urls import path
from rest_framework.routers import DefaultRouter

from fred.views.logs import (
    FredLogsPolView,
    FredLogsSessionView,
    FredLogsTextErrorsView,
    FredLogsMedSwitchView,
    FredLogsRphQueueView,
    FredLogsPatientView,
    FredLogsPaymentView,
    FredLogsRxView,
    FredLogsRxByPatientView,
    FredLogsPayView,
)

router = DefaultRouter()
# Register viewsets with router here

app_name = 'logs'

urlpatterns = [
    path("pol/", FredLogsPolView.as_view(), name="logs_pol"),
    path("session/", FredLogsSessionView.as_view(), name="logs_session"),
    path("texterrors/", FredLogsTextErrorsView.as_view(), name="logs_texterrors"),
    path("medswitch/", FredLogsMedSwitchView.as_view(), name="logs_medswitch"),
    path("rphqueue/", FredLogsRphQueueView.as_view(), name="logs_rphqueue"),
    path("patient/<int:patient_id>/", FredLogsPatientView.as_view(), name="logs_patient"),
    path("payment/<int:payment_id>/", FredLogsPaymentView.as_view(), name="logs_payment"),
    path("rx/<int:rx_id>/", FredLogsRxView.as_view(), name="logs_rx"),
    path("getrxlogs/<int:patient_id>/", FredLogsRxByPatientView.as_view(), name="logs_rx_by_patient"),
    path("pay/", FredLogsPayView.as_view(), name="logs_pay"),
] + router.urls
