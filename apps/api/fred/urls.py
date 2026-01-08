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
    FredUsersView,
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
    FailedTextNoPatientView,
    FailedTextPCDeliversView,
)

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
    path("patients/<int:pk>/", FredPatientDetailView.as_view(), name="patient_detail"),
    path("patients/", FredPatientView.as_view(), name="patient_list"),
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
    path("users/<int:pk>/", FredUsersDetailView.as_view(), name="users_detail"),
    path("users/", FredUsersView.as_view(), name="users_list"),
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
    path(
        "failed-text/not-delivered-pc-delivers/",
        FailedTextPCDeliversView.as_view(),
        name="failed_text_pc_delivers",
    ),
    path(
        "failed-text/not-delivered-no-patient/",
        FailedTextNoPatientView.as_view(),
        name="failed_text_no_patient",
    ),
]
