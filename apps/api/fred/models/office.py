"""
Office Models Module

Contains models related to office/location management:
- Office
- OfficeType
- OfficeAgreementType
- OfficeHistory
- OfficeInfo
- DeletedOffice

Legacy Controller Mapping: OfficeController, OfficeTypeController, OfficeAgreementTypeController

Grouping Rationale: Office, OfficeType, and OfficeAgreementType are related entities
typically managed together.
"""

from django.db import models
from .reference import Address


class Officetype(models.Model):
    """
    Office type classification model.
    Defines different types/categories of offices.
    """

    id = models.AutoField(primary_key=True)
    type = models.CharField(max_length=255)

    class Meta:
        managed = False
        db_table = "officetype"
        verbose_name = "Office Type"
        verbose_name_plural = "Office Types"

    def __str__(self):
        return self.type


class Officeagreementtype(models.Model):
    """
    Office agreement type model.
    Defines different types of agreements offices can have.
    """

    id = models.AutoField(primary_key=True)
    agreementname = models.TextField(db_column="agreementName")
    agreementdescription = models.TextField(
        db_column="agreementDescription", blank=True, null=True
    )
    createdat = models.DateTimeField(db_column="createdAt")
    modifiedat = models.DateTimeField(db_column="modifiedAt")

    class Meta:
        managed = False
        db_table = "officeAgreementType"
        verbose_name = "Office Agreement Type"
        verbose_name_plural = "Office Agreement Types"

    def __str__(self):
        return self.agreementname


class Office(models.Model):
    """
    Main office/location model.
    Represents a medical office or clinic location.
    """

    address = models.ForeignKey(
        Address,
        on_delete=models.SET_NULL,
        db_column="addressid",
        blank=True,
        null=True,
        related_name="offices",
    )
    name = models.TextField(blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    dio2enabled = models.DateTimeField(auto_now_add=True, blank=True, null=True)
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
        Officetype, models.DO_NOTHING, db_column="officetypeid", blank=True, null=True
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
        verbose_name = "Office"
        verbose_name_plural = "Offices"

    @property
    def addressid(self):
        """Backward compatibility property for legacy code using addressid."""
        return self.address_id

    def __str__(self):
        return self.name or f"Office {self.id}"


class Officehistory(models.Model):
    """
    Office history/audit model.
    Tracks changes made to office records.
    """

    id = models.AutoField(primary_key=True)
    officeid = models.IntegerField(db_column="officeId")
    triggeredaction = models.TextField(
        db_column="triggeredAction", blank=True, null=True
    )
    datelogged = models.DateTimeField(db_column="dateLogged", blank=True, null=True)
    olddata = models.JSONField(db_column="oldData", blank=True, null=True)
    newdata = models.JSONField(db_column="newData", blank=True, null=True)
    userid = models.IntegerField(db_column="userId", blank=True, null=True)

    class Meta:
        managed = False
        db_table = "officeHistory"
        verbose_name = "Office History"
        verbose_name_plural = "Office Histories"

    def __str__(self):
        return f"Office {self.officeid} - {self.triggeredaction} at {self.datelogged}"


class Officeinfo(models.Model):
    """
    Extended office information model.
    Contains additional details and settings for offices.
    """

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
        verbose_name = "Office Info"
        verbose_name_plural = "Office Info"

    def __str__(self):
        return f"Info for Office {self.officeid_id}"


class Deletedoffice(models.Model):
    """
    Deleted office tracking model.
    Stores information about offices that have been deleted.
    """

    officeid = models.IntegerField(db_column="officeId")
    details = models.TextField()
    created = models.DateTimeField()

    class Meta:
        managed = False
        db_table = "deletedOffice"
        verbose_name = "Deleted Office"
        verbose_name_plural = "Deleted Offices"

    def __str__(self):
        return f"Deleted Office {self.officeid}"


__all__ = [
    "Office",
    "Officetype",
    "Officeagreementtype",
    "Officehistory",
    "Officeinfo",
    "Deletedoffice",
]
