from rest_framework import serializers
from django.db import transaction
from django.db.models import Q
from mysknv.models import (
    Office,
    Activitylog,
    Correctorrequest,
    Dermacodeprintout,
    Dispense,
    Educatedperson,
    Employee,
    Inventory,
    Ipwhitelist,
    Officeipaduser,
    Officepatient,
    Officepermission,
    Officephysician,
    Officephysicianexclusion,
    Replacementmachinerequest,
    Shipment,
    Skincarecorrector,
    Useroffice,
)


class MySKNVOfficeIpaduserSerializer(serializers.ModelSerializer):
    class Meta:
        model = Officeipaduser
        fields = (
            "officeId",
            "userId",
        )


class MySKNVOfficePatientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Officepatient
        fields = (
            "officeId",
            "patientId",
        )


class MySKNVOfficePermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Officepermission
        fields = (
            "id",
            "roleId",
            "resource",
            "handler",
            "active",
            "dateCreated",
        )


class MySKNVOfficePhysicianExclusionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Officephysicianexclusion
        fields = (
            "officeId",
            "physicianId",
        )


class MySKNVOfficePhysicianSerializer(serializers.ModelSerializer):
    class Meta:
        model = Officephysician
        fields = (
            "officeId",
            "physicianId",
            "status",
        )


class MySKNVOfficeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Office
        fields = (
            "id",
            "companyId",
            "netsuiteId",
            "email",
            "name",
            "streetAddress",
            "city",
            "state",
            "zip",
            "phone",
            "logo",
            "status",
            "allowCustomInventory",
            "allowMoveInventory",
            "originalLogo",
            "logoCosmetic",
            "logoCosmeticAlt",
            "enableIpad",
            "cosmetics",
            "lastRxNumber",
            "leafletHeaderTemplate",
            "tier",
            "expectedPatients",
            "dateCreated",
            "dateModified",
            "adlOptOut",
            "allowOfficeDio",
        )


class OfficeMergeRequestSerializer(serializers.Serializer):
    from_office_id = serializers.IntegerField(
        required=True, help_text="ID of the office to merge FROM (will be soft-deleted)"
    )
    to_office_id = serializers.IntegerField(
        required=True,
        help_text="ID of the office to merge INTO (will receive all records)",
    )


class OfficeMergeService:
    """
    Service to merge two office records.

    Moves all related records from `from_office` to `to_office`,
    skipping duplicates for tables with composite keys,
    then soft-deletes the `from_office`.
    """

    def __init__(self, from_office_id: int, to_office_id: int, user_id: int = None):
        self.from_office_id = from_office_id
        self.to_office_id = to_office_id
        self.user_id = user_id
        self.merge_stats = {}

    def merge(self) -> dict:
        """
        Execute the merge operation.
        Returns a dictionary with merge statistics.
        """
        # Validate offices exist
        from_office = (
            Office.objects.using("mysknv").filter(id=self.from_office_id).first()
        )
        to_office = Office.objects.using("mysknv").filter(id=self.to_office_id).first()

        if not from_office:
            raise ValueError(f"Source office {self.from_office_id} not found")
        if not to_office:
            raise ValueError(f"Target office {self.to_office_id} not found")
        if from_office.id == to_office.id:
            raise ValueError("Cannot merge an office into itself")

        with transaction.atomic(using="mysknv"):
            # Tables with simple officeId (no composite key concerns)
            self._update_simple_table(Dermacodeprintout, "dermacodePrintout")
            self._update_simple_table(Dispense, "dispense")
            self._update_simple_table(Educatedperson, "educatedPerson")
            self._update_simple_table(Employee, "employee")
            self._update_simple_table(Inventory, "inventory")
            self._update_simple_table(Ipwhitelist, "ipWhitelist")
            self._update_simple_table(Shipment, "shipment")

            # Tables with IntegerField officeId (not FK)
            self._update_integer_field_table(Correctorrequest, "correctorRequest")
            self._update_integer_field_table(
                Replacementmachinerequest, "replacementMachineRequest"
            )
            self._update_integer_field_table(Skincarecorrector, "skincareCorrector")

            # Tables with composite keys - skip duplicates
            self._merge_composite_table(Officepatient, "officePatient", "patientId")
            self._merge_composite_table(Officeipaduser, "officeIpadUser", "userId")
            self._merge_composite_table(
                Officephysician, "officePhysician", "physicianId"
            )
            self._merge_composite_table(
                Officephysicianexclusion, "officePhysicianExclusion", "physicianId"
            )
            self._merge_composite_table(Useroffice, "userOffice", "userId")

            # Update activityLog records (has IntegerField officeId)
            self._update_activity_log()

            # Soft delete the source office
            from_office.status = "DELETED"
            from_office.save(using="mysknv")

            # Log the merge action
            self._log_merge_activity(from_office, to_office)

        return {
            "success": True,
            "from_office_id": self.from_office_id,
            "to_office_id": self.to_office_id,
            "stats": self.merge_stats,
        }

    def _update_simple_table(self, model, table_name: str):
        """Update tables with FK to Office."""
        count = (
            model.objects.using("mysknv")
            .filter(officeId=self.from_office_id)
            .update(officeId=self.to_office_id)
        )
        self.merge_stats[table_name] = {"moved": count}

    def _update_integer_field_table(self, model, table_name: str):
        """Update tables with IntegerField officeId."""
        count = (
            model.objects.using("mysknv")
            .filter(officeId=self.from_office_id)
            .update(officeId=self.to_office_id)
        )
        self.merge_stats[table_name] = {"moved": count}

    def _update_activity_log(self):
        """Update activityLog records."""
        count = (
            Activitylog.objects.using("mysknv")
            .filter(officeId=self.from_office_id)
            .update(officeId=self.to_office_id)
        )
        self.merge_stats["activityLog"] = {"moved": count}

    def _merge_composite_table(self, model, table_name: str, secondary_field: str):
        """
        Merge tables with composite keys (officeId + secondary_field).
        Skips records that would create duplicates in target office.
        """
        # Get IDs that already exist in target office
        existing_ids = set(
            model.objects.using("mysknv")
            .filter(officeId=self.to_office_id)
            .values_list(secondary_field, flat=True)
        )

        # Get records from source office
        source_records = model.objects.using("mysknv").filter(
            officeId=self.from_office_id
        )

        moved = 0
        skipped = 0

        for record in source_records:
            secondary_value = getattr(record, secondary_field)
            # Handle FK fields - get the actual ID
            if hasattr(secondary_value, "id"):
                secondary_id = secondary_value.id
            else:
                secondary_id = secondary_value

            if secondary_id in existing_ids:
                # Duplicate - delete from source (it exists in target)
                record.delete(using="mysknv")
                skipped += 1
            else:
                # No duplicate - update to target office
                record.officeId_id = self.to_office_id
                record.save(using="mysknv")
                moved += 1

        self.merge_stats[table_name] = {"moved": moved, "skipped": skipped}

    def _log_merge_activity(self, from_office, to_office):
        """Log the merge action to activityLog."""
        Activitylog.objects.using("mysknv").create(
            userId=self.user_id,
            officeId=self.to_office_id,
            message=f"Merged office {from_office.id} ({from_office.name}) into office {to_office.id} ({to_office.name})",
            category="OFFICE_MERGE",
            isHipaa=0,
        )
