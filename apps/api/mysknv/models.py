# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class Clindiffview(models.Model):
    approved = models.IntegerField(default=0)
    formulaCode = models.CharField(max_length=255)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = "ClinDiffView"


class Activitylog(models.Model):
    id = models.AutoField(primary_key=True)
    userId = models.BigIntegerField(null=True, blank=True)  # Field name made lowercase.
    officeId = models.IntegerField(null=True, blank=True)  # Field name made lowercase.
    ipAddress = models.CharField(
        max_length=255, null=True, blank=True
    )  # Field name made lowercase.
    message = models.CharField(max_length=255, null=True, blank=True)
    category = models.CharField(max_length=255, null=True, blank=True)
    isHipaa = models.IntegerField(default=0)  # Field name made lowercase.
    timeCreated = models.DateTimeField(
        default="CURRENT_TIMESTAMP"
    )  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = "activityLog"


class Address(models.Model):
    id = models.AutoField(primary_key=True)
    street = models.CharField(max_length=255, null=True, blank=True)
    city = models.CharField(max_length=255, null=True, blank=True)
    state = models.CharField(max_length=255, null=True, blank=True)
    zip = models.CharField(max_length=255, null=True, blank=True)
    phone = models.CharField(max_length=255, null=True, blank=True)
    dateCreated = models.DateTimeField()  # Field name made lowercase.
    dateUpdated = models.DateTimeField()  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = "address"


class Authevent(models.Model):
    id = models.AutoField(primary_key=True)
    userId = models.ForeignKey(
        "Users", models.DO_NOTHING, db_column="userId"
    )  # Field name made lowercase.
    event_type = models.IntegerField(default=0)
    ipaddress = models.CharField(max_length=255)
    time_attempted = models.IntegerField()

    class Meta:
        managed = False
        db_table = "authevent"


class Baseelement(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    location = models.CharField(max_length=255)
    content = models.TextField()

    class Meta:
        managed = False
        db_table = "baseElement"


class Clindiff(models.Model):
    approved = models.IntegerField(default=0)
    formulaCode = models.CharField(
        primary_key=True, max_length=255
    )  # Field name made lowercase.
    content = models.TextField(null=True, blank=True)
    modified = models.DateTimeField(default="CURRENT_TIMESTAMP")

    class Meta:
        managed = False
        db_table = "clinDiff"


class Coachingreport(models.Model):
    id = models.AutoField(primary_key=True)
    ownerId = models.IntegerField()  # Field name made lowercase.
    consultantId = models.IntegerField()  # Field name made lowercase.
    status = models.IntegerField(default=0)
    dateStart = models.CharField(max_length=255)  # Field name made lowercase.
    dateEnd = models.CharField(max_length=255)  # Field name made lowercase.
    q1 = models.IntegerField(default=0)
    q2 = models.IntegerField(default=0)
    q3 = models.IntegerField(default=0)
    q4 = models.IntegerField(default=0)
    q5 = models.IntegerField(default=0)
    q6 = models.IntegerField(default=0)
    q7 = models.IntegerField(default=0)
    q8 = models.IntegerField(default=0)
    q9 = models.IntegerField(default=0)
    q10 = models.IntegerField(default=0)
    q11 = models.IntegerField(default=0)
    q12 = models.IntegerField(default=0)
    q13 = models.IntegerField(default=0)
    q14 = models.IntegerField(default=0)
    q15 = models.IntegerField(default=0)
    q16 = models.IntegerField(default=0)
    q17 = models.IntegerField(default=0)
    q18 = models.IntegerField(default=0)
    q19 = models.IntegerField(default=0)
    q20 = models.IntegerField(default=0)
    q21 = models.IntegerField(default=0)
    q22 = models.IntegerField(default=0)
    q23 = models.IntegerField(default=0)
    q24 = models.IntegerField(default=0)
    q25 = models.IntegerField(default=0)
    q26 = models.IntegerField(default=0)
    q27 = models.IntegerField(default=0)
    q28 = models.IntegerField(default=0)
    q29 = models.IntegerField(default=0)
    q30 = models.IntegerField(default=0)
    strength1 = models.TextField(null=True, blank=True)
    strength2 = models.TextField(null=True, blank=True)
    strength3 = models.TextField(null=True, blank=True)
    opportunity1 = models.TextField(null=True, blank=True)
    opportunity2 = models.TextField(null=True, blank=True)
    opportunity3 = models.TextField(null=True, blank=True)
    actionitems = models.TextField(null=True, blank=True)
    dateCreated = models.DateTimeField(
        default="CURRENT_TIMESTAMP"
    )  # Field name made lowercase.
    dateModified = models.DateTimeField(
        null=True, blank=True
    )  # Field name made lowercase.
    q31 = models.IntegerField(null=True, blank=True)
    q32 = models.IntegerField(null=True, blank=True)
    q33 = models.IntegerField(null=True, blank=True, default=0)
    q34 = models.IntegerField(null=True, blank=True, default=0)
    q35 = models.IntegerField(null=True, blank=True, default=0)
    q36 = models.IntegerField(null=True, blank=True, default=0)
    version = models.IntegerField(default=1)

    class Meta:
        managed = False
        db_table = "coachingReport"


class Coachingreportinprogress(models.Model):
    id = models.AutoField(primary_key=True)
    ownerId = models.IntegerField()  # Field name made lowercase.
    consultantId = models.IntegerField()  # Field name made lowercase.
    status = models.IntegerField(default=0)
    dateStart = models.CharField(
        max_length=255, null=True, blank=True
    )  # Field name made lowercase.
    dateEnd = models.CharField(
        max_length=255, null=True, blank=True
    )  # Field name made lowercase.
    q1 = models.IntegerField(null=True, blank=True, default=0)
    q2 = models.IntegerField(null=True, blank=True, default=0)
    q3 = models.IntegerField(null=True, blank=True, default=0)
    q4 = models.IntegerField(null=True, blank=True, default=0)
    q5 = models.IntegerField(null=True, blank=True, default=0)
    q6 = models.IntegerField(null=True, blank=True, default=0)
    q7 = models.IntegerField(null=True, blank=True, default=0)
    q8 = models.IntegerField(null=True, blank=True, default=0)
    q9 = models.IntegerField(null=True, blank=True, default=0)
    q10 = models.IntegerField(null=True, blank=True, default=0)
    q11 = models.IntegerField(null=True, blank=True, default=0)
    q12 = models.IntegerField(null=True, blank=True, default=0)
    q13 = models.IntegerField(null=True, blank=True, default=0)
    q14 = models.IntegerField(null=True, blank=True, default=0)
    q15 = models.IntegerField(null=True, blank=True, default=0)
    q16 = models.IntegerField(null=True, blank=True, default=0)
    q17 = models.IntegerField(null=True, blank=True, default=0)
    q18 = models.IntegerField(null=True, blank=True, default=0)
    q19 = models.IntegerField(null=True, blank=True, default=0)
    q20 = models.IntegerField(null=True, blank=True, default=0)
    q21 = models.IntegerField(null=True, blank=True, default=0)
    q22 = models.IntegerField(null=True, blank=True, default=0)
    q23 = models.IntegerField(null=True, blank=True, default=0)
    q24 = models.IntegerField(null=True, blank=True, default=0)
    q25 = models.IntegerField(null=True, blank=True, default=0)
    q26 = models.IntegerField(null=True, blank=True, default=0)
    q27 = models.IntegerField(null=True, blank=True, default=0)
    q28 = models.IntegerField(null=True, blank=True, default=0)
    q29 = models.IntegerField(null=True, blank=True, default=0)
    q30 = models.IntegerField(null=True, blank=True, default=0)
    q31 = models.IntegerField(null=True, blank=True)
    q32 = models.IntegerField(null=True, blank=True)
    q33 = models.IntegerField(null=True, blank=True, default=0)
    q34 = models.IntegerField(null=True, blank=True, default=0)
    q35 = models.IntegerField(null=True, blank=True, default=0)
    q36 = models.IntegerField(null=True, blank=True, default=0)
    strength1 = models.TextField(null=True, blank=True)
    strength2 = models.TextField(null=True, blank=True)
    strength3 = models.TextField(null=True, blank=True)
    opportunity1 = models.TextField(null=True, blank=True)
    opportunity2 = models.TextField(null=True, blank=True)
    opportunity3 = models.TextField(null=True, blank=True)
    actionitems = models.TextField(null=True, blank=True)
    dateCreated = models.DateTimeField(
        default="CURRENT_TIMESTAMP"
    )  # Field name made lowercase.
    dateModified = models.DateTimeField(
        null=True, blank=True
    )  # Field name made lowercase.
    version = models.IntegerField(default=1)

    class Meta:
        managed = False
        db_table = "coachingReportInProgress"


class Coachingreportsignature(models.Model):
    id = models.AutoField(primary_key=True)
    coachingReportId = models.ForeignKey(
        "Coachingreport", models.DO_NOTHING, db_column="coachingReportId"
    )  # Field name made lowercase.
    s3Url = models.CharField(
        max_length=255, null=True, blank=True
    )  # Field name made lowercase.
    actions = models.CharField(max_length=255, null=True, blank=True)
    dateCreated = models.DateTimeField(
        default="CURRENT_TIMESTAMP"
    )  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = "coachingReportSignature"


class Commercialmedication(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    active = models.IntegerField(default=0)
    dateCreated = models.DateTimeField(
        default="CURRENT_TIMESTAMP"
    )  # Field name made lowercase.
    dateModified = models.DateTimeField(
        null=True, blank=True
    )  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = "commercialMedication"


class Commercialproduct(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    dateCreated = models.DateTimeField()  # Field name made lowercase.
    dateModified = models.DateTimeField()  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = "commercialProduct"


class Commercialproductingredient(models.Model):
    ingredientId = models.OneToOneField(
        "Ingredient", models.DO_NOTHING, db_column="ingredientId", primary_key=True
    )  # Field name made lowercase.
    commercialProductId = models.OneToOneField(
        "Commercialproduct",
        models.DO_NOTHING,
        db_column="commercialProductId",
    )  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = "commercialProductIngredient"


class Company(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255, null=True, blank=True)
    dateCreated = models.CharField(
        max_length=255, null=True, blank=True
    )  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = "company"


class Concern(models.Model):
    id = models.AutoField(primary_key=True)
    description = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        managed = False
        db_table = "concern"


class Conditions(models.Model):
    id = models.AutoField(primary_key=True)
    formulaCode = models.CharField(max_length=255)  # Field name made lowercase.
    condition = models.CharField(max_length=255)

    class Meta:
        managed = False
        db_table = "conditions"


class Consentsignature(models.Model):
    id = models.AutoField(primary_key=True)
    netsuiteId = models.IntegerField()  # Field name made lowercase.
    s3Url = models.CharField(max_length=255)  # Field name made lowercase.
    name = models.CharField(max_length=255, default="")
    title = models.CharField(max_length=255, default="")
    dateCreated = models.DateTimeField(
        default="CURRENT_TIMESTAMP"
    )  # Field name made lowercase.
    licenseNum = models.CharField(
        max_length=255, null=True, blank=True
    )  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = "consentSignature"


class Correctorrequest(models.Model):
    id = models.AutoField(primary_key=True)
    netsuiteId = models.IntegerField()  # Field name made lowercase.
    officeId = models.IntegerField()  # Field name made lowercase.
    officeName = models.CharField(max_length=255)  # Field name made lowercase.
    userId = models.IntegerField()  # Field name made lowercase.
    userName = models.CharField(max_length=255)  # Field name made lowercase.
    physicianName = models.CharField(max_length=255)  # Field name made lowercase.
    orderNum = models.CharField(max_length=255)  # Field name made lowercase.
    itemNum = models.CharField(max_length=255)  # Field name made lowercase.
    lotNum = models.CharField(
        max_length=255, null=True, blank=True
    )  # Field name made lowercase.
    numUnits = models.IntegerField(null=True, blank=True)  # Field name made lowercase.
    leaked = models.IntegerField(null=True, blank=True)
    defectivePackaging = models.IntegerField(
        null=True, blank=True
    )  # Field name made lowercase.
    filling = models.IntegerField(null=True, blank=True)
    shipping = models.IntegerField(null=True, blank=True)
    disliked = models.IntegerField(null=True, blank=True)
    consistency = models.IntegerField(null=True, blank=True)
    consistencyDesc = models.TextField(
        null=True, blank=True
    )  # Field name made lowercase.
    color = models.IntegerField(null=True, blank=True)
    colorDesc = models.TextField(null=True, blank=True)  # Field name made lowercase.
    odor = models.IntegerField(null=True, blank=True)
    odorDesc = models.TextField(null=True, blank=True)  # Field name made lowercase.
    other = models.IntegerField(null=True, blank=True)
    otherDesc = models.TextField(null=True, blank=True)  # Field name made lowercase.
    adverse = models.IntegerField(default=0)
    replacement = models.IntegerField(null=True, blank=True)
    credit = models.IntegerField(null=True, blank=True)
    refund = models.IntegerField(null=True, blank=True)
    dateCreated = models.DateTimeField()  # Field name made lowercase.
    dateModified = models.DateTimeField()  # Field name made lowercase.
    complaintSource = models.CharField(
        max_length=255, null=True, blank=True
    )  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = "correctorRequest"


class Cosmetic(models.Model):
    id = models.AutoField(primary_key=True)
    netsuiteId = models.IntegerField()  # Field name made lowercase.
    baseCode = models.CharField(
        max_length=255, null=True, blank=True
    )  # Field name made lowercase.
    sku = models.CharField(max_length=255)
    displayName = models.CharField(max_length=255)  # Field name made lowercase.
    containerSize = models.CharField(
        max_length=255, null=True, blank=True
    )  # Field name made lowercase.
    unitPrice = models.DecimalField(
        max_digits=10, decimal_places=2, default=0.00
    )  # Field name made lowercase.
    dateCreated = models.DateTimeField()  # Field name made lowercase.
    dateModified = models.DateTimeField()  # Field name made lowercase.
    unitsPerCase = models.IntegerField(
        null=True, blank=True
    )  # Field name made lowercase.
    active = models.IntegerField()

    class Meta:
        managed = False
        db_table = "cosmetic"


class Cosmeticleaflet(models.Model):
    baseCode = models.CharField(
        primary_key=True, max_length=255
    )  # Field name made lowercase.
    title = models.CharField(max_length=255)
    mainImageUrl = models.CharField(
        max_length=255, null=True, blank=True
    )  # Field name made lowercase.
    intro = models.TextField()
    benefits = models.TextField(null=True, blank=True)
    howItWorks = models.TextField()  # Field name made lowercase.
    dailyApplication = models.CharField(
        max_length=255, null=True, blank=True
    )  # Field name made lowercase.
    directions = models.CharField(max_length=255, null=True, blank=True)
    ingredients = models.TextField(null=True, blank=True)
    dateCreated = models.DateTimeField(
        null=True, blank=True
    )  # Field name made lowercase.
    dateModified = models.DateTimeField(
        null=True, blank=True, default="CURRENT_TIMESTAMP"
    )  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = "cosmeticLeaflet"


class Dermacode(models.Model):
    id = models.AutoField(primary_key=True)
    code = models.CharField(max_length=255)

    class Meta:
        managed = False
        db_table = "dermacode"


class Dermacodecosmetic(models.Model):
    dermacodeId = models.ForeignKey(
        "Dermacode", models.DO_NOTHING, db_column="dermacodeId", primary_key=True
    )  # Field name made lowercase.
    baseCode = models.CharField(
        max_length=255, null=True, blank=True
    )  # Field name made lowercase.
    isOptional = models.IntegerField(default=0)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = "dermacodeCosmetic"


class Dermacodeprintout(models.Model):
    id = models.AutoField(primary_key=True)
    officeId = models.ForeignKey(
        "Office", models.DO_NOTHING, db_column="officeId"
    )  # Field name made lowercase.
    userId = models.IntegerField()  # Field name made lowercase.
    dermacode = models.CharField(max_length=255)
    s3Key = models.CharField(max_length=255)  # Field name made lowercase.
    dateCreated = models.DateTimeField()  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = "dermacodePrintout"


class Dispense(models.Model):
    id = models.AutoField(primary_key=True)
    officeId = models.ForeignKey(
        "Office", models.DO_NOTHING, db_column="officeId"
    )  # Field name made lowercase.
    patientId = models.IntegerField(null=True, blank=True)  # Field name made lowercase.
    physicianId = models.IntegerField(
        null=True, blank=True
    )  # Field name made lowercase.
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    dermacode = models.CharField(max_length=255, null=True, blank=True)
    dateCreated = models.DateTimeField()  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = "dispense"


class Dispenseitem(models.Model):
    id = models.AutoField(primary_key=True)
    dispenseId = models.ForeignKey(
        "Dispense", models.DO_NOTHING, db_column="dispenseId"
    )  # Field name made lowercase.
    inventoryId = models.ForeignKey(
        "Inventory", models.DO_NOTHING, db_column="inventoryId", null=True, blank=True
    )  # Field name made lowercase.
    formulaName = models.CharField(max_length=255)  # Field name made lowercase.
    formulaIngredients = models.CharField(
        max_length=255, null=True, blank=True
    )  # Field name made lowercase.
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    prescriptionSerialNumber = models.CharField(
        max_length=255, null=True, blank=True
    )  # Field name made lowercase.
    instructions = models.CharField(max_length=255, null=True, blank=True)
    log = models.BinaryField(null=True, blank=True)

    class Meta:
        managed = False
        db_table = "dispenseItem"


class Dispenseitemdeletion(models.Model):
    id = models.AutoField(primary_key=True)
    dispenseId = models.IntegerField()  # Field name made lowercase.
    dispenseItemId = models.BigIntegerField()  # Field name made lowercase.
    jsonData = models.TextField()  # Field name made lowercase.
    dateCreated = models.DateTimeField()  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = "dispenseItemDeletion"


class Educatedperson(models.Model):
    id = models.AutoField(primary_key=True)
    employeeId = models.ForeignKey(
        "Employee", models.DO_NOTHING, db_column="employeeId", null=True, blank=True
    )  # Field name made lowercase.
    officeId = models.ForeignKey(
        "Office", models.DO_NOTHING, db_column="officeId"
    )  # Field name made lowercase.
    name = models.BinaryField()
    nameHash = models.CharField(max_length=255)  # Field name made lowercase.
    convertedToPatient = models.IntegerField(default=0)  # Field name made lowercase.
    interested = models.IntegerField(null=True, blank=True)
    s3Url = models.CharField(
        max_length=255, null=True, blank=True
    )  # Field name made lowercase.
    dateCreated = models.DateTimeField()  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = "educatedPerson"


class Educatedpersonsignature(models.Model):
    educatedPersonId = models.OneToOneField(
        "Educatedperson",
        models.DO_NOTHING,
        db_column="educatedPersonId",
        primary_key=True,
    )  # Field name made lowercase.
    signature = models.BinaryField()

    class Meta:
        managed = False
        db_table = "educatedPersonSignature"


class Emaillist(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    subject = models.CharField(max_length=255, null=True, blank=True)
    comment = models.CharField(max_length=255, null=True, blank=True)
    to = models.TextField(null=True, blank=True)
    cc = models.TextField(null=True, blank=True)
    bcc = models.TextField(null=True, blank=True)
    sendgrid = models.IntegerField(default=0)
    template = models.TextField(null=True, blank=True)
    plainText = models.TextField(null=True, blank=True)  # Field name made lowercase.
    dateCreated = models.DateTimeField()  # Field name made lowercase.
    dateModified = models.DateTimeField()  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = "emailList"


class Employee(models.Model):
    id = models.AutoField(primary_key=True)
    officeId = models.ForeignKey(
        "Office", models.DO_NOTHING, db_column="officeId"
    )  # Field name made lowercase.
    name = models.CharField(max_length=255)
    email = models.CharField(max_length=255, null=True, blank=True)
    streetAddress = models.CharField(
        max_length=255, null=True, blank=True
    )  # Field name made lowercase.
    city = models.CharField(max_length=255, null=True, blank=True)
    state = models.CharField(max_length=255, null=True, blank=True)
    zip = models.CharField(max_length=255, null=True, blank=True)
    ssn = models.BinaryField(null=True, blank=True)
    ssnIdx = models.CharField(
        max_length=255, null=True, blank=True
    )  # Field name made lowercase.
    agreementS3Key = models.CharField(
        max_length=255, null=True, blank=True
    )  # Field name made lowercase.
    w9S3Key = models.CharField(
        max_length=255, null=True, blank=True
    )  # Field name made lowercase.
    active = models.IntegerField(default=1)
    isTest = models.IntegerField(
        null=True, blank=True, default=0
    )  # Field name made lowercase.
    dateCreated = models.DateTimeField()  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = "employee"


class Formula(models.Model):
    id = models.AutoField(primary_key=True)
    formulaCode = models.CharField(max_length=255)  # Field name made lowercase.
    name = models.CharField(max_length=255, null=True, blank=True)
    ingredients = models.TextField(null=True, blank=True)
    sincerusIngredients = models.CharField(
        max_length=255, null=True, blank=True
    )  # Field name made lowercase.
    caseQuantity = models.IntegerField()  # Field name made lowercase.
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    tier1 = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    tier2 = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    tier3 = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    tier4 = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    tier5 = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    msrp = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    active = models.IntegerField(default=1)
    bestSeller = models.IntegerField(default=0)  # Field name made lowercase.
    dosageForm = models.CharField(
        max_length=255, null=True, blank=True
    )  # Field name made lowercase.
    dateDeactivated = models.DateTimeField(
        null=True, blank=True
    )  # Field name made lowercase.
    dateUpdated = models.DateTimeField(
        null=True, blank=True
    )  # Field name made lowercase.
    commonUsage = models.CharField(
        max_length=255, null=True, blank=True
    )  # Field name made lowercase.
    nsId = models.IntegerField(null=True, blank=True)  # Field name made lowercase.
    size = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        managed = False
        db_table = "formula"


class Formulaingredient(models.Model):
    formulaCode = models.CharField(
        max_length=6, primary_key=True
    )  # Field name made lowercase.
    ingredientId = models.IntegerField()  # Field name made lowercase.
    active = models.IntegerField(default=0)

    class Meta:
        managed = False
        db_table = "formulaIngredient"


class Formulapreorder(models.Model):
    id = models.AutoField(primary_key=True)
    formulaRequestId = models.ForeignKey(
        "Formularequest", models.DO_NOTHING, db_column="formulaRequestId"
    )  # Field name made lowercase.
    userId = models.IntegerField()  # Field name made lowercase.
    officeName = models.CharField(max_length=255)  # Field name made lowercase.
    qty = models.IntegerField()
    dateCreated = models.DateTimeField()  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = "formulaPreorder"


class Formularequest(models.Model):
    id = models.AutoField(primary_key=True)
    salesUserId = models.ForeignKey(
        "Users", models.DO_NOTHING, db_column="salesUserId", null=True, blank=True
    )  # Field name made lowercase.
    formulaName = models.CharField(
        max_length=255, null=True, blank=True
    )  # Field name made lowercase.
    formula = models.CharField(max_length=255, null=True, blank=True)
    practiceName = models.CharField(
        max_length=255, null=True, blank=True
    )  # Field name made lowercase.
    condition = models.CharField(max_length=255, null=True, blank=True)
    severity = models.CharField(max_length=255, null=True, blank=True)
    similarProduct = models.CharField(
        max_length=255, null=True, blank=True
    )  # Field name made lowercase.
    substitute = models.CharField(max_length=255, null=True, blank=True)
    dosageForm = models.CharField(
        max_length=255, null=True, blank=True
    )  # Field name made lowercase.
    offeredFormula = models.CharField(
        max_length=255, null=True, blank=True
    )  # Field name made lowercase.
    assignee = models.CharField(max_length=255, null=True, blank=True)
    isActive = models.IntegerField(
        null=True, blank=True, default=1
    )  # Field name made lowercase.
    status = models.IntegerField(null=True, blank=True)
    isPreorder = models.IntegerField(
        null=True, blank=True, default=0
    )  # Field name made lowercase.
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    datePreorderStart = models.DateTimeField(
        null=True, blank=True
    )  # Field name made lowercase.
    datePreorderEnd = models.DateTimeField(
        null=True, blank=True
    )  # Field name made lowercase.
    dateCreated = models.DateTimeField()  # Field name made lowercase.
    dateModified = models.DateTimeField()  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = "formulaRequest"


class Formularequestcomment(models.Model):
    id = models.AutoField(primary_key=True)
    formulaRequestId = models.ForeignKey(
        "Formularequest", models.DO_NOTHING, db_column="formulaRequestId"
    )  # Field name made lowercase.
    userId = models.ForeignKey(
        "Users", models.DO_NOTHING, db_column="userId"
    )  # Field name made lowercase.
    message = models.CharField(max_length=255, null=True, blank=True)
    dateCreated = models.DateTimeField()  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = "formulaRequestComment"


class Ingredient(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    commercialInactive = models.IntegerField(default=0)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = "ingredient"


class Ingredientconcern(models.Model):
    ingredientId = models.OneToOneField(
        "Ingredient", models.DO_NOTHING, db_column="ingredientId", primary_key=True
    )  # Field name made lowercase.
    concernId = models.OneToOneField(
        "Concern", models.DO_NOTHING, db_column="concernId"
    )  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = "ingredientConcern"


class Inventory(models.Model):
    id = models.AutoField(primary_key=True)
    officeId = models.ForeignKey(
        "Office", models.DO_NOTHING, db_column="officeId"
    )  # Field name made lowercase.
    formulaCode = models.ForeignKey(
        "Formula", models.DO_NOTHING, db_column="formulaCode", null=True, blank=True
    )  # Field name made lowercase.
    cosmeticId = models.IntegerField(
        null=True, blank=True
    )  # Field name made lowercase.
    amount = models.IntegerField(default=0)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    internalName = models.CharField(max_length=255)  # Field name made lowercase.
    instructions = models.CharField(max_length=255, null=True, blank=True)
    reorderTrigger = models.IntegerField(default=0)  # Field name made lowercase.
    reorderNotification = models.IntegerField(default=0)  # Field name made lowercase.
    disabled = models.IntegerField(default=0)
    type = models.CharField(max_length=255, null=True, blank=True, default="formula")
    useAlternateLogo = models.IntegerField(default=0)  # Field name made lowercase.
    dateUpdated = models.DateTimeField()  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = "inventory"


class Ipwhitelist(models.Model):
    id = models.AutoField(primary_key=True)
    officeId = models.ForeignKey(
        "Office", models.DO_NOTHING, db_column="officeId"
    )  # Field name made lowercase.
    cidr = models.CharField(max_length=255)
    dateCreated = models.DateTimeField(
        default="CURRENT_TIMESTAMP"
    )  # Field name made lowercase.
    dateModified = models.DateTimeField(
        null=True, blank=True, default="CURRENT_TIMESTAMP"
    )  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = "ipWhitelist"


class Issue(models.Model):
    id = models.AutoField(primary_key=True)
    userId = models.IntegerField(null=True, blank=True)  # Field name made lowercase.
    username = models.CharField(max_length=255, null=True, blank=True)
    description = models.TextField()
    attachments = models.TextField(null=True, blank=True)
    referrer = models.CharField(max_length=255, null=True, blank=True)
    useragent = models.CharField(max_length=255, null=True, blank=True)
    dateCreated = models.DateTimeField()  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = "issue"


class Leaflet(models.Model):
    id = models.AutoField(primary_key=True)
    formulaId = models.CharField(max_length=255)  # Field name made lowercase.
    status = models.IntegerField(default=0)
    formatting = models.TextField(null=True, blank=True)
    content = models.TextField(null=True, blank=True)
    instructions = models.TextField(null=True, blank=True)
    blackbox = models.TextField(null=True, blank=True)
    previewImage = models.CharField(
        max_length=255, null=True, blank=True
    )  # Field name made lowercase.
    ingredientCount = models.IntegerField(
        null=True, blank=True
    )  # Field name made lowercase.
    dateCreated = models.DateTimeField()  # Field name made lowercase.
    dateModified = models.DateTimeField()  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = "leaflet"


class LeafletIngredient(models.Model):
    leafletId = models.OneToOneField(
        "Leaflet", models.DO_NOTHING, db_column="leafletId"
    )  # Field name made lowercase.
    ingredientId = models.OneToOneField(
        "Ingredient", models.DO_NOTHING, db_column="ingredientId"
    )  # Field name made lowercase.
    position = models.IntegerField(default=0)

    class Meta:
        managed = False
        db_table = "leaflet_ingredient"


class Legalinfo(models.Model):
    id = models.AutoField(primary_key=True)
    netsuiteId = models.IntegerField()  # Field name made lowercase.
    physicianGroup = models.CharField(max_length=255)  # Field name made lowercase.
    physicianName = models.CharField(max_length=255)  # Field name made lowercase.
    physicianEmail = models.CharField(
        max_length=255, null=True, blank=True
    )  # Field name made lowercase.
    state = models.CharField(max_length=255, null=True, blank=True)
    dateCreated = models.DateTimeField()  # Field name made lowercase.
    dateModified = models.DateTimeField(
        null=True, blank=True, default="CURRENT_TIMESTAMP"
    )  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = "legalInfo"


class Lotnumber(models.Model):
    id = models.AutoField(primary_key=True)
    netsuiteId = models.IntegerField()  # Field name made lowercase.
    formulaCode = models.CharField(max_length=255)  # Field name made lowercase.
    lotNumber = models.CharField(max_length=255)  # Field name made lowercase.
    qty = models.IntegerField()
    hidden = models.IntegerField()
    dateAdded = models.DateField()  # Field name made lowercase.
    dateCreated = models.DateTimeField()  # Field name made lowercase.
    dateModified = models.DateTimeField()  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = "lotNumber"
        unique_together = ("netsuiteId", "formulaCode", "lotNumber")


class Medspasalesdio(models.Model):
    id = models.AutoField(primary_key=True)
    formulaCode = models.CharField(max_length=255)  # Field name made lowercase.
    active = models.IntegerField(default=0)
    dateCreated = models.DateTimeField(
        default="CURRENT_TIMESTAMP"
    )  # Field name made lowercase.
    dateModified = models.DateTimeField(
        null=True, blank=True
    )  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = "medSpaSalesDio"


class Medspasalesiou(models.Model):
    id = models.AutoField(primary_key=True)
    formulaCode = models.CharField(max_length=255)  # Field name made lowercase.
    active = models.IntegerField(default=0)
    dateCreated = models.DateTimeField(
        default="CURRENT_TIMESTAMP"
    )  # Field name made lowercase.
    dateModified = models.DateTimeField(
        null=True, blank=True
    )  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = "medSpaSalesIou"


class Medicationassessment(models.Model):
    id = models.AutoField(primary_key=True)
    commercialMedId = models.IntegerField(primary_key=False)
    formulaCode = models.CharField(max_length=255)  # Field name made lowercase.
    notes = models.CharField(max_length=255, null=True, blank=True)
    active = models.IntegerField(default=0)
    dateCreated = models.DateTimeField(
        default="CURRENT_TIMESTAMP"
    )  # Field name made lowercase.
    dateModified = models.DateTimeField(null=True, blank=True)

    class Meta:
        managed = False
        db_table = "medicationAssessment"


class Newpermission(models.Model):
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
        db_table = "newPermission"


class Newsalesresource(models.Model):
    id = models.AutoField(primary_key=True)
    categoryId = models.IntegerField()  # Field name made lowercase.
    title = models.CharField(max_length=255)
    summary = models.CharField(max_length=255, null=True, blank=True)
    url = models.CharField(max_length=255, null=True, blank=True)
    s3Url = models.CharField(
        max_length=255, null=True, blank=True
    )  # Field name made lowercase.
    comments = models.CharField(max_length=255, null=True, blank=True)
    dateCreated = models.DateTimeField(
        default="CURRENT_TIMESTAMP"
    )  # Field name made lowercase.
    dateModified = models.DateTimeField(
        null=True, blank=True
    )  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = "newSalesResource"


class Nsendpoints(models.Model):
    id = models.AutoField(primary_key=True)
    endPointURI = models.CharField(max_length=255)  # Field name made lowercase.
    deployID = models.IntegerField()  # Field name made lowercase.
    scriptID = models.IntegerField()  # Field name made lowercase.
    endPointMeta = models.CharField(max_length=255)  # Field name made lowercase.
    endPointName = models.CharField(max_length=255)  # Field name made lowercase.
    endPointRealmID = models.CharField(max_length=255)  # Field name made lowercase.
    endPointInstanceKey = models.CharField(max_length=255)  # Field name made lowercase.
    endPointKey = models.CharField(max_length=255)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = "nsEndpoints"


class Nsorder(models.Model):
    id = models.AutoField(primary_key=True)
    customerNsId = models.IntegerField()  # Field name made lowercase.
    transactionId = models.CharField(max_length=255)  # Field name made lowercase.
    customerName = models.CharField(max_length=255)  # Field name made lowercase.
    trackingNumbers = models.CharField(
        max_length=255, null=True, blank=True
    )  # Field name made lowercase.
    status = models.CharField(max_length=255, null=True, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    dateCreated = models.DateTimeField()  # Field name made lowercase.
    dateModified = models.DateTimeField()  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = "nsOrder"


class Nsorderitem(models.Model):
    id = models.AutoField(primary_key=True)
    nsOrderId = models.ForeignKey(
        "Nsorder", models.DO_NOTHING, db_column="nsOrderId"
    )  # Field name made lowercase.
    sku = models.CharField(max_length=255, null=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    casePrice = models.DecimalField(
        max_digits=10, decimal_places=2
    )  # Field name made lowercase.
    unitPrice = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True
    )  # Field name made lowercase.
    cases = models.IntegerField()
    units = models.IntegerField(null=True, blank=True)
    type = models.CharField(max_length=255)

    class Meta:
        managed = False
        db_table = "nsOrderItem"


class Nsordertracking(models.Model):
    id = models.AutoField(primary_key=True)
    nsOrderId = models.ForeignKey(
        "Nsorder", models.DO_NOTHING, db_column="nsOrderId"
    )  # Field name made lowercase.
    tracking = models.CharField(max_length=255)
    proofOfDeliveryUrl = models.CharField(
        max_length=255, null=True, blank=True
    )  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = "nsOrderTracking"


class Office(models.Model):
    id = models.AutoField(primary_key=True)
    companyId = models.ForeignKey(
        "Company", models.DO_NOTHING, db_column="companyId"
    )  # Field name made lowercase.
    netsuiteId = models.IntegerField()  # Field name made lowercase.
    email = models.CharField(max_length=255, null=True, blank=True)
    name = models.CharField(max_length=255)
    streetAddress = models.CharField(
        max_length=255, null=True, blank=True
    )  # Field name made lowercase.
    city = models.CharField(max_length=255, null=True, blank=True)
    state = models.CharField(max_length=255, null=True, blank=True)
    zip = models.CharField(max_length=255, null=True, blank=True)
    phone = models.CharField(max_length=255, null=True, blank=True)
    logo = models.CharField(max_length=255, null=True, blank=True)
    status = models.CharField(max_length=255, null=True, blank=True, default="NEW")
    allowCustomInventory = models.IntegerField(default=0)  # Field name made lowercase.
    allowMoveInventory = models.IntegerField(default=0)  # Field name made lowercase.
    originalLogo = models.CharField(
        max_length=255, null=True, blank=True
    )  # Field name made lowercase.
    logoCosmetic = models.CharField(
        max_length=255, null=True, blank=True
    )  # Field name made lowercase.
    logoCosmeticAlt = models.CharField(
        max_length=255, null=True, blank=True
    )  # Field name made lowercase.
    enableIpad = models.IntegerField(default=0)  # Field name made lowercase.
    cosmetics = models.IntegerField(default=0)
    lastRxNumber = models.BigIntegerField(default=104837)  # Field name made lowercase.
    leafletHeaderTemplate = models.IntegerField(default=1)  # Field name made lowercase.
    tier = models.IntegerField(null=True, blank=True, default=4)
    expectedPatients = models.IntegerField(
        null=True, blank=True
    )  # Field name made lowercase.
    dateCreated = models.DateTimeField(
        null=True, blank=True
    )  # Field name made lowercase.
    dateModified = models.DateTimeField(
        default="CURRENT_TIMESTAMP"
    )  # Field name made lowercase.
    adlOptOut = models.IntegerField(default=0)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = "office"


class Officeipaduser(models.Model):
    officeId = models.OneToOneField(
        "Office", models.DO_NOTHING, db_column="officeId"
    )  # Field name made lowercase.
    userId = models.OneToOneField(
        "Users", models.DO_NOTHING, db_column="userId"
    )  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = "officeIpadUser"


class Officepatient(models.Model):
    officeId = models.OneToOneField(
        "Office", models.DO_NOTHING, db_column="officeId"
    )  # Field name made lowercase.
    patientId = models.OneToOneField(
        "Patient", models.DO_NOTHING, db_column="patientId"
    )  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = "officePatient"


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
        "Office", models.DO_NOTHING, db_column="officeId"
    )  # Field name made lowercase.
    physicianId = models.OneToOneField(
        "Physician", models.DO_NOTHING, db_column="physicianId"
    )  # Field name made lowercase.
    status = models.IntegerField(default=1)

    class Meta:
        managed = False
        db_table = "officePhysician"


class Officephysicianexclusion(models.Model):
    officeId = models.OneToOneField(
        "Office", models.DO_NOTHING, db_column="officeId"
    )  # Field name made lowercase.
    physicianId = models.OneToOneField(
        "Physician", models.DO_NOTHING, db_column="physicianId"
    )  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = "officePhysicianExclusion"


class Outgoingemail(models.Model):
    id = models.AutoField(primary_key=True)
    emailListId = models.ForeignKey(
        "Emaillist", models.DO_NOTHING, db_column="emailListId", null=True, blank=True
    )  # Field name made lowercase.
    name = models.CharField(max_length=255, null=True, blank=True)
    subject = models.CharField(max_length=255, null=True, blank=True)
    recipients = models.TextField(null=True, blank=True)
    dateCreated = models.DateTimeField()  # Field name made lowercase.
    dateModified = models.DateTimeField()  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = "outgoingEmail"


class Patient(models.Model):
    id = models.AutoField(primary_key=True)
    userId = models.ForeignKey(
        "Users", models.DO_NOTHING, db_column="userId", null=True, blank=True
    )  # Field name made lowercase.
    officePatientId = models.BinaryField(
        null=True, blank=True
    )  # Field name made lowercase.
    name = models.BinaryField()
    email = models.BinaryField(null=True, blank=True)
    streetAddress = models.BinaryField(
        null=True, blank=True
    )  # Field name made lowercase.
    city = models.BinaryField(null=True, blank=True)
    state = models.BinaryField(null=True, blank=True)
    zip = models.BinaryField(null=True, blank=True)
    phone = models.BinaryField(null=True, blank=True)
    height = models.BinaryField(null=True, blank=True)
    weight = models.BinaryField(null=True, blank=True)
    dateOfBirth = models.BinaryField(
        null=True, blank=True
    )  # Field name made lowercase.
    gender = models.BinaryField(null=True, blank=True)

    class Meta:
        managed = False
        db_table = "patient"


class Patientphysician(models.Model):
    patientId = models.OneToOneField(
        "Patient", models.DO_NOTHING, db_column="patientId", primary_key=True
    )  # Field name made lowercase.
    physicianId = models.OneToOneField(
        "Physician", models.DO_NOTHING, db_column="physicianId"
    )  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = "patientPhysician"


class Pcdcontract(models.Model):
    id = models.AutoField(primary_key=True)
    salesUserId = models.ForeignKey(
        "Users", models.DO_NOTHING, db_column="salesUserId", null=True, blank=True
    )  # Field name made lowercase.
    practiceEmail = models.CharField(
        max_length=255, null=True, blank=True
    )  # Field name made lowercase.
    token = models.CharField(max_length=255)
    signed = models.IntegerField(default=0)
    s3Url = models.CharField(
        max_length=255, null=True, blank=True
    )  # Field name made lowercase.
    jsonData = models.TextField()  # Field name made lowercase.
    documentType = models.IntegerField(
        null=True, blank=True
    )  # Field name made lowercase.
    dateTokenSent = models.DateTimeField(
        null=True, blank=True
    )  # Field name made lowercase.
    dateCreated = models.DateTimeField(
        default="CURRENT_TIMESTAMP"
    )  # Field name made lowercase.
    dateModified = models.DateTimeField(
        null=True, blank=True
    )  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = "pcdContract"


class PcinvPcinventoryItems(models.Model):
    id = models.AutoField(primary_key=True)
    item_id = models.CharField(max_length=255)
    item_name = models.CharField(max_length=255)
    item_formula = models.CharField(max_length=255)
    item_price = models.CharField(max_length=255)
    item_suggested = models.CharField(max_length=255)
    last_mod = models.CharField(max_length=255)
    items_in_case = models.IntegerField(null=True, blank=True)

    class Meta:
        managed = False
        db_table = "pcinv_pcinventory_items"


class Permission(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255, null=True, blank=True)
    isRoute = models.IntegerField(null=True, blank=True)  # Field name made lowercase.
    scope = models.CharField(max_length=255, default="default")

    class Meta:
        managed = False
        db_table = "permission"


class Phinxlog(models.Model):
    version = models.BigIntegerField(primary_key=True)
    migration_name = models.CharField(max_length=255, null=True, blank=True)
    start_time = models.DateTimeField(null=True, blank=True)
    end_time = models.DateTimeField(null=True, blank=True)
    breakpoint = models.IntegerField(default=0)

    class Meta:
        managed = False
        db_table = "phinxlog"


class Physician(models.Model):
    id = models.AutoField(primary_key=True)
    userId = models.ForeignKey(
        "Users", models.DO_NOTHING, db_column="userId", null=True, blank=True
    )  # Field name made lowercase.
    name = models.CharField(max_length=255)
    email = models.CharField(max_length=255, null=True, blank=True)
    streetAddress = models.CharField(
        max_length=255, null=True, blank=True
    )  # Field name made lowercase.
    city = models.CharField(max_length=255, null=True, blank=True)
    state = models.CharField(max_length=255, null=True, blank=True)
    zip = models.CharField(max_length=255, null=True, blank=True)
    phone = models.CharField(max_length=255, null=True, blank=True)
    dateCreated = models.DateTimeField()  # Field name made lowercase.
    dateUpdated = models.DateTimeField()  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = "physician"


class Quote(models.Model):
    id = models.AutoField(primary_key=True)
    payload = models.JSONField(null=True, blank=True)

    class Meta:
        managed = False
        db_table = "quote"


class Refillreminder(models.Model):
    id = models.AutoField(primary_key=True)
    dispenseId = models.ForeignKey(
        "Dispense", models.DO_NOTHING, db_column="dispenseId"
    )  # Field name made lowercase.
    reminderDate = models.DateField()  # Field name made lowercase.
    sent = models.IntegerField(default=0)
    interval = models.IntegerField()
    dateSent = models.DateTimeField(null=True, blank=True)  # Field name made lowercase.
    dateCreated = models.DateTimeField()  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = "refillReminder"


class Refundrequest(models.Model):
    id = models.AutoField(primary_key=True)
    patientName = models.BinaryField()  # Field name made lowercase.
    patientAddress = models.BinaryField()  # Field name made lowercase.
    patientEmailOrPhone = models.BinaryField(
        null=True, blank=True
    )  # Field name made lowercase.
    doctorsName = models.CharField(max_length=255)  # Field name made lowercase.
    practiceName = models.CharField(max_length=255)  # Field name made lowercase.
    dateOfVisit = models.DateField()  # Field name made lowercase.
    lotNumber = models.CharField(max_length=255)  # Field name made lowercase.
    color = models.CharField(max_length=255, null=True, blank=True)
    consistency = models.CharField(max_length=255, null=True, blank=True)
    odor = models.CharField(max_length=255, null=True, blank=True)
    efficacy = models.CharField(max_length=255, null=True, blank=True)
    sensitivity = models.CharField(max_length=255, null=True, blank=True)
    container = models.CharField(max_length=255, null=True, blank=True)
    amountPaid = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True
    )  # Field name made lowercase.
    dateCreated = models.DateTimeField()  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = "refundRequest"


class Replacementmachinerequest(models.Model):
    id = models.AutoField(primary_key=True)
    netsuiteId = models.IntegerField()  # Field name made lowercase.
    officeId = models.IntegerField()  # Field name made lowercase.
    officeName = models.CharField(max_length=255)  # Field name made lowercase.
    userId = models.IntegerField()  # Field name made lowercase.
    userName = models.CharField(max_length=255)  # Field name made lowercase.
    physicianName = models.CharField(max_length=255)  # Field name made lowercase.
    serialNum = models.CharField(
        max_length=255, null=True, blank=True
    )  # Field name made lowercase.
    urgent = models.IntegerField(null=True, blank=True)
    wontStart = models.IntegerField(null=True, blank=True)  # Field name made lowercase.
    stopped = models.IntegerField(null=True, blank=True)
    strangeSound = models.IntegerField(
        null=True, blank=True
    )  # Field name made lowercase.
    wontReverse = models.IntegerField(
        null=True, blank=True
    )  # Field name made lowercase.
    pistonsStopped = models.IntegerField(
        null=True, blank=True
    )  # Field name made lowercase.
    looseNut = models.IntegerField(null=True, blank=True)  # Field name made lowercase.
    brokenDoorSwitch = models.IntegerField(
        null=True, blank=True
    )  # Field name made lowercase.
    brokenDoor = models.IntegerField(
        null=True, blank=True
    )  # Field name made lowercase.
    brokenKnob = models.IntegerField(
        null=True, blank=True
    )  # Field name made lowercase.
    other = models.IntegerField(null=True, blank=True)
    otherDesc = models.TextField(null=True, blank=True)  # Field name made lowercase.
    dateCreated = models.DateTimeField()  # Field name made lowercase.
    dateModified = models.DateTimeField()  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = "replacementMachineRequest"


class Role(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        managed = False
        db_table = "role"


class RolePermission(models.Model):
    roleId = models.OneToOneField(
        "Role", models.DO_NOTHING, db_column="roleId"
    )  # Field name made lowercase.
    permissionId = models.OneToOneField(
        "Permission", models.DO_NOTHING, db_column="permissionId"
    )  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = "role_permission"


class Rxbestmedspa(models.Model):
    id = models.AutoField(primary_key=True)
    formulaCode = models.CharField(max_length=255)  # Field name made lowercase.
    active = models.IntegerField(default=0)
    dateCreated = models.DateTimeField(
        default="CURRENT_TIMESTAMP"
    )  # Field name made lowercase.
    dateModified = models.DateTimeField(
        null=True, blank=True
    )  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = "rxBestMedSpa"


class Rxbestnumbingdio(models.Model):
    id = models.AutoField(primary_key=True)
    formulaCode = models.CharField(max_length=255)  # Field name made lowercase.
    active = models.IntegerField(default=0)
    dateCreated = models.DateTimeField(
        default="CURRENT_TIMESTAMP"
    )  # Field name made lowercase.
    dateModified = models.DateTimeField(
        null=True, blank=True
    )  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = "rxBestNumbingDio"


class Rxbestpodiatry(models.Model):
    id = models.AutoField(primary_key=True)
    formulaCode = models.CharField(max_length=255)  # Field name made lowercase.
    active = models.IntegerField(default=0)
    dateCreated = models.DateTimeField(
        default="CURRENT_TIMESTAMP"
    )  # Field name made lowercase.
    dateModified = models.DateTimeField(
        null=True, blank=True
    )  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = "rxBestPodiatry"


class Rxbestseller(models.Model):
    id = models.AutoField(primary_key=True)
    formulaCode = models.CharField(max_length=255)  # Field name made lowercase.
    active = models.IntegerField(default=0)
    dateCreated = models.DateTimeField(
        default="CURRENT_TIMESTAMP"
    )  # Field name made lowercase.
    dateModified = models.DateTimeField(
        null=True, blank=True
    )  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = "rxBestSeller"


class RxbestsellerCopy1(models.Model):
    id = models.AutoField(primary_key=True)
    formulaCode = models.CharField(max_length=255)  # Field name made lowercase.
    active = models.IntegerField(default=0)
    dateCreated = models.DateTimeField(
        default="CURRENT_TIMESTAMP"
    )  # Field name made lowercase.
    dateModified = models.DateTimeField(
        null=True, blank=True
    )  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = "rxBestSeller_copy1"


class Rxblt(models.Model):
    id = models.AutoField(primary_key=True)
    formulaCode = models.CharField(max_length=255)  # Field name made lowercase.
    active = models.IntegerField(default=0)
    dateCreated = models.DateTimeField(
        default="CURRENT_TIMESTAMP"
    )  # Field name made lowercase.
    dateModified = models.DateTimeField(
        null=True, blank=True
    )  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = "rxBlt"


class Rxconsent(models.Model):
    id = models.AutoField(primary_key=True)
    salesOrderId = models.ForeignKey(
        "Salesorder", models.DO_NOTHING, db_column="salesOrderId", null=True, blank=True
    )  # Field name made lowercase.
    legalInfoId = models.ForeignKey(
        "Legalinfo", models.DO_NOTHING, db_column="legalInfoId", null=True, blank=True
    )  # Field name made lowercase.
    consentSignatureId = models.ForeignKey(
        "Consentsignature",
        models.DO_NOTHING,
        db_column="consentSignatureId",
        null=True,
        blank=True,
    )  # Field name made lowercase.
    netsuiteId = models.IntegerField()  # Field name made lowercase.
    formulaCode = models.CharField(max_length=255)  # Field name made lowercase.
    dateCreated = models.DateTimeField()  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = "rxConsent"


class Saascontract(models.Model):
    id = models.AutoField(primary_key=True)
    salesUserId = models.ForeignKey(
        "Users", models.DO_NOTHING, db_column="salesUserId", null=True, blank=True
    )  # Field name made lowercase.
    practiceEmail = models.CharField(
        max_length=255, null=True, blank=True
    )  # Field name made lowercase.
    token = models.CharField(max_length=255)
    signed = models.IntegerField(default=0)
    s3Url = models.CharField(
        max_length=255, null=True, blank=True
    )  # Field name made lowercase.
    jsonData = models.TextField()  # Field name made lowercase.
    documentType = models.IntegerField(
        null=True, blank=True
    )  # Field name made lowercase.
    dateTokenSent = models.DateTimeField(
        null=True, blank=True
    )  # Field name made lowercase.
    dateCreated = models.DateTimeField(
        default="CURRENT_TIMESTAMP"
    )  # Field name made lowercase.
    dateModified = models.DateTimeField(
        null=True, blank=True
    )  # Field name made lowercase.
    netsuiteId = models.CharField(
        max_length=255, null=True, blank=True
    )  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = "saasContract"


class Salescontract(models.Model):
    id = models.AutoField(primary_key=True)
    salesUserId = models.ForeignKey(
        "Users", models.DO_NOTHING, db_column="salesUserId"
    )  # Field name made lowercase.
    practiceEmail = models.CharField(
        max_length=255, null=True, blank=True
    )  # Field name made lowercase.
    token = models.CharField(max_length=255)
    signed = models.IntegerField(default=0)
    s3Url = models.CharField(
        max_length=255, null=True, blank=True
    )  # Field name made lowercase.
    jsonData = models.TextField(null=True, blank=True)  # Field name made lowercase.
    documentType = models.IntegerField(
        null=True, blank=True
    )  # Field name made lowercase.
    dateTokenSent = models.DateTimeField(
        null=True, blank=True
    )  # Field name made lowercase.
    dateCreated = models.DateTimeField()  # Field name made lowercase.
    dateModified = models.DateTimeField(
        null=True, blank=True
    )  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = "salesContract"


class Salesorder(models.Model):
    id = models.AutoField(primary_key=True)
    ownerId = models.IntegerField()  # Field name made lowercase.
    legalInfoId = models.ForeignKey(
        "Legalinfo", models.DO_NOTHING, db_column="legalInfoId", null=True, blank=True
    )  # Field name made lowercase.
    consentSignatureId = models.ForeignKey(
        "Consentsignature",
        models.DO_NOTHING,
        db_column="consentSignatureId",
        null=True,
        blank=True,
    )  # Field name made lowercase.
    signerIp = models.CharField(
        max_length=255, default=""
    )  # Field name made lowercase.
    isTester = models.IntegerField(default=0)  # Field name made lowercase.
    prop65 = models.IntegerField(default=0)
    discountTier = models.CharField(
        max_length=255, null=True, blank=True
    )  # Field name made lowercase.
    token = models.CharField(max_length=255)
    approved = models.IntegerField(default=0)
    showTotalPrice = models.IntegerField(default=0)  # Field name made lowercase.
    showTotalUnits = models.IntegerField(default=0)  # Field name made lowercase.
    showPrice = models.IntegerField(default=0)  # Field name made lowercase.
    showUnits = models.IntegerField(default=0)  # Field name made lowercase.
    dateTokenSent = models.DateTimeField(
        null=True, blank=True
    )  # Field name made lowercase.
    dateCreated = models.DateTimeField()  # Field name made lowercase.
    dateModified = models.DateTimeField(
        default="CURRENT_TIMESTAMP"
    )  # Field name made lowercase.
    quoteId = models.IntegerField(null=True, blank=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = "salesOrder"


class Salesorderproduct(models.Model):
    id = models.AutoField(primary_key=True)
    salesOrderId = models.ForeignKey(
        "Salesorder", models.DO_NOTHING, db_column="salesOrderId", null=True, blank=True
    )  # Field name made lowercase.
    productType = models.CharField(
        max_length=255, null=True, blank=True
    )  # Field name made lowercase.
    productCode = models.CharField(
        max_length=255, null=True, blank=True
    )  # Field name made lowercase.
    quantity = models.IntegerField(default=0)
    displayName = models.CharField(
        max_length=255, null=True, blank=True
    )  # Field name made lowercase.
    volumeDiscount = models.FloatField(
        null=True, blank=True
    )  # Field name made lowercase.
    lineDiscount = models.FloatField(
        null=True, blank=True
    )  # Field name made lowercase.
    price = models.FloatField(null=True, blank=True)
    sku = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        managed = False
        db_table = "salesOrderProduct"


class Salesresource(models.Model):
    id = models.AutoField(primary_key=True)
    category = models.IntegerField()
    title = models.CharField(max_length=255)
    summary = models.CharField(max_length=255, null=True, blank=True)
    url = models.CharField(max_length=255, null=True, blank=True)
    s3Url = models.CharField(
        max_length=255, null=True, blank=True
    )  # Field name made lowercase.
    comments = models.CharField(max_length=255, null=True, blank=True)
    dateCreated = models.DateTimeField()  # Field name made lowercase.
    dateModified = models.DateTimeField()  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = "salesResource"


class Salesresourcecategory(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    active = models.IntegerField()
    dateCreated = models.DateTimeField(
        default="CURRENT_TIMESTAMP"
    )  # Field name made lowercase.
    dateModified = models.DateTimeField(
        null=True, blank=True
    )  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = "salesResourceCategory"


class Shipment(models.Model):
    id = models.AutoField(primary_key=True)
    netsuiteId = models.IntegerField()  # Field name made lowercase.
    companyId = models.IntegerField()  # Field name made lowercase.
    officeId = models.ForeignKey(
        "Office", models.DO_NOTHING, db_column="officeId", null=True, blank=True
    )  # Field name made lowercase.
    formulaCode = models.CharField(
        max_length=255, null=True, blank=True
    )  # Field name made lowercase.
    sku = models.CharField(max_length=255, null=True, blank=True)
    netsuiteName = models.CharField(max_length=255)  # Field name made lowercase.
    companyName = models.CharField(max_length=255)  # Field name made lowercase.
    formulaName = models.CharField(
        max_length=255, null=True, blank=True
    )  # Field name made lowercase.
    productFullName = models.CharField(
        max_length=255, null=True, blank=True
    )  # Field name made lowercase.
    productBaseQuantity = models.IntegerField(
        null=True, blank=True
    )  # Field name made lowercase.
    caseQuantity = models.IntegerField(
        null=True, blank=True
    )  # Field name made lowercase.
    productUnitsFulfilled = models.CharField(
        max_length=255, null=True, blank=True
    )  # Field name made lowercase.
    fulfillmentDate = models.DateField()  # Field name made lowercase.
    shippingAddress = models.CharField(
        max_length=255, null=True, blank=True
    )  # Field name made lowercase.
    shippingZip = models.CharField(
        max_length=255, null=True, blank=True
    )  # Field name made lowercase.
    physicianOnOrder = models.CharField(
        max_length=255, null=True, blank=True
    )  # Field name made lowercase.
    isLoaded = models.IntegerField(default=0)  # Field name made lowercase.
    lotNumber = models.CharField(
        max_length=255, null=True, blank=True
    )  # Field name made lowercase.
    dateCreated = models.DateTimeField()  # Field name made lowercase.
    nsShipmentId = models.IntegerField(
        null=True, blank=True
    )  # Field name made lowercase.
    nsItemId = models.IntegerField(null=True, blank=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = "shipment"


class Skincarecorrector(models.Model):
    id = models.AutoField(primary_key=True)
    netsuiteId = models.IntegerField()  # Field name made lowercase.
    officeId = models.IntegerField()  # Field name made lowercase.
    officeName = models.CharField(max_length=255)  # Field name made lowercase.
    userId = models.IntegerField()  # Field name made lowercase.
    userName = models.CharField(max_length=255)  # Field name made lowercase.
    physicianName = models.CharField(max_length=255)  # Field name made lowercase.
    orderNum = models.CharField(max_length=255)  # Field name made lowercase.
    itemNum = models.CharField(max_length=255)  # Field name made lowercase.
    lotNum = models.CharField(
        max_length=255, null=True, blank=True
    )  # Field name made lowercase.
    numUnits = models.IntegerField(null=True, blank=True)  # Field name made lowercase.
    leaked = models.IntegerField(null=True, blank=True)
    defectivePackaging = models.IntegerField(
        null=True, blank=True
    )  # Field name made lowercase.
    shipping = models.IntegerField(null=True, blank=True)
    label = models.IntegerField(null=True, blank=True)
    product = models.IntegerField(null=True, blank=True)
    productDesc = models.TextField(null=True, blank=True)  # Field name made lowercase.
    other = models.IntegerField(null=True, blank=True)
    otherDesc = models.TextField(null=True, blank=True)  # Field name made lowercase.
    dateCreated = models.DateTimeField()  # Field name made lowercase.
    dateModified = models.DateTimeField()  # Field name made lowercase.
    complaintSource = models.CharField(
        max_length=255, null=True, blank=True
    )  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = "skincareCorrector"


class Sknvcosmeticleaflet(models.Model):
    id = models.AutoField(primary_key=True)
    baseCode = models.CharField(max_length=255)  # Field name made lowercase.
    title = models.CharField(max_length=255)
    mainImageUrl = models.CharField(max_length=255)  # Field name made lowercase.
    intro = models.TextField()
    indications = models.TextField()
    keyIngredients = models.TextField(
        null=True, blank=True
    )  # Field name made lowercase.
    proTips = models.TextField(null=True, blank=True)  # Field name made lowercase.
    sizesAvailable = models.TextField()  # Field name made lowercase.
    fullIngredients = models.TextField(
        null=True, blank=True
    )  # Field name made lowercase.
    activeIngredients = models.TextField(
        null=True, blank=True
    )  # Field name made lowercase.
    inactiveIngredients = models.TextField(
        null=True, blank=True
    )  # Field name made lowercase.
    peelComposition = models.TextField(
        null=True, blank=True
    )  # Field name made lowercase.
    dateCreated = models.DateTimeField(
        default="CURRENT_TIMESTAMP"
    )  # Field name made lowercase.
    dateModified = models.DateTimeField(
        null=True, blank=True
    )  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = "sknvCosmeticLeaflet"


class Sknvrxleaflet(models.Model):
    id = models.AutoField(primary_key=True)
    formulaCode = models.CharField(max_length=255)  # Field name made lowercase.
    formulaNdc = models.CharField(max_length=255)  # Field name made lowercase.
    proprietaryName = models.CharField(max_length=255)  # Field name made lowercase.
    formulaName = models.CharField(max_length=255)  # Field name made lowercase.
    content_en = models.TextField()
    content_es = models.TextField()
    dateCreated = models.DateTimeField(
        default="CURRENT_TIMESTAMP"
    )  # Field name made lowercase.
    dateModified = models.DateTimeField(
        null=True, blank=True
    )  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = "sknvRxLeaflet"
        unique_together = ("formulaCode", "formulaNdc", "proprietaryName")


class Smscontract(models.Model):
    id = models.AutoField(primary_key=True)
    salesUserId = models.ForeignKey(
        "Users", models.DO_NOTHING, db_column="salesUserId", null=True, blank=True
    )  # Field name made lowercase.
    practiceEmail = models.CharField(
        max_length=255, null=True, blank=True
    )  # Field name made lowercase.
    token = models.CharField(max_length=255)
    signed = models.IntegerField(default=0)
    s3Url = models.CharField(
        max_length=255, null=True, blank=True
    )  # Field name made lowercase.
    jsonData = models.TextField()  # Field name made lowercase.
    documentType = models.IntegerField(
        null=True, blank=True
    )  # Field name made lowercase.
    dateTokenSent = models.DateTimeField(
        null=True, blank=True
    )  # Field name made lowercase.
    dateCreated = models.DateTimeField(
        default="CURRENT_TIMESTAMP"
    )  # Field name made lowercase.
    dateModified = models.DateTimeField(
        null=True, blank=True
    )  # Field name made lowercase.
    w9Id = models.IntegerField(null=True, blank=True)  # Field name made lowercase.
    fredId = models.IntegerField(null=True, blank=True)  # Field name made lowercase.
    netsuiteId = models.CharField(
        max_length=255, null=True, blank=True
    )  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = "smsContract"


class Subelitecontract(models.Model):
    id = models.AutoField(primary_key=True)
    salesUserId = models.ForeignKey(
        "Users", models.DO_NOTHING, db_column="salesUserId", null=True, blank=True
    )  # Field name made lowercase.
    practiceEmail = models.CharField(
        max_length=255, null=True, blank=True
    )  # Field name made lowercase.
    token = models.CharField(max_length=255)
    signed = models.IntegerField(default=0)
    s3Url = models.CharField(
        max_length=255, null=True, blank=True
    )  # Field name made lowercase.
    jsonData = models.TextField()  # Field name made lowercase.
    documentType = models.IntegerField(
        null=True, blank=True
    )  # Field name made lowercase.
    dateTokenSent = models.DateTimeField(
        null=True, blank=True
    )  # Field name made lowercase.
    dateCreated = models.DateTimeField(
        default="CURRENT_TIMESTAMP"
    )  # Field name made lowercase.
    dateModified = models.DateTimeField(
        null=True, blank=True
    )  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = "subEliteContract"


class Subelitepluscontract(models.Model):
    id = models.AutoField(primary_key=True)
    salesUserId = models.ForeignKey(
        "Users", models.DO_NOTHING, db_column="salesUserId", null=True, blank=True
    )  # Field name made lowercase.
    practiceEmail = models.CharField(
        max_length=255, null=True, blank=True
    )  # Field name made lowercase.
    token = models.CharField(max_length=255)
    signed = models.IntegerField(default=0)
    s3Url = models.CharField(
        max_length=255, null=True, blank=True
    )  # Field name made lowercase.
    jsonData = models.TextField()  # Field name made lowercase.
    documentType = models.IntegerField(
        null=True, blank=True
    )  # Field name made lowercase.
    dateTokenSent = models.DateTimeField(
        null=True, blank=True
    )  # Field name made lowercase.
    dateCreated = models.DateTimeField(
        default="CURRENT_TIMESTAMP"
    )  # Field name made lowercase.
    dateModified = models.DateTimeField(
        null=True, blank=True
    )  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = "subElitePlusContract"


class Token(models.Model):
    id = models.AutoField(primary_key=True)
    userId = models.ForeignKey(
        "Users", models.DO_NOTHING, db_column="userId"
    )  # Field name made lowercase.
    token = models.CharField(max_length=255)
    token_type = models.CharField(max_length=255, null=True, blank=True)
    time_created = models.IntegerField()

    class Meta:
        managed = False
        db_table = "token"


class Totaladl(models.Model):
    id = models.AutoField(primary_key=True)
    office_id = models.IntegerField()
    num_dispenses = models.IntegerField()

    class Meta:
        managed = False
        db_table = "totalADL"


class Tsacontract(models.Model):
    id = models.AutoField(primary_key=True)
    salesUserId = models.ForeignKey(
        "Users", models.DO_NOTHING, db_column="salesUserId", null=True, blank=True
    )  # Field name made lowercase.
    practiceEmail = models.CharField(
        max_length=255, null=True, blank=True
    )  # Field name made lowercase.
    token = models.CharField(max_length=255)
    signed = models.IntegerField(default=0)
    s3Url = models.CharField(
        max_length=255, null=True, blank=True
    )  # Field name made lowercase.
    jsonData = models.TextField()  # Field name made lowercase.
    documentType = models.IntegerField(
        null=True, blank=True
    )  # Field name made lowercase.
    dateTokenSent = models.DateTimeField(
        null=True, blank=True
    )  # Field name made lowercase.
    dateCreated = models.DateTimeField(
        default="CURRENT_TIMESTAMP"
    )  # Field name made lowercase.
    dateModified = models.DateTimeField(
        null=True, blank=True
    )  # Field name made lowercase.
    nsId = models.IntegerField(null=True, blank=True)  # Field name made lowercase.
    fredId = models.IntegerField(null=True, blank=True)  # Field name made lowercase.
    w9Id = models.IntegerField(null=True, blank=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = "tsaContract"


class Usercompany(models.Model):
    userId = models.OneToOneField(
        "Users", models.DO_NOTHING, db_column="userId"
    )  # Field name made lowercase.
    companyId = models.OneToOneField(
        "Company", models.DO_NOTHING, db_column="companyId"
    )  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = "userCompany"


class Userhierarchy(models.Model):
    parentId = models.OneToOneField(
        "Users", models.DO_NOTHING, db_column="parentId", primary_key=True
    )  # Field name made lowercase.
    childId = models.OneToOneField(
        "Users", models.DO_NOTHING, db_column="childId", related_name="childId"
    )  # Field name made lowercase.
    dateCreated = models.DateTimeField()  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = "userHierarchy"


class Usermeta(models.Model):
    userId = models.OneToOneField(
        "Users", models.DO_NOTHING, db_column="userId", primary_key=True
    )  # Field name made lowercase.
    name = models.CharField(max_length=255, null=True, blank=True)
    email = models.CharField(max_length=255, null=True, blank=True)
    reminderOptOut = models.IntegerField(default=0)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = "userMeta"


class Useroffice(models.Model):
    userId = models.OneToOneField(
        "Users", models.DO_NOTHING, db_column="userId", primary_key=True
    )  # Field name made lowercase.
    officeId = models.OneToOneField(
        "Office", models.DO_NOTHING, db_column="officeId"
    )  # Field name made lowercase.
    isPrimary = models.IntegerField(null=True, blank=True)  # Field name made lowercase.
    roleId = models.IntegerField(null=True, blank=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = "userOffice"


class Users(models.Model):
    id = models.AutoField(primary_key=True)
    roleId = models.ForeignKey(
        "Role", models.DO_NOTHING, db_column="roleId", null=True, blank=True
    )  # Field name made lowercase.
    email = models.BinaryField()
    emailHash = models.CharField(
        max_length=255, null=True, blank=True
    )  # Field name made lowercase.
    pass_field = models.CharField(
        max_length=255, db_column="pass"
    )  # Field renamed because it was a Python reserved word.
    name = models.BinaryField(null=True, blank=True)
    status = models.IntegerField(default=0)
    dateCreated = models.DateTimeField()  # Field name made lowercase.
    dateModified = models.DateTimeField()  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = "users"


class W9(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255, null=True, blank=True)
    businessName = models.CharField(
        max_length=255, null=True, blank=True
    )  # Field name made lowercase.
    taxClass = models.CharField(
        max_length=255, null=True, blank=True
    )  # Field name made lowercase.
    taxClassOther = models.CharField(
        max_length=255, null=True, blank=True
    )  # Field name made lowercase.
    exemptPayee = models.CharField(
        max_length=255, null=True, blank=True
    )  # Field name made lowercase.
    exemptFatca = models.CharField(
        max_length=255, null=True, blank=True
    )  # Field name made lowercase.
    address = models.CharField(max_length=255, null=True, blank=True)
    cityStateZip = models.CharField(
        max_length=255, null=True, blank=True
    )  # Field name made lowercase.
    accountNumbers = models.CharField(
        max_length=255, null=True, blank=True
    )  # Field name made lowercase.
    requesterNameAddress = models.CharField(
        max_length=255, null=True, blank=True
    )  # Field name made lowercase.
    tin = models.BinaryField(null=True, blank=True)
    s3Url = models.CharField(
        max_length=255, null=True, blank=True
    )  # Field name made lowercase.
    dateCreated = models.DateTimeField(
        default="CURRENT_TIMESTAMP"
    )  # Field name made lowercase.
    dateModified = models.DateTimeField(
        null=True, blank=True
    )  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = "w9"
