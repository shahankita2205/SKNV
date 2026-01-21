from django.db import models


class Office(models.Model):
    id = models.AutoField(primary_key=True)
    companyId = models.ForeignKey(
        "Company", models.DO_NOTHING, db_column="companyId"
    )  # Field name made lowercase.
    netsuiteId = models.IntegerField()  # Field name made lowercase.
    email = models.CharField(max_length=255, null=True, blank=True)
    name = models.CharField(max_length=90)  # Fixed max_length from 255 to 90
    streetAddress = models.CharField(
        max_length=90, null=True, blank=True
    )  # Field name made lowercase. Fixed max_length from 255 to 90
    city = models.CharField(
        max_length=45, null=True, blank=True
    )  # Fixed max_length from 255 to 45
    state = models.CharField(
        max_length=2, null=True, blank=True
    )  # Fixed max_length from 255 to 2
    zip = models.CharField(
        max_length=10, null=True, blank=True
    )  # Fixed max_length from 255 to 10
    phone = models.CharField(
        max_length=45, null=True, blank=True
    )  # Fixed max_length from 255 to 45
    logo = models.CharField(
        max_length=2046, null=True, blank=True
    )  # Fixed max_length from 255 to 2046
    status = models.CharField(
        max_length=20, null=True, blank=True, default="NEW"
    )  # Fixed max_length from 255 to 20
    allowCustomInventory = models.SmallIntegerField(
        default=0
    )  # Field name made lowercase. Changed to SmallIntegerField
    allowMoveInventory = models.SmallIntegerField(
        default=0
    )  # Field name made lowercase. Changed to SmallIntegerField
    originalLogo = models.CharField(
        max_length=2046, null=True, blank=True
    )  # Field name made lowercase. Fixed max_length from 255 to 2046
    logoCosmetic = models.CharField(
        max_length=255, null=True, blank=True
    )  # Field name made lowercase.
    logoCosmeticAlt = models.CharField(
        max_length=255, null=True, blank=True
    )  # Field name made lowercase.
    enableIpad = models.SmallIntegerField(
        default=0
    )  # Field name made lowercase. Changed to SmallIntegerField
    cosmetics = models.SmallIntegerField(default=0)  # Changed to SmallIntegerField
    lastRxNumber = models.BigIntegerField(default=104837)  # Field name made lowercase.
    leafletHeaderTemplate = models.SmallIntegerField(
        default=0
    )  # Field name made lowercase. Changed to SmallIntegerField, fixed default from 1 to 0
    tier = models.SmallIntegerField(
        null=True, blank=True, default=0
    )  # Changed to SmallIntegerField, fixed default from 4 to 0
    expectedPatients = models.IntegerField(
        null=True, blank=True
    )  # Field name made lowercase.
    dateCreated = models.DateTimeField(
        null=True, blank=True
    )  # Field name made lowercase.
    dateModified = models.DateTimeField(
        default="CURRENT_TIMESTAMP"
    )  # Field name made lowercase.
    adlOptOut = models.SmallIntegerField(
        default=0
    )  # Field name made lowercase. Changed to SmallIntegerField
    allowOfficeDio = models.SmallIntegerField(
        default=0
    )  # NEW FIELD added. Changed to SmallIntegerField

    class Meta:
        managed = False
        db_table = "office"


class Officeipaduser(models.Model):
    officeId = models.OneToOneField(
        "Office", models.DO_NOTHING, db_column="officeId", primary_key=True
    )  # Field name made lowercase.
    userId = models.ForeignKey(
        "Users", models.DO_NOTHING, db_column="userId"
    )  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = "officeIpadUser"
        unique_together = (("officeId", "userId"),)


class Officepatient(models.Model):
    officeId = models.OneToOneField(
        "Office", models.DO_NOTHING, db_column="officeId", primary_key=True
    )  # Field name made lowercase.
    patientId = models.ForeignKey(
        "Patient", models.DO_NOTHING, db_column="patientId"
    )  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = "officePatient"
        unique_together = (("officeId", "patientId"),)


class Officepermission(models.Model):
    id = models.AutoField(primary_key=True)
    roleId = models.ForeignKey(
        "Role", models.DO_NOTHING, db_column="roleId"
    )  # Field name made lowercase.
    resource = models.CharField(max_length=255)
    handler = models.CharField(max_length=255)
    active = models.IntegerField()
    dateCreated = models.DateTimeField(
        default="CURRENT_TIMESTAMP"
    )  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = "officePermission"


class Officephysician(models.Model):
    officeId = models.OneToOneField(
        "Office", models.DO_NOTHING, db_column="officeId", primary_key=True
    )  # Field name made lowercase.
    physicianId = models.ForeignKey(
        "Physician", models.DO_NOTHING, db_column="physicianId"
    )  # Field name made lowercase.
    status = models.SmallIntegerField(default=1)  # Changed to SmallIntegerField

    class Meta:
        managed = False
        db_table = "officePhysician"
        unique_together = (("officeId", "physicianId"),)


class Officephysicianexclusion(models.Model):
    officeId = models.OneToOneField(
        "Office", models.DO_NOTHING, db_column="officeId", primary_key=True
    )  # Field name made lowercase.
    physicianId = models.ForeignKey(
        "Physician", models.DO_NOTHING, db_column="physicianId"
    )  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = "officePhysicianExclusion"
        unique_together = (("officeId", "physicianId"),)
