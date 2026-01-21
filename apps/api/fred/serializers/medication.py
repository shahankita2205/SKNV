# fred/medication.py (medication-related serializers)

from rest_framework import serializers
from django.db.models import Q, Value
from django.db.models.functions import Replace
import logging

logger = logging.getLogger(__name__)

from fred.models import Medication, Ingredient, Othermedication, Outofstockmedication, Fee, Updatedskus


# ============================================================================
# NDC/SKU Update Helper Functions
# ============================================================================

class NDCResolver:
    """Helper class for resolving NDCs through the update chain"""
    
    @staticmethod
    def normalize_ndc(ndc):
        """Remove hyphens from NDC for comparison"""
        return ndc.replace('-', '') if ndc else ''
    
    @staticmethod
    def find_new_ndc_by_old_ndc(old_ndc):
        """
        Find the new NDC for a given old NDC.
        Searches both with and without hyphens.
        
        Args:
            old_ndc: Can be normalized or with hyphens
            
        Returns:
            str or None: The new NDC (may contain hyphens as stored in DB)
        """
        if not old_ndc:
            return None
        
        # Normalize the input for comparison
        old_ndc_normalized = NDCResolver.normalize_ndc(old_ndc)
        
        # Search in updatedskus with normalized comparison
        all_skus = Updatedskus.objects.using('fred').filter(active=True)
        for sku in all_skus:
            if NDCResolver.normalize_ndc(sku.oldndc) == old_ndc_normalized:
                # Return the new NDC as stored (may have hyphens)
                return sku.newndc
        
        return None
    
    @staticmethod
    def get_current_ndc(original_ndc):
        """
        Follow the update chain to get the most current NDC.
        Handles circular references and normalizes NDCs.
        
        IMPORTANT: This returns a NORMALIZED NDC (no hyphens) for consistent comparison.
        
        Args:
            original_ndc: NDC to resolve (with or without hyphens)
            
        Returns:
            str: Normalized current NDC (without hyphens)
            
        Example: 
            Input: "12345-678-90"
            Chain: "12345-678-90" -> "99999-999-99" 
            Output: "9999999999" (normalized)
        """
        if not original_ndc:
            return original_ndc
        
        # Normalize the input NDC first
        normalized_input = NDCResolver.normalize_ndc(original_ndc)
        current_ndc_normalized = normalized_input
        visited = {normalized_input: True}
        
        max_iterations = 50  # Safety limit to prevent infinite loops
        iterations = 0
        
        while iterations < max_iterations:
            # Find next NDC in chain (may have hyphens)
            updated_ndc = NDCResolver.find_new_ndc_by_old_ndc(current_ndc_normalized)
            
            if updated_ndc is None:
                # No more updates found
                break
            
            # Normalize the new NDC for comparison
            updated_ndc_normalized = NDCResolver.normalize_ndc(updated_ndc)
            
            if updated_ndc_normalized in visited:
                logger.warning(
                    f"Circular NDC reference detected: {updated_ndc_normalized} "
                    f"(starting from: {normalized_input})"
                )
                break
            
            visited[updated_ndc_normalized] = True
            current_ndc_normalized = updated_ndc_normalized
            iterations += 1
        
        if iterations >= max_iterations:
            logger.warning(
                f"Max iterations reached resolving NDC chain for: {original_ndc}"
            )
        
        # Always return normalized NDC for consistent comparison
        return current_ndc_normalized
    
    @staticmethod
    def has_updates(ndc):
        """
        Check if an NDC has been updated.
        Compares normalized versions to handle hyphens.
        
        Args:
            ndc: NDC to check (with or without hyphens)
            
        Returns:
            bool: True if the NDC has been updated to a different NDC
        """
        if not ndc:
            return False
        
        # Normalize input
        normalized_input = NDCResolver.normalize_ndc(ndc)
        
        # Get current (already normalized by get_current_ndc)
        current_normalized = NDCResolver.get_current_ndc(ndc)
        
        # Compare normalized versions
        return current_normalized != normalized_input
    
    @staticmethod
    def get_medication_by_ndc(ndc):
        """
        Get medication by NDC, automatically resolving to current SKU.
        Handles NDCs with or without hyphens.
        
        Process:
        1. Normalize input NDC (remove hyphens)
        2. Resolve to current NDC through update chain (returns normalized)
        3. Search for medication with normalized comparison
        
        Args:
            ndc: NDC to look up (with or without hyphens)
            
        Returns:
            Medication object or None
        """
        if not ndc:
            return None
        
        # Step 1: Normalize input NDC
        ndc_normalized = NDCResolver.normalize_ndc(ndc)
        
        # Step 2: Resolve to current NDC (already returns normalized)
        current_ndc_normalized = NDCResolver.get_current_ndc(ndc)
        
        # Step 3: Search for medication with current NDC
        medications = Medication.objects.using('fred').all()
        
        # First try to find with current/resolved NDC
        for med in medications:
            if med.ndc:
                med_ndc_normalized = NDCResolver.normalize_ndc(med.ndc)
                if med_ndc_normalized == current_ndc_normalized:
                    return med
        
        # If not found with current NDC and current is different from original,
        # try with original NDC (in case resolution failed)
        if current_ndc_normalized != ndc_normalized:
            for med in medications:
                if med.ndc:
                    med_ndc_normalized = NDCResolver.normalize_ndc(med.ndc)
                    if med_ndc_normalized == ndc_normalized:
                        return med
        
        return None


# ============================================================================
# Serializers
# ============================================================================

class FredIngredientSerializer(serializers.ModelSerializer):
    """Serializer for Ingredient model"""
    
    class Meta:
        model = Ingredient
        fields = [
            'id', 'slug', 'ingredient', 'description', 
            'concern', 'citations'
        ]


class FredFeeSerializer(serializers.ModelSerializer):
    """Serializer for Fee model"""
    fee_dollars = serializers.SerializerMethodField()
    
    class Meta:
        model = Fee
        fields = ['id', 'fee', 'fee_dollars', 'status', 'level', 'created', 'ndc']
        read_only_fields = ['created']
    
    def get_fee_dollars(self, obj):
        """Convert fee from cents to dollars"""
        return obj.get_fee_dollars()


class FredMedicationSerializer(serializers.ModelSerializer):
    """Serializer for Medication model"""
    current_ndc = serializers.SerializerMethodField(read_only=True)
    current_ndc_normalized = serializers.SerializerMethodField(read_only=True)
    is_current_sku = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = Medication
        fields = [
            'id', 'formula', 'formulacode', 'ndc', 'dosage', 'size',
            'created', 'mpn', 'formulashort', 'ingr', 'hwhid', 'nsid',
            'status', 'blacklist', 'brand_name', 'indication', 
            'key_inactives', 'packaging', 'dh_enabled', 'most_prescribed',
            'ingredients_not_included', 'activeingr', 'inactiveingr',
            'allowbulk', 'vinsid', 'current_ndc', 'current_ndc_normalized', 
            'is_current_sku'
        ]
        read_only_fields = ['id', 'created', 'current_ndc', 'current_ndc_normalized', 'is_current_sku']
        extra_kwargs = {
            'ndc': {'required': False}
        }
    
    def get_current_ndc_normalized(self, obj):
        """
        Get the current normalized NDC (for debugging/comparison).
        Always returns without hyphens.
        """
        if not obj.ndc:
            return None
        
        return NDCResolver.get_current_ndc(obj.ndc)
    
    def get_current_ndc(self, obj):
        """
        Get the current NDC if this medication's NDC has been updated.
        Returns None if this is already the current NDC.
        """
        if not obj.ndc:
            return None
        
        normalized_current = NDCResolver.get_current_ndc(obj.ndc)
        normalized_obj = NDCResolver.normalize_ndc(obj.ndc)
        
        # Only return if different (meaning there was an update)
        return normalized_current if normalized_current != normalized_obj else None
    
    def get_is_current_sku(self, obj):
        """Check if this medication is using the current SKU"""
        if not obj.ndc:
            return True
        
        return not NDCResolver.has_updates(obj.ndc)
    
    def validate_ndc(self, value):
        """Ensure NDC is unique for new medications"""
        if self.instance is None and value:  # Creating new medication
            ndc_normalized = NDCResolver.normalize_ndc(value)
            
            medications = Medication.objects.using('fred').all()
            for med in medications:
                if med.ndc:
                    med_ndc_normalized = NDCResolver.normalize_ndc(med.ndc)
                    if med_ndc_normalized == ndc_normalized:
                        raise serializers.ValidationError(
                            "Medication with this NDC already exists"
                        )
        
        return value


class FredMedicationWithFeeSerializer(FredMedicationSerializer):
    """Extended medication serializer that includes fee information"""
    fee = serializers.SerializerMethodField()
    fee_cents = serializers.SerializerMethodField()
    
    class Meta(FredMedicationSerializer.Meta):
        fields = FredMedicationSerializer.Meta.fields + ['fee', 'fee_cents']
    
    def get_fee(self, obj):
        """Get fee in dollars"""
        try:
            fee_obj = Fee.objects.using('fred').get(ndc=obj.ndc)
            return fee_obj.get_fee_dollars() if fee_obj.fee else None
        except Fee.DoesNotExist:
            return None
    
    def get_fee_cents(self, obj):
        """Get fee in cents (raw value)"""
        try:
            fee_obj = Fee.objects.using('fred').get(ndc=obj.ndc)
            return fee_obj.fee
        except Fee.DoesNotExist:
            return None


class FredOthermedicationSerializer(serializers.ModelSerializer):
    """
    Serializer for Othermedication model.
    Represents competitor and reference medications tracked in the system.
    """
    
    class Meta:
        model = Othermedication
        fields = "__all__"


class FredOutofstockmedicationSerializer(serializers.ModelSerializer):
    """Serializer for Outofstockmedication model"""
    medication_info = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = Outofstockmedication
        fields = [
            'id', 'medicationid', 'estimatedinstockdate', 
            'dateadded', 'isdeleted', 'medication_info'
        ]
    
    def get_medication_info(self, obj):
        """Get basic medication info"""
        medication = obj.medication
        if medication:
            return {
                'id': medication.id,
                'ndc': medication.ndc,
                'formula': medication.formula,
                'formulashort': medication.formulashort,
                'formulacode': medication.formulacode
            }
        return None
    
    def validate_medicationid(self, value):
        """Ensure medication exists"""
        if not Medication.objects.using('fred').filter(id=value).exists():
            raise serializers.ValidationError("Medication does not exist")
        return value


class FredUpdatedskusSerializer(serializers.ModelSerializer):
    """Serializer for Updatedskus model"""
    
    class Meta:
        model = Updatedskus
        fields = [
            'id', 'oldformulacode', 'oldndc', 'newformulacode', 
            'newndc', 'bud', 'active', 'created', 'modified'
        ]
        read_only_fields = ['created']


# Export all serializers and helpers
__all__ = [
    # Helper class
    'NDCResolver',
    
    # Serializers
    'FredIngredientSerializer',
    'FredFeeSerializer',
    'FredMedicationSerializer',
    'FredMedicationWithFeeSerializer',
    'FredOthermedicationSerializer',
    'FredOutofstockmedicationSerializer',
    'FredUpdatedskusSerializer',
]