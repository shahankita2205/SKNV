"""
Patient Serializers Module

Contains serializers related to patient management.
"""

from rest_framework import serializers
from django.core.paginator import Paginator
from django.db.models import Q, F, Value, CharField
from django.db.models.functions import Concat
from django.utils.html import strip_tags

from fred.models import patient, reference as reference_model
from fred.serializers import reference

__all__ = [
    # 'PatientSerializer',
    # 'PatientAddressSerializer',
    # 'PatientInsuranceSerializer',
]


class PatientModelSerializer(serializers.ModelSerializer):
    """
    Serializer for Fred Patients
    """

    address = reference.AddressModelSerializer(source="addressid", read_only=True)

    class Meta:
        model = patient.Patient
        fields = "__all__"

    def list_paginated(self, **options):
        # Options with defaults
        limit = options.get("limit", 10)
        page = options.get("page", 1)
        order = options.get("order", 0)
        order_dir = options.get("orderDir", "asc")
        search = options.get("search", "")

        patients = patient.Patient.objects.select_related("addressid").annotate(
            location=Concat(
                "addressid__city",
                Value(", "),
                "addressid__state",
                output_field=CharField(),
            )
        )

        # Filter by search if it exists
        if search:
            search_term = f"%{search}%"
            patients = patients.filter(
                Q(id__icontains=search)
                | Q(name__icontains=search)
                | Q(email__icontains=search)
                | Q(location__icontains=search)
                | Q(dob__icontains=search)
                | Q(phone__icontains=search)
            )

        # Ordering by columns
        columns = {
            0: "id",
            1: "name",
            2: "dob",
            3: "phone",
            4: "email",
            5: "address__city",
        }
        order_column = columns.get(order, "id")
        if order_dir.lower() == "desc":
            order_column = f"-{order_column}"

        patients = patients.order_by(order_column)
        patients = patients.values("id", "name", "dob", "phone", "email", "location")

        paginator = Paginator(patients, limit)
        page_obj = paginator.get_page(page)

        return {
            "patients": list(page_obj.object_list),
            "firstPage": 1,
            "currentPage": page_obj.number,
            "lastPage": paginator.num_pages,
            "recordsFiltered": len(page_obj.object_list),
            "nextPage": page_obj.next_page_number() if page_obj.has_next() else None,
            "previousPage": (
                page_obj.previous_page_number() if page_obj.has_previous() else None
            ),
            "recordsTotal": paginator.count,
            "limit": limit,
        }


class PatientMergeSerializer(serializers.Serializer):
    phone = serializers.CharField(required=True, allow_blank=True, trim_whitespace=True)
    email = serializers.CharField(required=True, allow_blank=True, trim_whitespace=True)
    address = serializers.IntegerField(min_value=1, required=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["to"] = serializers.IntegerField(required=True)
        self.fields["from"] = serializers.IntegerField(required=True)

    def validate_to(self, value):
        if not patient.Patient.objects.filter(id=value).exists():
            raise serializers.ValidationError(f"Patient with id {value} does not exist")
        return value

    def validate_from(self, value):
        if not patient.Patient.objects.filter(id=value).exists():
            raise serializers.ValidationError(f"Patient with id {value} does not exist")
        return value

    def validate_address(self, value):
        if not reference_model.Address.objects.filter(id=value).exists():
            raise serializers.ValidationError(f"Address with id {value} does not exist")
        return value


class PatientPaginationQuerySerializer(serializers.Serializer):
    page = serializers.IntegerField(default=1, min_value=1, required=False)
    limit = serializers.IntegerField(
        default=25, min_value=1, max_value=100, required=False
    )
    searchTerm = serializers.CharField(
        required=False, allow_blank=True, trim_whitespace=True
    )
    order = serializers.ListField(
        child=serializers.DictField(), required=False, allow_empty=True
    )

    def validate_page(self, value):
        """Ensure page is at least 1."""
        if not value or value <= 0:
            return 1
        return value

    def validate_limit(self, value):
        """Ensure limit is reasonable."""
        if not value or value <= 0:
            return 25
        return min(value, 100)

    def validate_searchTerm(self, value):
        """Strip tags and return None if empty."""
        if not value:
            return None
        cleaned = strip_tags(value).strip()
        return cleaned if cleaned else None

    def validate_order(self, value):
        """Extract and validate first order item or return default."""
        if not value or len(value) == 0:
            return {"column": 0, "dir": "asc"}

        first_order = value[0]

        # Validate column
        try:
            column = int(first_order.get("column", 0))
            column = max(0, column)  # Ensure non-negative
        except (ValueError, TypeError):
            column = 0

        # Validate direction
        dir_value = first_order.get("dir", "asc")
        if dir_value:
            cleaned_dir = strip_tags(str(dir_value)).strip().lower()
            dir_value = cleaned_dir if cleaned_dir in ["asc", "desc"] else "asc"
        else:
            dir_value = "asc"

        return {"column": column, "dir": dir_value}
