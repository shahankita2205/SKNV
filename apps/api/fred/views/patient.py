"""
Patient Views Module

Contains views/viewsets related to patient management.

Legacy Controller Mapping: PatientController
"""

from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import action
from django.core import serializers
from django.db import transaction, connections
from django.db.models import Q, Prefetch
from django.utils.html import strip_tags
from core.permissions.legacy import legacy_roles

from fred.models import patient as patient_model
from fred.models import reference as reference_model, Logspatient as logspatient_model
from fred.serializers import reference
from fred.serializers import patient

import json
import logging

logger = logging.getLogger(__name__)

# TODO: Migrate patient-related views from views.py

__all__ = [
    # 'PatientViewSet',
]


class PatientViewSet(viewsets.ViewSet):
    def get_permissions(self):
        method_perms = {
            "patient_get_all - GET": [
                legacy_roles(
                    "admin",
                    "customer-service",
                    "customer-service-manager",
                    "pharmacist",
                    "manager",
                )
            ],
            "patient_get_all_no_phone - GET": [
                legacy_roles(
                    "admin",
                    "customer-service",
                    "customer-service-manager",
                    "manager",
                    "pharmacist",
                )
            ],
            "patient_get_list - GET": [
                legacy_roles(
                    "admin",
                    "customer-service",
                    "customer-service-manager",
                    "pharmacist",
                    "manager",
                )
            ],
            "patient_get_fast_list - GET": [
                legacy_roles(
                    "admin",
                    "customer-service",
                    "customer-service-manager",
                    "pharmacist",
                    "manager",
                )
            ],
            "patient_get_list_paginated - GET": [
                legacy_roles(
                    "admin",
                    "customer-service",
                    "customer-service-manager",
                    "pharmacist",
                    "manager",
                )
            ],
            "patient_one - GET": [
                legacy_roles(
                    "admin",
                    "patient",
                    "customer-service",
                    "customer-service-manager",
                    "pharmacist",
                    "manager",
                    "office",
                )
            ],
            "patient_get_rx - GET": [
                legacy_roles(
                    "admin",
                    "patient",
                    "customer-service",
                    "customer-service-manager",
                    "pharmacist",
                    "manager",
                )
            ],
            "patient_get_payments - GET": [
                legacy_roles(
                    "admin",
                    "patient",
                    "customer-service",
                    "customer-service-manager",
                    "pharmacist",
                    "manager",
                )
            ],
            "patient_get_cards - GET": [
                legacy_roles(
                    "admin",
                    "patient",
                    "customer-service",
                    "customer-service-manager",
                    "pharmacist",
                    "manager",
                )
            ],
            "patient_get_view - GET": [
                legacy_roles(
                    "admin",
                    "patient",
                    "customer-service",
                    "customer-service-manager",
                    "pharmacist",
                    "manager",
                    "office",
                    "doctor",
                )
            ],
            "patient_add_patient - POST": [
                legacy_roles("admin", "pharmacist", "doctor", "office")
            ],
            "patient_one - PUT": [
                legacy_roles(
                    "admin",
                    "patient",
                    "customer-service",
                    "customer-service-manager",
                    "pharmacist",
                    "sales",
                    "sales-manager",
                )
            ],
            "patient_one - DELETE": [
                legacy_roles(
                    "admin",
                )
            ],
            "patient_merge_patients - POST": [
                legacy_roles("admin", "pharmacist", "customer-service-manager")
            ],
            "patient_search_patients - GET": [legacy_roles("admin", "pharmacist")],
            "patient_payment_void_rx - GET": [
                legacy_roles(
                    "admin", "customer-service-manager", "manager", "pharmacist"
                )
            ],
            "patient_rx_no_payment - GET": [
                legacy_roles(
                    "admin",
                    "customer-service",
                    "customer-service-manager",
                    "manager",
                    "pharmacist",
                )
            ],
            "patient_refills_no_payment - GET": [
                legacy_roles(
                    "admin",
                    "customer-service",
                    "customer-service-manager",
                    "manager",
                    "pharmacist",
                )
            ],
            "patient_get_patient_history - GET": [
                legacy_roles(
                    "admin",
                    "customer-service",
                    "customer-service-manager",
                    "manager",
                    "pharmacist",
                )
            ],
            "patient_get_feedbacks - GET": [
                legacy_roles(
                    "admin",
                    "customer-service",
                    "customer-service-manager",
                    "manager",
                    "pharmacist",
                )
            ],
            "patient_get_rx_history - GET": [
                legacy_roles(
                    "admin",
                    "customer-service",
                    "customer-service-manager",
                    "manager",
                    "pharmacist",
                )
            ],
            "patient_get_prescription_payment_info - GET": [
                legacy_roles(
                    "admin",
                    "customer-service",
                    "customer-service-manager",
                    "manager",
                    "pharmacist",
                )
            ],
        }
        logger.error(self.request.resolver_match.view_name)
        perms = method_perms.get(
            f"{self.request.resolver_match.view_name} - {self.request.method}", []
        )
        return [perm() for perm in perms]

    """
    GET /patients/
    Get all patients
    """

    def get_all(self, request):
        try:
            # Create payment record within a transaction
            with transaction.atomic(using="fred"):
                patients = patient_model.Patient.objects.all().order_by("id")
                return Response(
                    {
                        "message": "Patients retrieved successfully",
                        "values": list(patients.values()),
                    },
                    status=status.HTTP_200_OK,
                )
        except Exception as e:
            logger.error(f"Unexpected error Retrieving all patients: {e}")
            return Response(
                {"error": "An error occurred while retrieving the patients"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    """
    GET /patients/nophone
    Get all patients along with their address city/state and office name/id
    """

    def get_all_without_phone(self, request):
        try:
            # Create payment record within a transaction
            with transaction.atomic(using="fred"):
                with connections["fred"].cursor() as cursor:
                    cursor.execute(
                        "select distinct on(p.id) patientId, p.name, p.dob, p.phone, p.email, p.created, a.city, a.state, o.name as officeName, o.id as officeId from rx inner join patient p on rx.patientid = p.id inner join address a on p.addressid = a.id inner join office o on rx.officeid = o.id where p.phone IS NULL OR p.phone = '' OR p.phone = '5555555555'"
                    )
                    total_count = cursor.rowcount
                    columns = [col[0] for col in cursor.description]
                    results = [dict(zip(columns, row)) for row in cursor.fetchall()]
                    return Response(
                        {
                            "count": total_count,
                            "message": "Patients retrieved successfully",
                            "values": results,
                        },
                        status=status.HTTP_200_OK,
                    )
        except Exception as e:
            logger.error(f"Unexpected error Retrieving all patients: {e}")
            return Response(
                {
                    "error": "An error occurred while retrieving the patients",
                    "error2": f"{e}",
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    """
    GET /patients/list
    Get all patients with their address info
    """

    def get_patient_list(self, request):
        try:
            # Create payment record within a transaction
            with transaction.atomic(using="fred"):
                patients = patient_model.Patient.objects.select_related(
                    "addressid"
                ).all()[:1000]
                serializer = patient.PatientModelSerializer(patients, many=True)
                return Response(
                    {
                        "message": "Patients retrieved successfully",
                        "values": serializer.data,
                    },
                    status=status.HTTP_200_OK,
                )
        except Exception as e:
            logger.error(f"Unexpected error Retrieving all patients: {e}")
            return Response(
                {
                    "error": "An error occurred while retrieving the patients",
                    "error2": f"{e}",
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    """
    GET /patients/fastlist
    Get all patients with their address info
    """

    def get_patient_fast_list(self, request):
        try:
            serializer = patient.PatientModelSerializer()
            patients_list = serializer.list_paginated(limit=100, order=0)
            results = []
            for patient_obj in patients_list["patients"]:
                results.append({"id": patient_obj["id"], "name": patient_obj["name"]})

            return Response(
                {"message": "Patients retrieved successfully", "results": results},
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            logger.error(f"Unexpected error Retrieving all patients: {e}")
            return Response(
                {
                    "error": "An error occurred while retrieving the patients",
                    "error2": f"{e}",
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    """
    GET /patients/list-paginated
    Get all patients with their address info
    """

    def get_patient_list_paginated(self, request):
        try:
            input_serializer = patient.PatientPaginationQuerySerializer(
                data=request.GET
            )
            input_serializer.is_valid(raise_exception=True)

            params = input_serializer.validated_data
            order_data = params.get("order", {"column": 0, "dir": "asc"})

            patient_serializer = patient.PatientModelSerializer()
            results = patient_serializer.list_paginated(
                page=params["page"],
                limit=params["limit"],
                search=params.get("searchTerm"),
                order=order_data["column"],
                orderDir=order_data["dir"],
            )
            return Response(
                {"message": "Patients retrieved successfully", "results": results},
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            logger.error(f"Unexpected error Retrieving all patients: {e}")
            return Response(
                {
                    "error": "An error occurred while retrieving the patients",
                    "error2": f"{e}",
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    """
    GET /patients/<patientid>
    Get a single patient from a provided id along with their address
    """

    def get_one_patient(self, request, patient_id):
        if not patient_id or not patient_id.strip():
            return Response(
                {"error": "Expected 'patient_id' integer in request url"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            patient_obj = patient_model.Patient.objects.select_related("addressid").get(
                id=patient_id.strip()
            )
            patient_serializer = patient.PatientModelSerializer(patient_obj)
            return Response(
                {
                    "message": "Successfully retreived patient",
                    "value": patient_serializer.data,
                },
                status=status.HTTP_200_OK,
            )
        except patient_model.Patient.DoesNotExist:
            return Response(
                {"error": f"Patient with id {patient_id} not found"},
                status=status.HTTP_400_BAD_REQUEST,
            )

    """
    GET /patients/rx/{patient_id}
    Gets all Rxs for a patient along with any related information
    """

    def get_patient_rxs(self, request, patient_id):
        # TO DO when Rxs are implemented
        return Response(
            {"error": "Not Implemented Yet"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    """
    GET /patients/payments/{patient_id}
    Gets all Payments for a patient along with any related information
    """

    def get_patient_payments(self, request, patient_id):
        # TO DO when Payments are implemented
        return Response(
            {"error": "Not Implemented Yet"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    """
    GET /patients/cards/{patient_id}
    Gets all Cards for a patient from Payments along with any related information
    """

    def get_patient_cards(self, request, patient_id):
        # TO DO when Payments are implemented
        return Response(
            {"error": "Not Implemented Yet"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    """
    GET /patients/view/{patient_id}
    Gets patient information with address, but first needs a role check to make sure the use has access to view the patient.
        To be implemented once offices and users are done.
    """

    def view_patient(self, request, patient_id):
        # TO DO when Offices and Users are implemented
        return Response(
            {"error": "Not Implemented Yet"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    """
    POST /patients/add/
    Create Patient record

    Expected payload: (All optional)
    {
        "addressid":
        "firstname":
        "lastname":
        "dob":
        "gender":
        "phone":
        "email":
        "allergies":
        "otherdrugs":
        "otherinfo":
        "pregnant":
        "prefix":
        "middlename":
        "suffix":
        "userid":
        "pharmetikaid":

    }
    """

    def add_patient(self, request):
        try:
            # Serialize and validate the input data
            serializer = patient.PatientModelSerializer(data=request.data)
            if not serializer.is_valid():
                return Response(
                    {"error": "Invalid data", "details": serializer.errors},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            with transaction.atomic(using="fred"):
                patient_obj = serializer.save()

                # Log successful creation
                logger.info(f"Patient created successfully: ID {patient_obj.id}")

                return Response(
                    {
                        "message": "Patient created successfully",
                        "id": patient_obj.id,  # Return ID like the original function
                    },
                    status=status.HTTP_201_CREATED,
                )
        except Exception as e:
            logger.error(f"Unexpected error creating patient: {e}")
            return Response(
                {"error": "An error occurred while creating the patient"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    """
    PUT /patients/{patient_id}/
    Update Patient record

    Expected payload: (All optional)
    {
        "addressid":
        "firstname":
        "lastname":
        "dob":
        "gender":
        "phone":
        "email":
        "allergies":
        "otherdrugs":
        "otherinfo":
        "pregnant":
        "prefix":
        "middlename":
        "suffix":
        "userid":
        "pharmetikaid":

    }
    """

    def update_patient(self, request, patient_id):
        try:
            # Serialize and validate the input data
            serializer = patient.PatientModelSerializer(data=request.data)
            if not serializer.is_valid():
                return Response(
                    {"error": "Invalid data", "details": serializer.errors},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            if not patient_id or not patient_id.strip():
                return Response(
                    {"error": "Expected 'patient_id' integer in request url"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Update Patient record within a transaction
            with transaction.atomic(using="fred"):
                patient_obj = patient_model.Patient.objects.get(id=patient_id.strip())
                for attribute, value in request.data.items():
                    if attribute == "addressid":
                        address_obj = reference_model.Address.objects.get(id=value)
                        setattr(patient_obj, attribute, address_obj)
                    else:
                        setattr(patient_obj, attribute, value)

                patient_obj.full_clean()
                patient_obj.save()

                # Log successful creation
                logger.info(f"Patient updated successfully: ID {patient_obj.id}")

                return Response(
                    {
                        "message": "Patient updated successfully",
                        "id": patient_obj.id,  # Return ID like the original function
                    },
                    status=status.HTTP_200_OK,
                )
        except patient_model.Patient.DoesNotExist:
            return Response(
                {"error": f"Patient with id {patient_id} not found"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except reference_model.Address.DoesNotExist:
            return Response(
                {"error": f"Address with id given in payload not found"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Exception as e:
            logger.error(f"Unexpected error updating Patient: {e}")
            return Response(
                {"error": "An error occurred while updating the Patient"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    """
    DELETE /patients/{patient_id}/
    Delete Patient record
    """

    def delete_patient(self, request, patient_id):
        try:
            if not patient_id or not patient_id.strip():
                return Response(
                    {"error": "Expected 'patient_id' integer in request url"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            with transaction.atomic(using="fred"):
                patient_obj = patient_model.Patient.objects.get(id=patient_id.strip())

                patient_obj.delete()

                # Log successful creation
                logger.info(f"Patient deleted successfully: ID {patient_id.strip()}")

                return Response(
                    {
                        "message": "Patient deleted successfully",
                        "id": patient_id.strip(),  # Return ID like the original function
                    },
                    status=status.HTTP_200_OK,
                )
        except patient_model.Patient.DoesNotExist:
            return Response(
                {"error": f"Patient with id {patient_id.strip()} not found"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Exception as e:
            logger.error(f"Unexpected error updating patient: {e}")
            return Response(
                {"error": "An error occurred while updating the patient"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    """
    POST - /patients/merge/
    Merges a patient into another patient
    Expected Payload:
    {
        to: (patient_id),
        from: (patient_id),
        phone:
        email:
        address: (address_id)
    }
    """

    def merge_patients(self, request):
        try:
            # Serialize Input
            serializer = patient.PatientMergeSerializer(data=request.data)
            if not serializer.is_valid():
                return Response(
                    {
                        "error": "Invalid request data",
                        "details": serializer.errors,
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )
            with transaction.atomic(using="fred"):
                logger.error(serializer.data)
                to_patient = patient_model.Patient.objects.get(id=serializer.data["to"])
                from_patient = patient_model.Patient.objects.get(
                    id=serializer.data["from"]
                )
                address = reference_model.Address.objects.get(
                    id=serializer.data["address"]
                )
                # TO DO
                # Merge Tasks
                # Merge Payments
                # Merge Rxs
                # Merge Logs
                # Merge Prepaids
                # Merge IHF Logs
                # Merge Texts Sent

                # Update Patient Information
                setattr(to_patient, "phone", serializer.data["phone"])
                setattr(to_patient, "email", serializer.data["email"])
                setattr(to_patient, "addressid", address)
                to_patient.allergies = (
                    from_patient.allergies if from_patient.allergies else "n/a"
                )
                to_patient.otherdrugs = (
                    from_patient.otherdrugs if from_patient.otherdrugs else "n/a"
                )
                to_patient.otherinfo = (
                    from_patient.otherinfo if from_patient.otherinfo else "n/a"
                )
                to_patient.full_clean()
                to_patient.save()

                from_patient.delete()

                # Digital Health Merging Here.
                # Logging Here
                return Response(
                    {
                        "message": "Patient merged successfully",
                    },
                    status=status.HTTP_200_OK,
                )
        except patient_model.Patient.DoesNotExist:
            return Response(
                {"error": f"Patient not found"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except reference_model.Address.DoesNotExist:
            return Response(
                {"error": f"Address with id {serializer.data.address} not found"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Exception as e:
            logger.error(f"Unexpected error merging patients: {e}")
            return Response(
                {"error": f"An error occurred while merging the patient. {e}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    """
    GET - /patients/search/?term={search}
    Gets all patients whose name contains the search term.
    """

    def search(self, request):
        try:
            term = request.GET.get("term", "")
            term = strip_tags(term).strip() if term else ""
            with transaction.atomic(using="fred"):
                patients = patient_model.Patient.objects.filter(
                    name__icontains=term
                ).order_by("id")
                return Response(
                    {
                        "message": "Patients retrieved successfully",
                        "values": list(patients.values()),
                    },
                    status=status.HTTP_200_OK,
                )
        except Exception as e:
            logger.error(f"Unexpected error searching for patients: {e}")
            return Response(
                {"error": f"An error occurred while searching the patient. {e}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    """
    GET - /patients/paymentvoidrx/
    Gets all patients with both a payment and a void rx.
    """

    def get_patients_with_payment_and_void_rx(self, request):
        # TO DO when Offices and Users are implemented
        return Response(
            {"error": "Not Implemented Yet"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    """
    GET - /patients/rxnopayment/
    Gets all Rxs with no payments.
    Why this is a patient endpoint? No idea. 
    """

    def get_rxs_with_no_payments(self, request):
        # TO DO when Payments and Rxs are implemented
        return Response(
            {"error": "Not Implemented Yet"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    """
    GET - /patients/refillnopayment/
    Gets all Refills with no payments.
    Why this is a patient endpoint? No idea. 
    """

    def get_refills_with_no_payments(self, request):
        # TO DO when Payments and Rxs and Rxfills are implemented
        return Response(
            {"error": "Not Implemented Yet"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    """
    GET - /patients/patienthistory/{patient_id}
    Gets all patient history logs for a given patient in descending order
    """

    def get_patient_history(self, request, patient_id):
        try:
            with transaction.atomic(using="fred"):
                patient_logs = logspatient_model.objects.filter(
                    patientid=patient_id.strip()
                ).order_by("-id")
                return Response(
                    {
                        "message": "Patients retrieved successfully",
                        "values": list(patient_logs.values()),
                    },
                    status=status.HTTP_200_OK,
                )
        except Exception as e:
            logger.error(f"Unexpected error getting patient history: {e}")
            return Response(
                {"error": "An error occurred while getting patient history"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    """
    GET - /patients/feedbacks
    Gets all feedbacks
    """

    def get_feedbacks(self, request):
        # TO DO when Digital Health is implemented
        return Response(
            {"error": "Not Implemented Yet"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    """
    GET - /patients/rxhistory/{patient_id}
    Gets all rx history logs for a given patient in descending order
    """

    def get_rx_history_for_patient(self, request, patient_id):
        # TO DO when Rx is implemented
        return Response(
            {"error": "Not Implemented Yet"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    """
    GET - /patients/rxpayments/{patient_id}
    Gets all the information on the patient and their payments.
    """

    def get_prescription_payment_info(self, request, patient_id):
        # TO DO when Rx, Doctor, Office, RxFill, Medication, Office are implemented
        return Response(
            {"error": "Not Implemented Yet"},
            status=status.HTTP_400_BAD_REQUEST,
        )
