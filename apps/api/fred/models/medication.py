# fred/models.py (medication-related models)

from django.db import models
import json


class Medication(models.Model):
    """
    Medication model - maps to fred.medication table
    """
    id = models.AutoField(primary_key=True)
    formula = models.TextField(blank=True, null=True)
    formulacode = models.TextField(blank=True, null=True)
    ndc = models.TextField(unique=True, blank=True, null=True)
    dosage = models.TextField(blank=True, null=True)
    size = models.TextField(blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True)
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
    most_prescribed = models.BooleanField(default=False, null=True)
    ingredients_not_included = models.TextField(blank=True, null=True)
    activeingr = models.TextField(blank=True, null=True)
    inactiveingr = models.TextField(blank=True, null=True)
    allowbulk = models.BooleanField(default=True)
    vinsid = models.IntegerField(blank=True, null=True)
    
    class Meta:
        db_table = 'medication'
        managed = False
        ordering = ['formula']
    
    def __str__(self):
        return f"{self.formula} ({self.ndc})" if self.formula and self.ndc else f"Medication {self.id}"
    
    def is_blacklisted_for_state(self, state):
        """Check if medication is blacklisted for a specific state"""
        if not self.blacklist:
            return False
        
        try:
            blacklist_array = json.loads(self.blacklist)
            return state in blacklist_array
        except (json.JSONDecodeError, TypeError):
            return False
    
    def is_blacklisted_for_dio(self):
        """Check if medication is blacklisted for DIO (Direct Inventory Ordering)"""
        DIO_BLACKLIST_SIGNIFIER = "FRED"
        if not self.blacklist:
            return False
        
        try:
            blacklist_array = json.loads(self.blacklist)
            return DIO_BLACKLIST_SIGNIFIER in blacklist_array
        except (json.JSONDecodeError, TypeError):
            return False


class Othermedication(models.Model):
    """
    Other medication model - maps to fred.othermedication table
    Used for tracking non-SKNV medications (competitor products, reference medications)
    """
    id = models.AutoField(primary_key=True)
    brand_ndc = models.TextField(blank=True, null=True)
    branded_name = models.CharField(max_length=255, blank=True, null=True)
    applicant = models.CharField(max_length=255, blank=True, null=True)
    api = models.CharField(max_length=255, blank=True, null=True)  # Active Pharmaceutical Ingredient
    percentage = models.CharField(max_length=255, blank=True, null=True)
    dosage = models.CharField(max_length=255, blank=True, null=True)
    condition = models.CharField(max_length=255, blank=True, null=True)
    allergen_irritant = models.CharField(max_length=255, blank=True, null=True)
    sknv_ndc = models.CharField(max_length=255, blank=True, null=True)
    sknv_suggested_formulations = models.TextField(blank=True, null=True)
    
    class Meta:
        db_table = 'othermedication'
        managed = False
        ordering = ['branded_name']
    
    def __str__(self):
        return f"{self.branded_name} ({self.brand_ndc})" if self.branded_name else f"Other Medication {self.id}"


class Fee(models.Model):
    """
    Fee structure for medications - maps to fred.fee table
    """
    id = models.AutoField(primary_key=True)
    fee = models.IntegerField(blank=True, null=True)  # Note: stored as cents (int), not decimal
    status = models.IntegerField(blank=True, null=True)
    level = models.IntegerField(blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True)
    ndc = models.CharField(max_length=255, unique=True, blank=True, null=True)
    
    class Meta:
        db_table = 'fee'
        managed = False
    
    def __str__(self):
        return f"Fee for {self.ndc}: ${self.fee / 100:.2f}" if self.fee else f"Fee {self.id}"
    
    def get_fee_dollars(self):
        """Return fee in dollars (converting from cents)"""
        return self.fee / 100 if self.fee else 0


class Ingredient(models.Model):
    """
    Ingredient model - maps to fred.ingredient table
    Note: No auto-increment ID or timestamps in original schema
    """
    id = models.IntegerField(primary_key=True)
    slug = models.CharField(max_length=50, blank=True, null=True)
    ingredient = models.CharField(max_length=50, blank=True, null=True)
    description = models.CharField(max_length=50, blank=True, null=True)
    concern = models.CharField(max_length=256, blank=True, null=True)
    citations = models.CharField(max_length=8192, blank=True, null=True)
    
    class Meta:
        db_table = 'ingredient'
        managed = False
        ordering = ['ingredient']
    
    def __str__(self):
        return self.ingredient if self.ingredient else f"Ingredient {self.id}"


class Outofstockmedication(models.Model):
    """
    Out of stock medication tracking - maps to fred.outofstockmedication table
    """
    id = models.AutoField(primary_key=True)
    medicationid = models.IntegerField()
    estimatedinstockdate = models.DateField()
    dateadded = models.DateField()
    isdeleted = models.BooleanField(default=False)
    
    class Meta:
        db_table = 'outofstockmedication'
        managed = False
        ordering = ['-dateadded']
    
    def __str__(self):
        return f"Medication ID {self.medicationid} - Out until {self.estimatedinstockdate}"
    
    @property
    def medication(self):
        """Get the related medication"""
        try:
            return Medication.objects.using('fred').get(id=self.medicationid)
        except Medication.DoesNotExist:
            return None


class Updatedskus(models.Model):
    """
    SKU/NDC update tracking - maps to fred.updatedskus table
    """
    id = models.AutoField(primary_key=True)
    oldformulacode = models.TextField()
    oldndc = models.TextField()
    newformulacode = models.TextField()
    newndc = models.TextField()
    bud = models.TextField()  # Beyond Use Date
    active = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(blank=True, null=True)
    
    class Meta:
        db_table = 'updatedskus'
        managed = False
        indexes = [
            models.Index(fields=['oldndc', 'active']),
            models.Index(fields=['newndc', 'active']),
        ]
    
    def __str__(self):
        return f"{self.oldndc} -> {self.newndc} ({'Active' if self.active else 'Inactive'})"


class AutoSizeSku(models.Model):
    """
    Auto-sizing SKU configuration - maps to fred.auto_size_skus table
    """
    id = models.AutoField(primary_key=True)
    formulacode = models.TextField()
    active = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    
    class Meta:
        db_table = 'auto_size_skus'
        managed = False
    
    def __str__(self):
        return f"AutoSize SKU: {self.formulacode} ({'Active' if self.active else 'Inactive'})"


# Export all medication-related models
__all__ = [
    'Medication',
    'Othermedication',
    'Fee',
    'Ingredient',
    'Outofstockmedication',
    'Updatedskus',
    'AutoSizeSku',
]