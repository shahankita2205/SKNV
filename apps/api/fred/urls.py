from django.urls import path
from .views import (
    DioItemsSkuView,
    FredAddressView,
    FredAddressDetailView,
    FredAllergensView,
    FredAllergensDetailView,
    FredAuditTableView,
    FredAuditTableDetailView,
    FredAutomatedtasksView,
    FredAutomatedtasksDetailView,
    FredDeletedofficeView,
    FredDeletedofficeDetailView,
    FredDeviceView,
    FredDeviceDetailView,
    FredDioItemsView,
    FredDioItemsDetailView,
    FredDispenselogsView,
    FredDispenselogsDetailView,
    FredFailedfulfillogView,
    FredFailedfulfillogDetailView,
    FredFaqView,
    FredFaqDetailView,
    FredFeatureflagView,
    FredFeatureflagDetailView,
    FredFeeView,
    FredFeeDetailView,
    FredFulfillmentpartnersView,
    FredFulfillmentpartnersDetailView,
    FredIhflogsView,
    FredIhflogsDetailView,
    FredIngredientView,
    FredIngredientDetailView,
    FredInhouseeligibilityView,
    FredInhouseeligibilityDetailView,
    FredInventoryView,
    FredInventoryDetailView,
    FredLogsView,
    FredLogsDetailView,
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
    FredLogspatientView,
    FredLogspatientDetailView,
    FredLogsrxView,
    FredLogsrxDetailView,
    FredLotsView,
    FredLotsDetailView,
    FredMedalignmentsView,
    FredMedalignmentsDetailView,
    FredMedicationView,
    FredMedicationDetailView,
    FredMedleafletView,
    FredMedleafletDetailView,
    FredOfficeView,
    FredOfficeDetailView,
    FredOfficeagreementtypeView,
    FredOfficeagreementtypeDetailView,
    FredOfficehistoryView,
    FredOfficehistoryDetailView,
    FredOfficeinfoView,
    FredOfficeinfoDetailView,
    FredOfficetypeView,
    FredOfficetypeDetailView,
    FredOthermedicationView,
    FredOthermedicationDetailView,
    FredOutofstockmedicationView,
    FredOutofstockmedicationDetailView,
    FredPatientView,
    FredPatientDetailView,
    FredPatientlogsView,
    FredPatientlogsDetailView,
    FredPatientmetaView,
    FredPatientmetaDetailView,
    FredPatientOutreachView,
    FredPatientOutreachDetailView,
    FredPaymentView,
    FredPaymentDetailView,
    FredPaymentsnotapprovedView,
    FredPaymentsnotapprovedDetailView,
    FredPcdAgreementView,
    FredPcdAgreementDetailView,
    FredPcdFormularyAgreementView,
    FredPcdFormularyAgreementDetailView,
    FredPcdInboundNdcView,
    FredPcdInboundNdcDetailView,
    FredPcdNormalizedDrugGroupView,
    FredPcdNormalizedDrugGroupDetailView,
    FredPrepaidView,
    FredPrepaidDetailView,
    FredRxView,
    FredRxDetailView,
    FredRxfillView,
    FredRxfillDetailView,
    FredRxprintView,
    FredRxprintDetailView,
    FredRxrawView,
    FredRxrawDetailView,
    FredShipmentView,
    FredShipmentDetailView,
    FredSkincarepairingsView,
    FredSkincarepairingsDetailView,
    FredStateView,
    FredStateDetailView,
    FredSubstatusView,
    FredSubstatusDetailView,
    FredTaskView,
    FredTaskDetailView,
    FredTextsentView,
    FredTextsentDetailView,
    FredTokenView,
    FredTokenDetailView,
    FredUpdatedskusView,
    FredUpdatedskusDetailView,
    UserListView,
    UserDetailView,
    UserAddView,
    UserLogsView,
    SalesPerformanceView,
    CustomerServiceUsersView,
    SalesActiveUsersView,
    SalesUsersView,
    SalesManagerUsersView,
    PharmacistUsersView,
    PharmacyListUsersView,
    CustomerServiceListUsersView,
    FredUsersDetailView,
    FredUserstateView,
    FredUserstateDetailView,
    GetCyberSourceCustomerView,
    GetCyberSourceCustomerFromTransactionIdView,
    CallListView,
    PatientOutreachCreateView,
    PatientOutreachQueueView,
    PatientOutreachStatusUpdateView,
    PatientOutreachBulkStatusUpdateView,
    PatientOutreachDeleteByRxView,
    CreateFredPaymentView,
    BulkCreatePaymentsView,
    CreateFredPaymentTransactionView,
    SendManualPaymentTextView,
    SendCustomSMSView,
    MatchPaymentToRxFillView,
    UpdatePatientCallQueueView,
    RefillsNoPaymentView,
    NewRxNoPaymentView,
    CallQueueListView,
    PatientOutreachListView,
    DoctorListView,
    OfficeTypeListView,
    DoctorDetailView,
    DoctorCreateView,
    DoctorUpdateView,
    DoctorDeleteView,
    DoctorFastListView,
    DoctorListAllView,
    DoctorNPIsView,
    DoctorListPaginatedView,
    DashboardTotalRxReportView,
    DashboardTotalPaymentsReportView,
    DashboardSmsReportView,
    DashboardRefillsReportView,
    DashboardProgramReportView,
    DashboardFulfillmentReportView,
    DashboardTrendsReportView,
    DashboardSumsReportView,
    OfficeListView,
    OfficeDetailView,
    OfficeCreateView,
    OfficeFastListView,
    OfficeUsersView,
    OfficeSalesView,
    UserOfficesView,
    OfficeSetUsersView,
    OfficeSetSalesView,
    OfficeAddUserView,
    OfficeViewView,
    OfficePerformanceView,
    OfficeContactsView,
    OfficeMedicationsView,
    OfficePrescribersView,
    OfficePatientsView,
    OfficeRxView,
    OfficePendingRxView,
    OfficePendingPaymentsView,
    OfficeListPaginatedView,
    OfficeUpdateVendorIdView,
    OfficeByNetsuiteIdView,
    OfficeListAltView,
    OfficeListNewView,
    OfficeListUpdatedView,
    OfficeUnassignedPaginatedView,
    OfficeListWithAddressView,
    OfficePaidRxsView,
    OfficeMovePaymentView,
    OfficeCanPrescribeView,
    OfficeLeafletView,
    OfficeQrView,
    OfficeReportsView,
    OfficeMergeView,
    OfficeLeafletSampleView,
    OfficeSummaryReportView,
    OfficeInventoryReportView,
    OfficeEscrowReportView,
    OfficeSkincareParingsView,
    OfficeProviderSkincarePairingsView,
    OfficeDioBySkuView,
    OfficeUpdateSkusView,
    OfficeDioOptoutView,
    OfficeSaveDioShipmentView,
    OfficeLoadDioView,
)

from fred.views import reference
from fred.views import patient

urlpatterns = [
    # Address urls
    path("addresses/<int:pk>/", FredAddressDetailView.as_view(), name="address_detail"),
    path("addresses/", FredAddressView.as_view(), name="address_list"),
    # Allergens urls
    path(
        "allergens/<int:pk>/",
        FredAllergensDetailView.as_view(),
        name="allergens_detail",
    ),
    path("allergens/", FredAllergensView.as_view(), name="allergens_list"),
    path(
        "dashboard/total-rx-report/",
        DashboardTotalRxReportView.as_view(),
        name="dashboard_total_rx_report",
    ),
    path(
        "dashboard/total-payments-report/",
        DashboardTotalPaymentsReportView.as_view(),
        name="dashboard_total_payments_report",
    ),
    path(
        "dashboard/sms-report/",
        DashboardSmsReportView.as_view(),
        name="dashboard_sms_report",
    ),
    path(
        "dashboard/refills/",
        DashboardRefillsReportView.as_view(),
        name="dashboard_refills_report",
    ),
    path(
        "dashboard/program/",
        DashboardProgramReportView.as_view(),
        name="dashboard_program_report",
    ),
    path(
        "dashboard/fulfillment/",
        DashboardFulfillmentReportView.as_view(),
        name="dashboard_fulfillment_report",
    ),
    path(
        "dashboard/trends/",
        DashboardTrendsReportView.as_view(),
        name="dashboard_trends_report",
    ),
    path(
        "dashboard/sums/",
        DashboardSumsReportView.as_view(),
        name="dashboard_sums_report",
    ),
    # Audit Table urls
    path(
        "audit-tables/<int:pk>/",
        FredAuditTableDetailView.as_view(),
        name="audit_table_detail",
    ),
    path("audit-tables/", FredAuditTableView.as_view(), name="audit_table_list"),
    # Automated tasks urls
    path(
        "automated-tasks/<int:pk>/",
        FredAutomatedtasksDetailView.as_view(),
        name="automated_tasks_detail",
    ),
    path(
        "automated-tasks/",
        FredAutomatedtasksView.as_view(),
        name="automated_tasks_list",
    ),
    # Deleted office urls
    path(
        "deleted-offices/<int:pk>/",
        FredDeletedofficeDetailView.as_view(),
        name="deleted_office_detail",
    ),
    path(
        "deleted-offices/", FredDeletedofficeView.as_view(), name="deleted_office_list"
    ),
    # Device urls
    path("devices/<int:pk>/", FredDeviceDetailView.as_view(), name="device_detail"),
    path("devices/", FredDeviceView.as_view(), name="device_list"),
    # Dispense logs urls
    path(
        "dispense-logs/<int:pk>/",
        FredDispenselogsDetailView.as_view(),
        name="dispense_logs_detail",
    ),
    path("dispense-logs/", FredDispenselogsView.as_view(), name="dispense_logs_list"),
    # Failed fulfill log urls
    path(
        "failed-fulfill-logs/<int:pk>/",
        FredFailedfulfillogDetailView.as_view(),
        name="failed_fulfill_log_detail",
    ),
    path(
        "failed-fulfill-logs/",
        FredFailedfulfillogView.as_view(),
        name="failed_fulfill_log_list",
    ),
    # FAQ urls
    path("faqs/<int:pk>/", FredFaqDetailView.as_view(), name="faq_detail"),
    path("faqs/", FredFaqView.as_view(), name="faq_list"),
    # Feature flag urls
    path(
        "feature-flags/<int:pk>/",
        FredFeatureflagDetailView.as_view(),
        name="feature_flag_detail",
    ),
    path("feature-flags/", FredFeatureflagView.as_view(), name="feature_flag_list"),
    # Fee urls
    path("fees/<int:pk>/", FredFeeDetailView.as_view(), name="fee_detail"),
    path("fees/", FredFeeView.as_view(), name="fee_list"),
    # Fulfillment partners urls
    path(
        "fulfillment-partners/<int:pk>/",
        FredFulfillmentpartnersDetailView.as_view(),
        name="fulfillment_partners_detail",
    ),
    path(
        "fulfillment-partners/",
        FredFulfillmentpartnersView.as_view(),
        name="fulfillment_partners_list",
    ),
    # IHF logs urls
    path("ihf-logs/<int:pk>/", FredIhflogsDetailView.as_view(), name="ihf_logs_detail"),
    path("ihf-logs/", FredIhflogsView.as_view(), name="ihf_logs_list"),
    # Ingredient urls
    path(
        "ingredients/<int:pk>/",
        FredIngredientDetailView.as_view(),
        name="ingredient_detail",
    ),
    path("ingredients/", FredIngredientView.as_view(), name="ingredient_list"),
    # In-house eligibility urls
    path(
        "inhouse-eligibility/<int:pk>/",
        FredInhouseeligibilityDetailView.as_view(),
        name="inhouse_eligibility_detail",
    ),
    path(
        "inhouse-eligibility/",
        FredInhouseeligibilityView.as_view(),
        name="inhouse_eligibility_list",
    ),
    # Inventory urls
    path(
        "inventory/<int:pk>/",
        FredInventoryDetailView.as_view(),
        name="inventory_detail",
    ),
    path("inventory/", FredInventoryView.as_view(), name="inventory_list"),
    # Logs urls
    path("logs/pol/", FredLogsPolView.as_view(), name="logs_pol"),
    path("logs/session/", FredLogsSessionView.as_view(), name="logs_session"),
    path("logs/texterrors/", FredLogsTextErrorsView.as_view(), name="logs_texterrors"),
    path("logs/medswitch/", FredLogsMedSwitchView.as_view(), name="logs_medswitch"),
    path("logs/rphqueue/", FredLogsRphQueueView.as_view(), name="logs_rphqueue"),
    path(
        "logs/patient/<int:patient_id>/",
        FredLogsPatientView.as_view(),
        name="logs_patient",
    ),
    path(
        "logs/payment/<int:payment_id>/",
        FredLogsPaymentView.as_view(),
        name="logs_payment",
    ),
    path("logs/rx/<int:rx_id>/", FredLogsRxView.as_view(), name="logs_rx"),
    path(
        "logs/getrxlogs/<int:patient_id>/",
        FredLogsRxByPatientView.as_view(),
        name="logs_rx_by_patient",
    ),
    path("logs/pay/", FredLogsPayView.as_view(), name="logs_pay"),
    path("logs/<int:pk>/", FredLogsDetailView.as_view(), name="logs_detail"),
    path("logs/", FredLogsView.as_view(), name="logs_list"),
    # Logs patient urls
    path(
        "logs-patient/<int:pk>/",
        FredLogspatientDetailView.as_view(),
        name="logs_patient_detail",
    ),
    path("logs-patient/", FredLogspatientView.as_view(), name="logs_patient_list"),
    # Logs rx urls
    path("logs-rx/<int:pk>/", FredLogsrxDetailView.as_view(), name="logs_rx_detail"),
    path("logs-rx/", FredLogsrxView.as_view(), name="logs_rx_list"),
    # Lots urls
    path("lots/<int:pk>/", FredLotsDetailView.as_view(), name="lots_detail"),
    path("lots/", FredLotsView.as_view(), name="lots_list"),
    # Med alignments urls
    path(
        "med-alignments/<int:pk>/",
        FredMedalignmentsDetailView.as_view(),
        name="med_alignments_detail",
    ),
    path(
        "med-alignments/", FredMedalignmentsView.as_view(), name="med_alignments_list"
    ),
    # Medication urls
    path(
        "medications/<int:pk>/",
        FredMedicationDetailView.as_view(),
        name="medication_detail",
    ),
    path("medications/", FredMedicationView.as_view(), name="medication_list"),
    # Med leaflet urls
    path(
        "med-leaflets/<int:pk>/",
        FredMedleafletDetailView.as_view(),
        name="med_leaflet_detail",
    ),
    path("med-leaflets/", FredMedleafletView.as_view(), name="med_leaflet_list"),
    # Office urls (already provided in example)
    path("offices/<int:pk>/", FredOfficeDetailView.as_view(), name="office_detail"),
    path("offices/", FredOfficeView.as_view(), name="office_list"),
    # Office agreement type urls
    path(
        "office-agreement-types/<int:pk>/",
        FredOfficeagreementtypeDetailView.as_view(),
        name="office_agreement_type_detail",
    ),
    path(
        "office-agreement-types/",
        FredOfficeagreementtypeView.as_view(),
        name="office_agreement_type_list",
    ),
    # Office history urls
    path(
        "office-history/<int:pk>/",
        FredOfficehistoryDetailView.as_view(),
        name="office_history_detail",
    ),
    path(
        "office-history/", FredOfficehistoryView.as_view(), name="office_history_list"
    ),
    # Office info urls
    path(
        "office-info/<int:pk>/",
        FredOfficeinfoDetailView.as_view(),
        name="office_info_detail",
    ),
    path("office-info/", FredOfficeinfoView.as_view(), name="office_info_list"),
    # Office type urls
    path(
        "office-types/<int:pk>/",
        FredOfficetypeDetailView.as_view(),
        name="office_type_detail",
    ),
    path("office-types/", FredOfficetypeView.as_view(), name="office_type_list"),
    # Other medication urls
    path(
        "other-medications/<int:pk>/",
        FredOthermedicationDetailView.as_view(),
        name="other_medication_detail",
    ),
    path(
        "other-medications/",
        FredOthermedicationView.as_view(),
        name="other_medication_list",
    ),
    # Out of stock medication urls
    path(
        "out-of-stock-medications/<int:pk>/",
        FredOutofstockmedicationDetailView.as_view(),
        name="out_of_stock_medication_detail",
    ),
    path(
        "out-of-stock-medications/",
        FredOutofstockmedicationView.as_view(),
        name="out_of_stock_medication_list",
    ),
    # Patient urls
    # path("patients/<int:pk>/", FredPatientDetailView.as_view(), name="patient_detail"),
    # path("patients/", FredPatientView.as_view(), name="patient_list"),
    # Patient logs urls
    path(
        "patient-logs/<int:pk>/",
        FredPatientlogsDetailView.as_view(),
        name="patient_logs_detail",
    ),
    path("patient-logs/", FredPatientlogsView.as_view(), name="patient_logs_list"),
    # Patient meta urls
    path(
        "patient-meta/<int:pk>/",
        FredPatientmetaDetailView.as_view(),
        name="patient_meta_detail",
    ),
    path("patient-meta/", FredPatientmetaView.as_view(), name="patient_meta_list"),
    # Payment urls
    path("payments/<int:pk>/", FredPaymentDetailView.as_view(), name="payment_detail"),
    path("payments/", FredPaymentView.as_view(), name="payment_list"),
    # Payments not approved urls
    path(
        "payments-not-approved/<int:pk>/",
        FredPaymentsnotapprovedDetailView.as_view(),
        name="payments_not_approved_detail",
    ),
    path(
        "payments-not-approved/",
        FredPaymentsnotapprovedView.as_view(),
        name="payments_not_approved_list",
    ),
    # PCD Agreement urls
    path(
        "pcd-agreements/<int:pk>/",
        FredPcdAgreementDetailView.as_view(),
        name="pcd_agreement_detail",
    ),
    path("pcd-agreements/", FredPcdAgreementView.as_view(), name="pcd_agreement_list"),
    # PCD Formulary Agreement urls
    path(
        "pcd-formulary-agreements/<int:pk>/",
        FredPcdFormularyAgreementDetailView.as_view(),
        name="pcd_formulary_agreement_detail",
    ),
    path(
        "pcd-formulary-agreements/",
        FredPcdFormularyAgreementView.as_view(),
        name="pcd_formulary_agreement_list",
    ),
    # PCD Inbound NDC urls
    path(
        "pcd-inbound-ndc/<int:pk>/",
        FredPcdInboundNdcDetailView.as_view(),
        name="pcd_inbound_ndc_detail",
    ),
    path(
        "pcd-inbound-ndc/", FredPcdInboundNdcView.as_view(), name="pcd_inbound_ndc_list"
    ),
    # PCD Normalized Drug Group urls
    path(
        "pcd-normalized-drug-groups/<int:pk>/",
        FredPcdNormalizedDrugGroupDetailView.as_view(),
        name="pcd_normalized_drug_group_detail",
    ),
    path(
        "pcd-normalized-drug-groups/",
        FredPcdNormalizedDrugGroupView.as_view(),
        name="pcd_normalized_drug_group_list",
    ),
    # Prepaid urls
    path("prepaid/<int:pk>/", FredPrepaidDetailView.as_view(), name="prepaid_detail"),
    path("prepaid/", FredPrepaidView.as_view(), name="prepaid_list"),
    # RX urls
    path("rx/<int:pk>/", FredRxDetailView.as_view(), name="rx_detail"),
    path("rx/", FredRxView.as_view(), name="rx_list"),
    # RX Fill urls
    path("rx-fills/<int:pk>/", FredRxfillDetailView.as_view(), name="rx_fill_detail"),
    path("rx-fills/", FredRxfillView.as_view(), name="rx_fill_list"),
    # RX Print urls
    path(
        "rx-prints/<int:pk>/", FredRxprintDetailView.as_view(), name="rx_print_detail"
    ),
    path("rx-prints/", FredRxprintView.as_view(), name="rx_print_list"),
    # RX Raw urls
    path("rx-raw/<int:pk>/", FredRxrawDetailView.as_view(), name="rx_raw_detail"),
    path("rx-raw/", FredRxrawView.as_view(), name="rx_raw_list"),
    # Shipment urls
    path(
        "shipments/<int:pk>/", FredShipmentDetailView.as_view(), name="shipment_detail"
    ),
    path("shipments/", FredShipmentView.as_view(), name="shipment_list"),
    # Skincare pairings urls
    path(
        "skincare-pairings/<int:pk>/",
        FredSkincarepairingsDetailView.as_view(),
        name="skincare_pairings_detail",
    ),
    path(
        "skincare-pairings/",
        FredSkincarepairingsView.as_view(),
        name="skincare_pairings_list",
    ),
    # State urls
    path("states/<int:pk>/", FredStateDetailView.as_view(), name="state_detail"),
    path("states/", FredStateView.as_view(), name="state_list"),
    # Substatus urls
    path(
        "substatus/<int:pk>/",
        FredSubstatusDetailView.as_view(),
        name="substatus_detail",
    ),
    path("substatus/", FredSubstatusView.as_view(), name="substatus_list"),
    # Task urls
    path("tasks/<int:pk>/", FredTaskDetailView.as_view(), name="task_detail"),
    path("tasks/", FredTaskView.as_view(), name="task_list"),
    # Text sent urls
    path(
        "texts-sent/<int:pk>/",
        FredTextsentDetailView.as_view(),
        name="text_sent_detail",
    ),
    path("texts-sent/", FredTextsentView.as_view(), name="text_sent_list"),
    # Token urls
    path("tokens/<int:pk>/", FredTokenDetailView.as_view(), name="token_detail"),
    path("tokens/", FredTokenView.as_view(), name="token_list"),
    # Updated SKUs urls
    path(
        "updated-skus/<int:pk>/",
        FredUpdatedskusDetailView.as_view(),
        name="updated_skus_detail",
    ),
    path("updated-skus/", FredUpdatedskusView.as_view(), name="updated_skus_list"),
    # Users urls
    path("users/add/", UserAddView.as_view(), name="users_add"),
    path("users/<int:pk>/", UserDetailView.as_view(), name="users_detail"),
    path("users/logs/<int:pk>/", UserLogsView.as_view(), name="users_logs"),
    path(
        "users/salesPerformance/",
        SalesPerformanceView.as_view(),
        name="users_sales_performance",
    ),
    path("users/", UserListView.as_view(), name="users_list"),
    path(
        "users/customer-service/",
        CustomerServiceUsersView.as_view(),
        name="users_customer_service_list",
    ),
    path("users/salesActive/", SalesActiveUsersView.as_view(), name="users_sales_list"),
    path("users/sales/", SalesUsersView.as_view(), name="users_sales_all_list"),
    path(
        "users/salesmanager/",
        SalesManagerUsersView.as_view(),
        name="users_sales_manager_list",
    ),
    path("users/pharmacist/", PharmacistUsersView.as_view(), name="users_pharmacist"),
    path(
        "users/pharmacylist/",
        PharmacyListUsersView.as_view(),
        name="users_pharmacy_list",
    ),
    path("users/cslist/", CustomerServiceListUsersView.as_view(), name="users_cs_list"),
    # User state urls
    path(
        "user-states/<int:pk>/",
        FredUserstateDetailView.as_view(),
        name="user_state_detail",
    ),
    path("user-states/", FredUserstateView.as_view(), name="user_state_list"),
    path("call-list/", CallListView.as_view(), name="call_list"),
    path(
        "call-queue/",
        CallQueueListView.as_view(),
        name="call_queue_list",
    ),
    path(
        "dio-items/<int:pk>/", FredDioItemsDetailView.as_view(), name="dio_items_detail"
    ),
    path("dio-items/", FredDioItemsView.as_view(), name="dio_items_list"),
    # Dio Items SKU endpoint with netsuiteid filter
    path("dio-items-sku/", DioItemsSkuView.as_view(), name="dio_items_sku_list"),
    path(
        "patient-outreach/<int:pk>/",
        FredPatientOutreachDetailView.as_view(),
        name="patient_outreach_detail",
    ),
    path(
        "patient-outreach/",
        FredPatientOutreachView.as_view(),
        name="patient_outreach_list",
    ),
    path(
        "patient-outreach-list/",
        PatientOutreachListView.as_view(),
        name="patient_outreach_list_paginated",
    ),
    # Special endpoint for creating outreach records with rxid from URL
    path(
        "patient-outreach/rx/<int:rxid>/",
        PatientOutreachCreateView.as_view(),
        name="patient_outreach_create",
    ),
    path(
        "patient-outreach/queue/",
        PatientOutreachQueueView.as_view(),
        name="patient_outreach_queue",
    ),
    # Status update endpoints for cronjob
    path(
        "patient-outreach/status/<int:pk>/",
        PatientOutreachStatusUpdateView.as_view(),
        name="patient_outreach_status_update",
    ),
    # Bulk status update for cronjob efficiency
    path(
        "patient-outreach/bulk-status-update/",
        PatientOutreachBulkStatusUpdateView.as_view(),
        name="patient_outreach_bulk_status_update",
    ),
    path(
        "payments/create/",
        CreateFredPaymentView.as_view(),
        name="payment_create",
    ),
    path(
        "payments/create-transaction/",
        CreateFredPaymentTransactionView.as_view(),
        name="payment_create_transaction",
    ),
    path(
        "payments/bulk-create/",
        BulkCreatePaymentsView.as_view(),
        name="payment_bulk_create",
    ),
    path(
        "rxfill/manual-payment-text/",
        SendManualPaymentTextView.as_view(),
        name="send_manual_payment_text",
    ),
    path(
        "cybersource/get-customer/",
        GetCyberSourceCustomerView.as_view(),
        name="cybersource_get_customer",
    ),
    path(
        "cybersource/transaction/<str:transaction_id>/customer/",
        GetCyberSourceCustomerFromTransactionIdView.as_view(),
        name="cybersource_get_customer_by_transaction",
    ),
    path(
        "payments/match-to-rxfill/",
        MatchPaymentToRxFillView.as_view(),
        name="payment_match_to_rxfill",
    ),
    path(
        "patient-call-queue/",
        UpdatePatientCallQueueView.as_view(),
        name="update_patient_call_queue",
    ),
    path(
        "patient-outreach/delete-by-rx/",
        PatientOutreachDeleteByRxView.as_view(),
        name="patient_outreach_delete_by_rx",
    ),
    path(
        "sms/send/",
        SendCustomSMSView.as_view(),
        name="send_custom_sms",
    ),
    path(
        "refills-no-payment/",
        RefillsNoPaymentView.as_view(),
        name="refills_no_payment",
    ),
    path(
        "newrx-no-payment/",
        NewRxNoPaymentView.as_view(),
        name="newrx_no_payment",
    ),
    path(
        "doctors/fastlist/",
        DoctorFastListView.as_view(),
        name="doctor_fastlist",
    ),
    path(
        "doctors/list/",
        DoctorListAllView.as_view(),
        name="doctor_list_all",
    ),
    path(
        "doctors/npis/",
        DoctorNPIsView.as_view(),
        name="doctor_npis",
    ),
    path(
        "doctors/list-paginated/",
        DoctorListPaginatedView.as_view(),
        name="doctor_list_paginated",
    ),
    path(
        "doctors/add/",
        DoctorCreateView.as_view(),
        name="doctor_add",
    ),
    path(
        "doctors/<int:pk>/update/",
        DoctorUpdateView.as_view(),
        name="doctor_update",
    ),
    path(
        "doctors/<int:pk>/delete/",
        DoctorDeleteView.as_view(),
        name="doctor_delete",
    ),
    path(
        "doctors/<int:pk>/",
        DoctorDetailView.as_view(),
        name="doctor_detail",
    ),
    path(
        "doctors/",
        DoctorListView.as_view(),
        name="doctor_list",
    ),
    path(
        "office-types/",
        OfficeTypeListView.as_view(),
        name="doctor_list",
    ),
    path("office/add/", OfficeCreateView.as_view(), name="office-create"),
    path("office/fastlist/", OfficeFastListView.as_view(), name="office-fastlist"),
    path("office/user/", UserOfficesView.as_view(), name="office-user"),
    path("office/", OfficeListView.as_view(), name="office-list"),
    path("office/<int:pk>/", OfficeDetailView.as_view(), name="office-detail"),
    path("office/<int:pk>/users/", OfficeUsersView.as_view(), name="office-users"),
    path("office/<int:pk>/sales/", OfficeSalesView.as_view(), name="office-sales"),
    path(
        "office/addUser/<int:pk>/", OfficeAddUserView.as_view(), name="office-add-user"
    ),
    path("office/view/<int:pk>/", OfficeViewView.as_view(), name="office-view"),
    path(
        "office/performance/<int:pk>/",
        OfficePerformanceView.as_view(),
        name="office-performance",
    ),
    path(
        "office/<int:pk>/users/set/",
        OfficeSetUsersView.as_view(),
        name="office-set-users",
    ),
    path(
        "office/<int:pk>/sales/set/",
        OfficeSetSalesView.as_view(),
        name="office-set-sales",
    ),
    path(
        "office/contacts/<int:pk>/",
        OfficeContactsView.as_view(),
        name="office-contacts",
    ),
    path(
        "office/medications/<int:pk>/",
        OfficeMedicationsView.as_view(),
        name="office-medications",
    ),
    path(
        "office/prescribers/<int:pk>/",
        OfficePrescribersView.as_view(),
        name="office-prescribers",
    ),
    path(
        "office/patients/<int:pk>/",
        OfficePatientsView.as_view(),
        name="office-patients",
    ),
    path("office/rx/<int:pk>/", OfficeRxView.as_view(), name="office-rx"),
    path(
        "office/pendingrx/<int:pk>/",
        OfficePendingRxView.as_view(),
        name="office-pending-rx",
    ),
    path(
        "office/pendingpayments/<int:pk>/",
        OfficePendingPaymentsView.as_view(),
        name="office-pending-payments",
    ),
    path(
        "office/list-paginated/",
        OfficeListPaginatedView.as_view(),
        name="office-list-paginated",
    ),
    path(
        "office/update-vendor-id/<int:pk>/",
        OfficeUpdateVendorIdView.as_view(),
        name="office-update-vendor-id",
    ),
    path("office/nsid/", OfficeByNetsuiteIdView.as_view(), name="office-by-nsid"),
    path("office/list/", OfficeListAltView.as_view(), name="office-list-alt"),
    path("office/list-new/", OfficeListNewView.as_view(), name="office-list-new"),
    path(
        "office/list-updated/",
        OfficeListUpdatedView.as_view(),
        name="office-list-updated",
    ),
    path(
        "office/unassigned-paginated/",
        OfficeUnassignedPaginatedView.as_view(),
        name="office-unassigned-paginated",
    ),
    path(
        "office/listWithAddress/",
        OfficeListWithAddressView.as_view(),
        name="office-list-with-address",
    ),
    path(
        "office/paid-rxs/<int:pk>/", OfficePaidRxsView.as_view(), name="office-paid-rxs"
    ),
    path(
        "office/movePayment/",
        OfficeMovePaymentView.as_view(),
        name="office-move-payment",
    ),
    path(
        "office/canPrescribe/<int:pk>/",
        OfficeCanPrescribeView.as_view(),
        name="office-can-prescribe",
    ),
    path(
        "office/leaflet/<int:pk>/", OfficeLeafletView.as_view(), name="office-leaflet"
    ),
    path("office/qr/<int:pk>/", OfficeQrView.as_view(), name="office-qr"),
    path("office/reports/", OfficeReportsView.as_view(), name="office-reports"),
    path("office/merge/", OfficeMergeView.as_view(), name="office-merge"),
    path(
        "office/leafletSample/",
        OfficeLeafletSampleView.as_view(),
        name="office-leaflet-sample",
    ),
    path(
        "office/summaryreport/",
        OfficeSummaryReportView.as_view(),
        name="office-summary-report",
    ),
    path(
        "office/inventoryreport/",
        OfficeInventoryReportView.as_view(),
        name="office-inventory-report",
    ),
    path(
        "office/escrowreport/",
        OfficeEscrowReportView.as_view(),
        name="office-escrow-report",
    ),
    path(
        "office/skincare-pairings/<int:pk>/",
        OfficeSkincareParingsView.as_view(),
        name="office-skincare-pairings",
    ),
    path(
        "office/provider-skincare-pairings/<int:pk>/",
        OfficeProviderSkincarePairingsView.as_view(),
        name="office-provider-skincare-pairings",
    ),
    path(
        "office/getdiobysku/<int:pk>/",
        OfficeDioBySkuView.as_view(),
        name="office-dio-by-sku",
    ),
    path(
        "office/updateskus/<int:pk>/",
        OfficeUpdateSkusView.as_view(),
        name="office-update-skus",
    ),
    path("office/loadDIO/", OfficeLoadDioView.as_view(), name="office-load-dio"),
    path(
        "office/savedioshipment/",
        OfficeSaveDioShipmentView.as_view(),
        name="office-save-dio-shipment",
    ),
    path(
        "office/dio/optout/<int:pk>/",
        OfficeDioOptoutView.as_view(),
        name="office-dio-optout",
    ),
    path(
        "address/create/",
        reference.AddressCreateView.as_view(),
        name="address_create",
    ),
    path(
        "address/",
        reference.AddressGetAllView.as_view(),
        name="address_get_all",
    ),
    path(
        "address/match/",
        reference.AddressMatchView.as_view(),
        name="address_match",
    ),
    path(
        "address/match-all/",
        reference.AddressMatchAllView.as_view(),
        name="address_match_all",
    ),
    path(
        "address/<str:address_id>/",
        reference.AddressOneView.as_view(),
        name="address_get_one",
    ),
    path(
        "patients/",
        patient.PatientViewSet.as_view({"get": "get_all"}),
        name="patient_get_all",
    ),
    path(
        "patients/nophone/",
        patient.PatientViewSet.as_view({"get": "get_all_without_phone"}),
        name="patient_get_all_no_phone",
    ),
    path(
        "patients/list/",
        patient.PatientViewSet.as_view({"get": "get_patient_list"}),
        name="patient_get_list",
    ),
    path(
        "patients/fastlist/",
        patient.PatientViewSet.as_view({"get": "get_patient_fast_list"}),
        name="patient_get_fast_list",
    ),
    path(
        "patients/list-paginated/",
        patient.PatientViewSet.as_view({"get": "get_patient_list_paginated"}),
        name="patient_get_list_paginated",
    ),
    path(
        "patients/add/",
        patient.PatientViewSet.as_view({"post": "add_patient"}),
        name="patient_add_patient",
    ),
    path(
        "patients/merge/",
        patient.PatientViewSet.as_view({"post": "merge_patients"}),
        name="patient_merge_patients",
    ),
    path(
        "patients/search/",
        patient.PatientViewSet.as_view({"get": "search"}),
        name="patient_search_patients",
    ),
    path(
        "patients/paymentvoidrx/",
        patient.PatientViewSet.as_view(
            {"get": "get_patients_with_payment_and_void_rx"}
        ),
        name="patient_payment_void_rx",
    ),
    path(
        "patients/rxnopayment/",
        patient.PatientViewSet.as_view({"get": "get_rxs_with_no_payments"}),
        name="patient_rx_no_payment",
    ),
    path(
        "patients/refillnopayment/",
        patient.PatientViewSet.as_view({"get": "get_refills_with_no_payments"}),
        name="patient_refills_no_payment",
    ),
    path(
        "patients/patienthistory/<str:patient_id>/",
        patient.PatientViewSet.as_view({"get": "get_patient_history"}),
        name="patient_get_patient_history",
    ),
    path(
        "patients/feedbacks/",
        patient.PatientViewSet.as_view({"get": "get_feedbacks"}),
        name="patient_get_feedbacks",
    ),
    path(
        "patients/rxhistory/<str:patient_id>/",
        patient.PatientViewSet.as_view({"get": "get_rx_history_for_patient"}),
        name="patient_get_rx_history",
    ),
    path(
        "patients/rxpayments/<str:patient_id>/",
        patient.PatientViewSet.as_view({"get": "get_prescription_payment_info"}),
        name="patient_get_prescription_payment_info",
    ),
    path(
        "patients/<str:patient_id>/",
        patient.PatientViewSet.as_view(
            {
                "get": "get_one_patient",
                "put": "update_patient",
                "delete": "delete_patient",
            }
        ),
        name="patient_one",
    ),
]
