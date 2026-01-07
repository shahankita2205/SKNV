# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models
from decimal import Decimal


class Address(models.Model):
    address1 = models.TextField(blank=True, null=True)
    address2 = models.TextField(blank=True, null=True)
    city = models.TextField(blank=True, null=True)
    state = models.TextField(blank=True, null=True)
    zip = models.TextField(blank=True, null=True)
    created = models.DateTimeField()
    type = models.TextField(blank=True, null=True)
    zip4 = models.CharField(max_length=5, blank=True, null=True)
    latlong = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = "address"


class Allergens(models.Model):
    wp_id = models.IntegerField(blank=True, null=True)
    allergen_irritant = models.CharField(max_length=1024, blank=True, null=True)
    concern = models.TextField(blank=True, null=True)
    citations = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = "allergens"


class AuditRefill(models.Model):
    rxfill_id = models.IntegerField()
    changed = models.DateTimeField()
    action = models.TextField()
    column_name = models.TextField()
    old_value = models.TextField(blank=True, null=True)
    new_value = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = "audit_refill"


class AuditTable(models.Model):
    aud_id = models.AutoField(primary_key=True)
    action = models.TextField(blank=True, null=True)
    table_name = models.TextField(blank=True, null=True)
    action_tstz = models.DateTimeField(blank=True, null=True)
    old_data = models.JSONField(blank=True, null=True)
    new_data = models.JSONField(blank=True, null=True)
    user_name = models.TextField(blank=True, null=True)
    sql_stmt = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = "audit_table"


class Automatedtasks(models.Model):
    repid = models.IntegerField()
    stateid = models.IntegerField()
    type = models.CharField(max_length=255)
    created = models.DateTimeField()
    modified = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = "automatedtasks"


class Deletedoffice(models.Model):
    officeid = models.IntegerField(db_column="officeId")  # Field name made lowercase.
    details = models.TextField()
    created = models.DateTimeField()

    class Meta:
        managed = False
        db_table = "deletedOffice"


class Device(models.Model):
    officeid = models.IntegerField(blank=True, null=True)
    deviceid = models.TextField(blank=True, null=True)
    serial = models.TextField(blank=True, null=True)
    created = models.DateTimeField()

    class Meta:
        managed = False
        db_table = "device"


class Dispenselogs(models.Model):
    dispenselogid = models.AutoField(
        db_column="dispenseLogId", primary_key=True
    )  # Field name made lowercase.
    ndcid = models.ForeignKey(
        "Medication", models.DO_NOTHING, db_column="ndcId", to_field="ndc"
    )  # Field name made lowercase.
    rxid = models.ForeignKey(
        "Rx", models.DO_NOTHING, db_column="rxId"
    )  # Field name made lowercase.
    lotnumber = models.CharField(
        db_column="lotNumber", max_length=255
    )  # Field name made lowercase.
    expiration = models.DateField()
    quantity = models.IntegerField()
    pharmacistid = models.ForeignKey(
        "Users", models.DO_NOTHING, db_column="pharmacistId"
    )  # Field name made lowercase.
    patientid = models.ForeignKey(
        "Patient", models.DO_NOTHING, db_column="patientId"
    )  # Field name made lowercase.
    substatusid = models.ForeignKey(
        "Substatus", models.DO_NOTHING, db_column="subStatusId"
    )  # Field name made lowercase.
    additionalnotes = models.TextField(
        db_column="additionalNotes", blank=True, null=True
    )  # Field name made lowercase.
    createdby = models.ForeignKey(
        "Users",
        models.DO_NOTHING,
        db_column="createdBy",
        related_name="dispenselogs_createdby_set",
    )  # Field name made lowercase.
    modifiedby = models.ForeignKey(
        "Users",
        models.DO_NOTHING,
        db_column="modifiedBy",
        related_name="dispenselogs_modifiedby_set",
        blank=True,
        null=True,
    )  # Field name made lowercase.
    datecreated = models.DateTimeField(
        db_column="dateCreated"
    )  # Field name made lowercase.
    datemodified = models.DateTimeField(
        db_column="dateModified", blank=True, null=True
    )  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = "dispenseLogs"


# class Doctor(models.Model):
#     name = models.TextField(blank=True, null=True)
#     phone = models.TextField(blank=True, null=True)
#     email = models.TextField(blank=True, null=True)
#     dea = models.TextField(blank=True, null=True)
#     npi = models.TextField(blank=True, null=True)
#     spi = models.TextField(blank=True, null=True)
#     created = models.DateTimeField()
#     prefix = models.TextField(blank=True, null=True)
#     firstname = models.TextField(blank=True, null=True)
#     middlename = models.TextField(blank=True, null=True)
#     lastname = models.TextField(blank=True, null=True)
#     suffix = models.TextField(blank=True, null=True)
#     pin = models.IntegerField(blank=True, null=True)
#     pharmetikaid = models.IntegerField(blank=True, null=True)
#     approval = models.BooleanField()

#     class Meta:
#         managed = False
#         db_table = "doctor"


class Featureflag(models.Model):
    featureid = models.AutoField(
        db_column="featureId", primary_key=True
    )  # Field name made lowercase.
    name = models.CharField(max_length=255)
    description = models.CharField(max_length=255)
    active = models.BooleanField()
    createdby = models.ForeignKey(
        "Users", models.DO_NOTHING, db_column="createdBy"
    )  # Field name made lowercase.
    modifiedby = models.ForeignKey(
        "Users",
        models.DO_NOTHING,
        db_column="modifiedBy",
        related_name="featureflag_modifiedby_set",
        blank=True,
        null=True,
    )  # Field name made lowercase.
    startdate = models.DateTimeField(
        db_column="startDate", blank=True, null=True
    )  # Field name made lowercase.
    enddate = models.DateTimeField(
        db_column="endDate", blank=True, null=True
    )  # Field name made lowercase.
    datecreated = models.DateTimeField(
        db_column="dateCreated"
    )  # Field name made lowercase.
    datemodified = models.DateTimeField(
        db_column="dateModified", blank=True, null=True
    )  # Field name made lowercase.
    title = models.CharField(max_length=255, blank=True, null=True)
    dailylimit = models.IntegerField(
        db_column="dailyLimit", blank=True, null=True
    )  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = "featureFlag"


class Fee(models.Model):
    fee = models.IntegerField(blank=True, null=True)
    status = models.IntegerField(blank=True, null=True)
    level = models.IntegerField(blank=True, null=True)
    created = models.DateTimeField()
    ndc = models.CharField(unique=True, max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = "fee"


class Fulfillmentpartners(models.Model):
    fpid = models.AutoField(
        db_column="fpId", primary_key=True
    )  # Field name made lowercase.
    name = models.CharField(max_length=255)
    description = models.CharField(max_length=255)
    datecreated = models.DateTimeField(
        db_column="dateCreated"
    )  # Field name made lowercase.
    datemodified = models.DateTimeField(
        db_column="dateModified", blank=True, null=True
    )  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = "fulfillmentPartners"


class Ihflogs(models.Model):
    ihfid = models.AutoField(
        db_column="ihfId", primary_key=True
    )  # Field name made lowercase.
    rxid = models.ForeignKey(
        "Rx", models.DO_NOTHING, db_column="rxId"
    )  # Field name made lowercase.
    fillid = models.ForeignKey(
        "Rxfill", models.DO_NOTHING, db_column="fillId"
    )  # Field name made lowercase.
    patientid = models.ForeignKey(
        "Patient", models.DO_NOTHING, db_column="patientId"
    )  # Field name made lowercase.
    officeid = models.ForeignKey(
        "Office", models.DO_NOTHING, db_column="officeId"
    )  # Field name made lowercase.
    fpid = models.ForeignKey(
        Fulfillmentpartners, models.DO_NOTHING, db_column="fpId"
    )  # Field name made lowercase.
    datecreated = models.DateTimeField(
        db_column="dateCreated"
    )  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = "ihfLogs"


class Inhouseeligibility(models.Model):
    iheid = models.AutoField(
        db_column="iheId", primary_key=True
    )  # Field name made lowercase.
    stateid = models.ForeignKey(
        "State", models.DO_NOTHING, db_column="stateId"
    )  # Field name made lowercase.
    ndcid = models.CharField(
        db_column="ndcId", max_length=255
    )  # Field name made lowercase.
    createdby = models.ForeignKey(
        "Users", models.DO_NOTHING, db_column="createdBy"
    )  # Field name made lowercase.
    modifiedby = models.ForeignKey(
        "Users",
        models.DO_NOTHING,
        db_column="modifiedBy",
        related_name="inhouseeligibility_modifiedby_set",
        blank=True,
        null=True,
    )  # Field name made lowercase.
    datecreated = models.DateTimeField(
        db_column="dateCreated"
    )  # Field name made lowercase.
    datemodified = models.DateTimeField(
        db_column="dateModified", blank=True, null=True
    )  # Field name made lowercase.
    active = models.BooleanField()

    class Meta:
        managed = False
        db_table = "inHouseEligibility"
        unique_together = (("stateid", "ndcid"),)


class Ingredient(models.Model):
    id = models.IntegerField(primary_key=True)
    slug = models.CharField(max_length=50, blank=True, null=True)
    ingredient = models.CharField(max_length=50, blank=True, null=True)
    description = models.CharField(max_length=50, blank=True, null=True)
    concern = models.CharField(max_length=256, blank=True, null=True)
    citations = models.CharField(max_length=8192, blank=True, null=True)

    class Meta:
        managed = False
        db_table = "ingredient"


class Inventory(models.Model):
    ndc = models.TextField(blank=True, null=True)
    lot = models.TextField(blank=True, null=True)
    bud = models.TextField(blank=True, null=True)
    qty = models.IntegerField(blank=True, null=True)
    warehouse = models.TextField(blank=True, null=True)
    status = models.TextField(blank=True, null=True)
    created = models.DateTimeField()

    class Meta:
        managed = False
        db_table = "inventory"


class Logs(models.Model):
    userid = models.TextField(blank=True, null=True)
    recordid = models.TextField(blank=True, null=True)
    recordtype = models.TextField(blank=True, null=True)
    msg = models.TextField(blank=True, null=True)
    type = models.TextField(blank=True, null=True)
    created = models.DateTimeField()
    rxid = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = "logs"


class Logspatient(models.Model):
    userid = models.TextField(blank=True, null=True)
    msg = models.TextField(blank=True, null=True)
    patientid = models.IntegerField(blank=True, null=True)
    created = models.DateTimeField()

    class Meta:
        managed = False
        db_table = "logspatient"


class Logsrx(models.Model):
    userid = models.TextField(blank=True, null=True)
    msg = models.TextField(blank=True, null=True)
    rxid = models.IntegerField(blank=True, null=True)
    created = models.DateTimeField()

    class Meta:
        managed = False
        db_table = "logsrx"


class Lots(models.Model):
    lotnumber = models.CharField(
        db_column="lotNumber", max_length=20, blank=True, null=True
    )  # Field name made lowercase.
    formulacode = models.CharField(
        db_column="formulaCode", max_length=20, blank=True, null=True
    )  # Field name made lowercase.
    expirationdate = models.DateField(
        db_column="expirationDate", blank=True, null=True
    )  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = "lots"


class Medalignments(models.Model):
    othermedication = models.ForeignKey(
        "Othermedication",
        models.DO_NOTHING,
        db_column="othermedication",
        blank=True,
        null=True,
    )
    medication = models.IntegerField()
    ndc = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = "medalignments"


class Medication(models.Model):
    formula = models.TextField(blank=True, null=True)
    formulacode = models.TextField(blank=True, null=True)
    ndc = models.TextField(unique=True, blank=True, null=True)
    dosage = models.TextField(blank=True, null=True)
    size = models.TextField(blank=True, null=True)
    created = models.DateTimeField()
    mpn = models.TextField(blank=True, null=True)
    formulashort = models.TextField(blank=True, null=True)
    ingr = models.TextField(blank=True, null=True)
    hwhid = models.TextField(blank=True, null=True)
    nsid = models.IntegerField(blank=True, null=True)
    status = models.TextField(blank=True, null=True)
    blacklist = models.TextField(blank=True, null=True)
    brand_name = models.TextField(blank=True, null=True)
    indication = models.CharField(max_length=255, blank=True, null=True)
    key_inactives = models.TextField(blank=True, null=True)
    packaging = models.CharField(max_length=255, blank=True, null=True)
    dh_enabled = models.BooleanField(blank=True, null=True)
    most_prescribed = models.BooleanField(blank=True, null=True)
    ingredients_not_included = models.TextField(blank=True, null=True)
    activeingr = models.TextField(blank=True, null=True)
    inactiveingr = models.TextField(blank=True, null=True)
    allowbulk = models.BooleanField()

    class Meta:
        managed = False
        db_table = "medication"


class Medleaflet(models.Model):
    ndc = models.CharField(max_length=255, blank=True, null=True)
    content_en = models.TextField(blank=True, null=True)
    content_es = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = "medleaflet"


class NdcExchange(models.Model):
    inboundndc = models.TextField()
    outboundndc = models.TextField()
    status = models.TextField(blank=True, null=True)
    created = models.DateTimeField(blank=True, null=True)
    updated = models.DateTimeField(blank=True, null=True)
    deleted = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = "ndc_exchange"


class Office(models.Model):
    addressid = models.IntegerField(blank=True, null=True)
    name = models.TextField(blank=True, null=True)
    created = models.DateTimeField()
    locationid = models.TextField(blank=True, null=True)
    sales = models.TextField(blank=True, null=True)
    altaddress = models.TextField(blank=True, null=True)
    users = models.TextField(blank=True, null=True)
    logo = models.TextField(blank=True, null=True)
    dhenabled = models.BooleanField(blank=True, null=True)
    allowmsgconsult = models.BooleanField(blank=True, null=True)
    allowvideoconsult = models.BooleanField(blank=True, null=True)
    allowmsgfreeform = models.BooleanField(blank=True, null=True)
    videoconsultfee = models.IntegerField(blank=True, null=True)
    msgconsultfee = models.IntegerField(blank=True, null=True)
    displayname = models.TextField(blank=True, null=True)
    netsuiteid = models.IntegerField(blank=True, null=True)
    allowchatconsult = models.BooleanField(blank=True, null=True)
    chatconsultfee = models.IntegerField(blank=True, null=True)
    email = models.CharField(max_length=8192, blank=True, null=True)
    acct = models.TextField(blank=True, null=True)
    route = models.CharField(max_length=8192, blank=True, null=True)
    officeemail = models.CharField(max_length=8192, blank=True, null=True)
    primaryemail = models.CharField(max_length=8192, blank=True, null=True)
    delivermode = models.CharField(max_length=8192, blank=True, null=True)
    suppresssknvmessaging = models.BooleanField(blank=True, null=True)
    suppressrefills = models.BooleanField(blank=True, null=True)
    inofficedispense = models.BooleanField(blank=True, null=True)
    allownewpatientreqconsult = models.BooleanField(blank=True, null=True)
    officeslug = models.CharField(max_length=8192, blank=True, null=True)
    vendorid = models.IntegerField(blank=True, null=True)
    modified = models.DateTimeField(blank=True, null=True)
    synced = models.DateTimeField(blank=True, null=True)
    dtcstates = models.TextField(blank=True, null=True)
    suppresspairings = models.BooleanField(blank=True, null=True)
    officetypeid = models.ForeignKey(
        "Officetype", models.DO_NOTHING, db_column="officetypeid", blank=True, null=True
    )
    officeagreementtypeid = models.IntegerField(blank=True, null=True)
    note = models.TextField(blank=True, null=True)
    virtualinventoryenabled = models.BooleanField(default=False)
    vi_status = models.IntegerField(blank=True, null=True)
    replenishmentoptout = models.BooleanField(default=False)
    parentid = models.IntegerField(blank=True, null=True)
    vifeeshippinghandling = models.FloatField(default=8.0, blank=True, null=True)
    vifeeservice = models.FloatField(default=5.0, blank=True, null=True)
    viproceedstype = models.IntegerField(blank=True, null=True)
    vivendorid = models.IntegerField(blank=True, null=True)
    vicontactid = models.IntegerField(blank=True, null=True)
    vicontracttoken = models.TextField(blank=True, null=True)
    dio2 = models.BooleanField(default=False)

    class Meta:
        managed = False
        db_table = "office"


class Officeagreementtype(models.Model):
    id = models.AutoField(primary_key=True)
    agreementname = models.TextField(
        db_column="agreementName"
    )  # Field name made lowercase.
    agreementdescription = models.TextField(
        db_column="agreementDescription", blank=True, null=True
    )  # Field name made lowercase.
    createdat = models.DateTimeField(
        db_column="createdAt"
    )  # Field name made lowercase.
    modifiedat = models.DateTimeField(
        db_column="modifiedAt"
    )  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = "officeAgreementType"


class Officehistory(models.Model):
    id = models.AutoField(primary_key=True)
    officeid = models.IntegerField(db_column="officeId")  # Field name made lowercase.
    triggeredaction = models.TextField(
        db_column="triggeredAction", blank=True, null=True
    )  # Field name made lowercase.
    datelogged = models.DateTimeField(
        db_column="dateLogged", blank=True, null=True
    )  # Field name made lowercase.
    olddata = models.JSONField(
        db_column="oldData", blank=True, null=True
    )  # Field name made lowercase.
    newdata = models.JSONField(
        db_column="newData", blank=True, null=True
    )  # Field name made lowercase.
    userid = models.IntegerField(
        db_column="userId", blank=True, null=True
    )  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = "officeHistory"


class Officeinfo(models.Model):
    officeid = models.ForeignKey(Office, models.DO_NOTHING, db_column="officeid")
    featuredskincare = models.TextField(blank=True, null=True)
    abouthtml = models.TextField(blank=True, null=True)
    herobackground = models.TextField(blank=True, null=True)
    avatartoshow = models.TextField(blank=True, null=True)
    officeimage = models.TextField(blank=True, null=True)
    created = models.DateTimeField()
    modified = models.DateTimeField(blank=True, null=True)
    fax = models.TextField(blank=True, null=True)
    primaryphone = models.TextField(blank=True, null=True)
    reminderopt = models.BooleanField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = "officeinfo"


class Othermedication(models.Model):
    brand_ndc = models.TextField(blank=True, null=True)
    branded_name = models.CharField(max_length=255, blank=True, null=True)
    applicant = models.CharField(max_length=255, blank=True, null=True)
    api = models.CharField(max_length=255, blank=True, null=True)
    percentage = models.CharField(max_length=255, blank=True, null=True)
    dosage = models.CharField(max_length=255, blank=True, null=True)
    condition = models.CharField(max_length=255, blank=True, null=True)
    allergen_irritant = models.CharField(max_length=255, blank=True, null=True)
    sknv_ndc = models.CharField(max_length=255, blank=True, null=True)
    sknv_suggested_formulations = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = "othermedication"


class Outofstockmedication(models.Model):
    dateadded = models.DateField(blank=True, null=True)
    estimatedinstockdate = models.DateField(blank=True, null=True)
    isdeleted = models.BooleanField()
    medicationid = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = "outofstockmedication"


class Patient(models.Model):
    addressid = models.IntegerField(blank=True, null=True)
    name = models.TextField(blank=True, null=True)
    dob = models.TextField(blank=True, null=True)
    gender = models.TextField(blank=True, null=True)
    phone = models.TextField(blank=True, null=True)
    email = models.TextField(blank=True, null=True)
    allergies = models.TextField(blank=True, null=True)
    otherdrugs = models.TextField(blank=True, null=True)
    otherinfo = models.TextField(blank=True, null=True)
    created = models.DateTimeField()
    pregnant = models.BooleanField(blank=True, null=True)
    prefix = models.TextField(blank=True, null=True)
    firstname = models.TextField(blank=True, null=True)
    middlename = models.TextField(blank=True, null=True)
    lastname = models.TextField(blank=True, null=True)
    suffix = models.TextField(blank=True, null=True)
    userid = models.IntegerField(blank=True, null=True)
    pharmetikaid = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = "patient"


class Patientlogs(models.Model):
    patientid = models.IntegerField()
    columnname = models.CharField(max_length=255)
    previousvalue = models.TextField(blank=True, null=True)
    newvalue = models.TextField(blank=True, null=True)
    created = models.DateTimeField(blank=True, null=True)
    updatedby = models.CharField(max_length=255, blank=True, null=True)
    url = models.CharField(max_length=255, blank=True, null=True)
    action = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = "patientlogs"


class Patientmeta(models.Model):
    addressid = models.IntegerField(blank=True, null=True)
    qty = models.IntegerField(blank=True, null=True)
    dob = models.TextField(blank=True, null=True)
    phone = models.TextField(blank=True, null=True)
    txid = models.TextField(blank=True, null=True)
    received = models.DateTimeField(blank=True, null=True)
    created = models.DateTimeField()
    paymentid = models.IntegerField(blank=True, null=True)
    sqrcid = models.TextField(blank=True, null=True)
    locid = models.TextField(blank=True, null=True)
    deviceid = models.TextField(blank=True, null=True)
    name = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = "patientmeta"


class Payment(models.Model):
    id = models.AutoField(primary_key=True)
    patientid = models.IntegerField(blank=True, null=True)
    officeid = models.IntegerField(blank=True, null=True)
    amount = models.TextField()  # NOT NULL in DDL, so removed blank=True, null=True
    txid = models.TextField(blank=True, null=True)
    type = models.TextField(blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True)  # DEFAULT now() in DDL
    status = models.TextField(blank=True, null=True)
    sqrcid = models.TextField(blank=True, null=True)
    trrep = models.IntegerField(blank=True, null=True)
    provider = models.CharField(max_length=255, default="square", blank=True, null=True)
    qty = models.TextField(blank=True, null=True)
    discount = models.DecimalField(
        max_digits=10, decimal_places=2, blank=True, null=True
    )
    shippingcost = models.DecimalField(
        max_digits=10, decimal_places=2, blank=True, null=True
    )
    discountdetails = models.TextField(blank=True, null=True)
    refund_amount = models.TextField(blank=True, null=True)
    refund_reason = models.TextField(blank=True, null=True)
    refund_detail = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = "payment"
        indexes = [
            models.Index(fields=["patientid"], name="payment_patientid"),
            models.Index(fields=["officeid"], name="payment_officeid"),
        ]


class Paymentsnotapproved(models.Model):
    rxid = models.IntegerField()
    rxfillid = models.IntegerField()
    paymentid = models.IntegerField()
    rxfillqty = models.IntegerField()
    orderid = models.CharField(max_length=11, blank=True, null=True)
    datesettofill = models.DateTimeField()
    dateshippedbyhwh = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = "paymentsnotapproved"
        unique_together = (("rxid", "rxfillid"),)


class PcdAgreement(models.Model):
    providernpi = models.TextField()
    status = models.TextField(blank=True, null=True)
    effectivedate = models.DateTimeField(blank=True, null=True)
    expirationdate = models.DateTimeField(blank=True, null=True)
    created = models.DateTimeField(blank=True, null=True)
    updated = models.DateTimeField(blank=True, null=True)
    deleted = models.DateTimeField(blank=True, null=True)
    approvalstatus = models.TextField(blank=True, null=True)
    approvaldate = models.DateTimeField(blank=True, null=True)
    approvaluser = models.TextField(blank=True, null=True)
    documenturl = models.TextField(blank=True, null=True)
    createduser = models.TextField(blank=True, null=True)
    deleteduser = models.TextField(blank=True, null=True)
    updateduser = models.TextField(blank=True, null=True)
    email = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = "pcd_agreement"


class PcdFormularyAgreement(models.Model):
    pcd_agreement_id = models.IntegerField()
    normalizeddruggroupid = models.IntegerField()
    status = models.TextField(blank=True, null=True)
    created = models.DateTimeField(blank=True, null=True)
    updated = models.DateTimeField(blank=True, null=True)
    deleted = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = "pcd_formulary_agreement"


class PcdInboundNdc(models.Model):
    inboundndc = models.TextField(unique=True)
    normalizedgroupid = models.IntegerField()
    status = models.TextField(blank=True, null=True)
    created = models.DateTimeField(blank=True, null=True)
    createduser = models.TextField(blank=True, null=True)
    updated = models.DateTimeField(blank=True, null=True)
    updateduser = models.TextField(blank=True, null=True)
    deleted = models.DateTimeField(blank=True, null=True)
    deleteduser = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = "pcd_inbound_ndc"


class PcdNormalizedDrugGroup(models.Model):
    outboundndc = models.TextField()
    groupname = models.TextField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    status = models.TextField(blank=True, null=True)
    created = models.DateTimeField(blank=True, null=True)
    createduser = models.TextField(blank=True, null=True)
    updated = models.DateTimeField(blank=True, null=True)
    updateduser = models.TextField(blank=True, null=True)
    deleted = models.DateTimeField(blank=True, null=True)
    deleteduser = models.TextField(blank=True, null=True)
    dosageform = models.TextField(blank=True, null=True)
    activeingredients = models.TextField(blank=True, null=True)
    medicalcondition = models.TextField(blank=True, null=True)
    percentstrength = models.TextField(blank=True, null=True)
    clinicaldifference = models.TextField(blank=True, null=True)
    outboundndcname = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = "pcd_normalized_drug_group"


class Prepaid(models.Model):
    patientid = models.IntegerField()
    rxid = models.IntegerField()
    medicationid = models.CharField(max_length=255)
    qty = models.IntegerField()
    created = models.DateTimeField()
    modified = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = "prepaid"


class Rx(models.Model):
    rxrawid = models.IntegerField(blank=True, null=True)
    patientid = models.IntegerField(blank=True, null=True)
    doctorid = models.IntegerField(blank=True, null=True)
    officeid = models.IntegerField(blank=True, null=True)
    medicationid = models.TextField(blank=True, null=True)
    status = models.TextField(blank=True, null=True)
    qty = models.IntegerField(blank=True, null=True)
    refills = models.IntegerField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    sig = models.TextField(blank=True, null=True)
    received = models.DateTimeField(blank=True, null=True)
    effective = models.DateTimeField(blank=True, null=True)
    created = models.DateTimeField()
    suppressrefills = models.BooleanField(blank=True, null=True)
    pharmetikaid = models.TextField(blank=True, null=True)
    dhdata = models.TextField(blank=True, null=True)
    rxsource = models.TextField(blank=True, null=True)
    ndcexchange_flag = models.BooleanField(blank=True, null=True)
    raw_ndc = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = "rx"


class Rxfill(models.Model):
    rxid = models.IntegerField(blank=True, null=True)
    status = models.TextField(blank=True, null=True)
    lot = models.TextField(blank=True, null=True)
    created = models.DateTimeField()
    shipmentid = models.IntegerField(blank=True, null=True)
    paymentid = models.IntegerField(blank=True, null=True)
    nsso = models.TextField(blank=True, null=True)
    orderid = models.TextField(blank=True, null=True)
    fillfrom = models.TextField(blank=True, null=True)
    type = models.TextField(blank=True, null=True)
    origin = models.CharField(max_length=255, blank=True, null=True)
    ordered_date = models.DateTimeField(blank=True, null=True)
    fp_status = models.CharField(max_length=8192, blank=True, null=True)
    qty = models.IntegerField(blank=True, null=True)
    ecommorderid = models.CharField(max_length=255, blank=True, null=True)
    hasaddons = models.BooleanField()
    bulkapprovestatus = models.CharField(max_length=255, blank=True, null=True)
    labelurl = models.TextField(blank=True, null=True)
    shippingmethod = models.TextField(blank=True, null=True)
    islotnumvalid = models.BooleanField(blank=True, null=True)
    remindersent = models.DateTimeField(blank=True, null=True)
    processed = models.DateTimeField(blank=True, null=True)
    isbulk = models.BooleanField(blank=True, null=True)
    iscomplaintrequested = models.BooleanField(blank=True, null=True)
    outreach_attempt = models.IntegerField(blank=True, null=True)
    outreach_attempt_date = models.DateTimeField(blank=True, null=True)
    call_outcome = models.TextField(blank=True, null=True)
    istwoqty = models.BooleanField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = "rxfill"


class Rxprint(models.Model):
    rxid = models.IntegerField(blank=True, null=True)
    origin = models.TextField(blank=True, null=True)
    type = models.TextField(blank=True, null=True)
    created = models.DateTimeField()

    class Meta:
        managed = False
        db_table = "rxprint"


class Rxraw(models.Model):
    payload = models.TextField(blank=True, null=True)
    msgid = models.TextField(blank=True, null=True)
    msg = models.TextField(blank=True, null=True)
    edi = models.TextField(blank=True, null=True)
    sent = models.DateTimeField(blank=True, null=True)
    received = models.DateTimeField()
    status = models.TextField(blank=True, null=True)
    format = models.CharField(max_length=255, blank=True, null=True)
    rxsource = models.CharField(max_length=25, blank=True, null=True)

    class Meta:
        managed = False
        db_table = "rxraw"


class Shipment(models.Model):
    addressid = models.IntegerField(blank=True, null=True)
    tracking = models.TextField(blank=True, null=True)
    carrier = models.TextField(blank=True, null=True)
    status = models.TextField(blank=True, null=True)
    created = models.DateTimeField()
    label = models.TextField(blank=True, null=True)
    datereleased = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = "shipment"


class Skincarepairings(models.Model):
    id = models.BigIntegerField(blank=True, null=False, primary_key=True)
    sku = models.TextField(blank=True, null=True)
    date_created = models.DateTimeField(blank=True, null=True)
    order_id = models.BigIntegerField(blank=True, null=True)
    order_status = models.TextField(blank=True, null=True)
    product_net_revenue = models.FloatField(blank=True, null=True)
    product_name = models.TextField(blank=True, null=True)
    fredofficeid = models.TextField(
        db_column="fredOfficeId", blank=True, null=True
    )  # Field name made lowercase.
    prescribernpi = models.TextField(
        db_column="prescriberNpi", blank=True, null=True
    )  # Field name made lowercase.
    last_updated_date = models.DateField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = "skincarepairings"


class State(models.Model):
    short = models.CharField(max_length=2)
    long = models.CharField(max_length=255)
    bulkpreapproved = models.BooleanField()

    class Meta:
        managed = False
        db_table = "state"


class Substatus(models.Model):
    substatusid = models.AutoField(
        db_column="subStatusId", primary_key=True
    )  # Field name made lowercase.
    status = models.CharField(max_length=255)
    formattedstatus = models.CharField(
        db_column="formattedStatus", max_length=255
    )  # Field name made lowercase.
    description = models.CharField(max_length=255)
    active = models.BooleanField()
    datecreated = models.DateTimeField(
        db_column="dateCreated"
    )  # Field name made lowercase.
    datemodified = models.DateTimeField(
        db_column="dateModified", blank=True, null=True
    )  # Field name made lowercase.
    fpid = models.IntegerField(
        db_column="fpId", blank=True, null=True
    )  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = "subStatus"


class Task(models.Model):
    patientid = models.IntegerField(blank=True, null=True)
    rxid = models.IntegerField(blank=True, null=True)
    ownerid = models.IntegerField(blank=True, null=True)
    assigneeid = models.IntegerField(blank=True, null=True)
    due = models.DateField(blank=True, null=True)
    action = models.TextField(blank=True, null=True)
    status = models.TextField(blank=True, null=True)
    created = models.DateTimeField()
    dailycheck = models.BooleanField()
    type = models.CharField(max_length=255, blank=True, null=True)
    csrxid = models.IntegerField(blank=True, null=True)
    csfillid = models.IntegerField(blank=True, null=True)
    doctorid = models.IntegerField(blank=True, null=True)
    officeid = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = "task"


class Textsent(models.Model):
    patientid = models.IntegerField(
        db_column="patientId", blank=True, null=True
    )  # Field name made lowercase.
    rxid = models.IntegerField(
        db_column="rxId", blank=True, null=True
    )  # Field name made lowercase.
    type = models.CharField(max_length=255)
    phonenumber = models.CharField(
        db_column="phoneNumber", max_length=20
    )  # Field name made lowercase.
    sid = models.CharField(max_length=255, blank=True, null=True)
    status = models.CharField(max_length=20)
    message = models.TextField(blank=True, null=True)
    token = models.CharField(max_length=70)
    datecreated = models.DateTimeField(
        db_column="dateCreated"
    )  # Field name made lowercase.
    datemodified = models.DateTimeField(
        db_column="dateModified", blank=True, null=True
    )  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = "textSent"


class Token(models.Model):
    token = models.TextField(blank=True, null=True)
    status = models.TextField(blank=True, null=True)
    type = models.TextField(blank=True, null=True)
    recordtype = models.TextField(blank=True, null=True)
    recordid = models.IntegerField(blank=True, null=True)
    amount = models.IntegerField(blank=True, null=True)
    created = models.DateTimeField()

    class Meta:
        managed = False
        db_table = "token"


class Updatedskus(models.Model):
    oldformulacode = models.TextField()
    oldndc = models.TextField()
    newformulacode = models.TextField()
    newndc = models.TextField()
    bud = models.TextField()
    active = models.BooleanField()
    created = models.DateTimeField()
    modified = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = "updatedskus"


class Userstate(models.Model):
    userid = models.ForeignKey(
        "Users", models.DO_NOTHING, db_column="userId"
    )  # Field name made lowercase.
    stateid = models.IntegerField(db_column="stateId")  # Field name made lowercase.
    active = models.IntegerField()
    datecreated = models.DateTimeField(
        db_column="dateCreated"
    )  # Field name made lowercase.
    datemodified = models.DateTimeField(
        db_column="dateModified", blank=True, null=True
    )  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = "userState"
        unique_together = (("userid", "stateid"),)


class Users(models.Model):
    first_name = models.CharField(max_length=255, blank=True, null=True)
    last_name = models.CharField(max_length=255, blank=True, null=True)
    email = models.CharField(max_length=255)
    pass_field = models.CharField(
        db_column="pass", max_length=255, blank=True, null=True
    )  # Field renamed because it was a Python reserved word.
    created = models.DateTimeField()
    role = models.CharField(max_length=255, blank=True, null=True)
    status = models.CharField(max_length=255, blank=True, null=True)
    patientid = models.IntegerField(blank=True, null=True)
    salesid = models.IntegerField(blank=True, null=True)
    managerid = models.IntegerField(blank=True, null=True)
    doctorid = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = "users"


class DioItems(models.Model):
    officeid = models.IntegerField(blank=True, null=True)
    formulacode = models.TextField(blank=True, null=True)
    active = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = False
        db_table = "dio_items"


class PrescriptionDispense(models.Model):
    """
    Model for prescription dispense records for ASAP reporting
    """

    # Report metadata
    report_start_date = models.DateField()
    report_end_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=20, default="pending")

    # Patient information
    patient_first_name = models.CharField(max_length=100, blank=True, null=True)
    patient_last_name = models.CharField(max_length=100, blank=True, null=True)
    patient_dob = models.DateField(blank=True, null=True)
    patient_gender = models.CharField(max_length=10, blank=True, null=True)
    patient_address1 = models.CharField(max_length=200, blank=True, null=True)
    patient_city = models.CharField(max_length=100, blank=True, null=True)
    patient_state = models.CharField(max_length=10, blank=True, null=True)
    patient_zip = models.CharField(max_length=20, blank=True, null=True)
    patient_phone = models.CharField(max_length=20, blank=True, null=True)

    # Prescription information
    rx_number = models.IntegerField()
    date_written = models.DateField()
    refills_authorized = models.IntegerField(default=0)
    date_filled = models.DateField()
    fill_number = models.IntegerField(default=0)
    ndc = models.CharField(max_length=20, blank=True, null=True)
    quantity_dispensed = models.DecimalField(
        max_digits=10, decimal_places=2, blank=True, null=True
    )
    days_supply = models.IntegerField(blank=True, null=True)
    dosage_units = models.CharField(
        max_length=5, blank=True, null=True
    )  # 01=each, 02=ml, 03=gm
    payment_type = models.CharField(
        max_length=5, default="01"
    )  # 01=cash, 02=insurance, etc.
    date_sold = models.DateField()

    # Prescriber information
    prescriber_npi = models.CharField(max_length=20, blank=True, null=True)
    prescriber_dea = models.CharField(max_length=20, blank=True, null=True)
    prescriber_last_name = models.CharField(max_length=100, blank=True, null=True)
    prescriber_first_name = models.CharField(max_length=100, blank=True, null=True)
    prescriber_middle_name = models.CharField(max_length=100, blank=True, null=True)

    # Reporting status
    reporting_status = models.CharField(
        max_length=5, default="00"
    )  # 00=new, 01=void, etc.

    # Pharmacy information
    pharmacy_npi = models.CharField(max_length=20, blank=True, null=True)
    pharmacy_dea = models.CharField(max_length=20, blank=True, null=True)
    pharmacy_name = models.CharField(max_length=200, blank=True, null=True)
    pharmacy_address1 = models.CharField(max_length=200, blank=True, null=True)
    pharmacy_address2 = models.CharField(max_length=200, blank=True, null=True)
    pharmacy_city = models.CharField(max_length=100, blank=True, null=True)
    pharmacy_state = models.CharField(max_length=10, blank=True, null=True)
    pharmacy_zip = models.CharField(max_length=20, blank=True, null=True)
    pharmacy_phone = models.CharField(max_length=20, blank=True, null=True)
    pharmacy_source_id = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        managed = False  # Set to True if you want Django to manage this table
        db_table = "prescription_dispenses"
        unique_together = (("rx_number", "fill_number"),)
        indexes = [
            models.Index(fields=["report_start_date"]),
            models.Index(fields=["status"]),
            models.Index(fields=["rx_number", "fill_number"]),
            models.Index(fields=["patient_state"]),
            models.Index(fields=["date_filled"]),
        ]
        ordering = ["-date_filled", "-rx_number"]

    def __str__(self):
        return f"RX {self.rx_number} - {self.patient_last_name}, {self.patient_first_name} - {self.date_filled}"


class RxFillReport(models.Model):
    """
    Django model for the rx_fill_report database view.
    This is a read-only model representing aggregated prescription fill data.
    """

    # Rx Data
    rx_id = models.IntegerField(db_column="rxId")
    rx_created_date = models.DateField(db_column="rxCreatedDate", null=True, blank=True)
    rx_qty = models.IntegerField(db_column="rxQty", null=True, blank=True)
    rx_refills = models.IntegerField(db_column="rxRefills", null=True, blank=True)
    rx_ndc_prescribed = models.CharField(
        db_column="rxNDCPrescribed", max_length=255, null=True, blank=True
    )
    rx_status = models.CharField(
        db_column="rxStatus", max_length=100, null=True, blank=True
    )

    # Rx Fill Data
    fill_id = models.IntegerField(db_column="fillId", primary_key=True)
    fill_type = models.CharField(
        db_column="fillType", max_length=100, null=True, blank=True
    )
    fill_created_date = models.DateField(
        db_column="fillCreatedDate", null=True, blank=True
    )
    fill_status = models.CharField(
        db_column="fillStatus", max_length=100, null=True, blank=True
    )
    fill_qty = models.IntegerField(db_column="fillQty", null=True, blank=True)

    # Shipment
    shipment_date = models.DateField(db_column="shipmentDate", null=True, blank=True)
    shipment_tracking = models.CharField(
        db_column="shipmentTracking", max_length=255, null=True, blank=True
    )

    # Drug/Medication
    medication_brand_name = models.CharField(
        db_column="medicationBrandName", max_length=255, null=True, blank=True
    )
    medication_formula_code = models.CharField(
        db_column="medicationFormulaCode", max_length=100, null=True, blank=True
    )

    # Payment / Fee
    payment_price = models.DecimalField(
        db_column="paymentPrice", max_digits=10, decimal_places=2, null=True, blank=True
    )
    payment_date_of_fill = models.DateField(
        db_column="paymentDateofFill", null=True, blank=True
    )
    payment_amount_paid = models.DecimalField(
        db_column="paymentAmountPaid",
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
    )

    # Doctor
    doctor_first_name = models.CharField(
        db_column="doctorfirstname", max_length=255, null=True, blank=True
    )
    doctor_last_name = models.CharField(
        db_column="doctorlastname", max_length=255, null=True, blank=True
    )
    doctor_name = models.CharField(
        db_column="doctorName", max_length=255, null=True, blank=True
    )
    doctor_phone = models.CharField(
        db_column="doctorPhone", max_length=20, null=True, blank=True
    )
    doctor_email = models.EmailField(db_column="doctorEmail", null=True, blank=True)
    doctor_npi = models.CharField(
        db_column="doctorNPI", max_length=20, null=True, blank=True
    )

    # Office
    office_id = models.IntegerField(db_column="officeId", null=True, blank=True)
    office_name = models.CharField(
        db_column="officeName", max_length=255, null=True, blank=True
    )
    office_address1 = models.CharField(
        db_column="officeAddress1", max_length=255, null=True, blank=True
    )
    office_address2 = models.CharField(
        db_column="officeAddress2", max_length=255, null=True, blank=True
    )
    office_city = models.CharField(
        db_column="officeCity", max_length=100, null=True, blank=True
    )
    office_state = models.CharField(
        db_column="officeState", max_length=2, null=True, blank=True
    )
    office_zip = models.CharField(
        db_column="officeZip", max_length=10, null=True, blank=True
    )
    office_email = models.EmailField(db_column="officeEmail", null=True, blank=True)
    office_netsuite_id = models.CharField(
        db_column="officeNetSuiteId", max_length=100, null=True, blank=True
    )
    office_in_office_dispense = models.BooleanField(
        db_column="officeInOfficeDispense", null=True, blank=True
    )
    office_suppress_refills = models.BooleanField(
        db_column="officeSuppressRefills", null=True, blank=True
    )

    # Consultant
    consultant_first_name = models.CharField(
        db_column="consultantFirstName", max_length=255, null=True, blank=True
    )
    consultant_last_name = models.CharField(
        db_column="consultantLastName", max_length=255, null=True, blank=True
    )
    consultant_email = models.EmailField(
        db_column="consultantEmail", null=True, blank=True
    )

    class Meta:
        managed = False  # Django won't manage this table (it's a view)
        db_table = "rx_fill_report"
        verbose_name = "Rx Fill Report"
        verbose_name_plural = "Rx Fill Reports"
        ordering = ["-rx_created_date"]

    def __str__(self):
        return f"Rx {self.rx_id} - {self.medication_brand_name or 'Unknown Medication'}"

    @property
    def full_office_address(self):
        """Return formatted full office address"""
        parts = [
            self.office_address1,
            self.office_address2,
            self.office_city,
            self.office_state,
            self.office_zip,
        ]
        return ", ".join(filter(None, parts))

    @property
    def doctor_full_name(self):
        """Return formatted doctor full name"""
        if self.doctor_first_name and self.doctor_last_name:
            return f"{self.doctor_first_name} {self.doctor_last_name}"
        return self.doctor_name

    @property
    def consultant_full_name(self):
        """Return formatted consultant full name"""
        if self.consultant_first_name and self.consultant_last_name:
            return f"{self.consultant_first_name} {self.consultant_last_name}"
        return None

    def save(self, *args, **kwargs):
        """Override save to prevent modifications to view data"""
        raise NotImplementedError("Cannot save to database view")

    def delete(self, *args, **kwargs):
        """Override delete to prevent deletions from view"""
        raise NotImplementedError("Cannot delete from database view")
