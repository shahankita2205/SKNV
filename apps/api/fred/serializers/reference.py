"""
reference Serializers Module

Contains serializers related to reference domain.
"""

from rest_framework import serializers
from django.db.models import Q

import re
import logging
from functools import reduce
from operator import or_
from difflib import SequenceMatcher

logger = logging.getLogger(__name__)

from fred.models import reference
from fred.models import Faq


class FredFaqSerializer(serializers.ModelSerializer):
    class Meta:
        model = Faq
        fields = "__all__"

    def validate_category(self, value):
        """Convert category to lowercase to match legacy PHP behavior"""
        if value:
            return value.lower()
        return value


__all__ = ["FredFaqSerializer"]


class AddressModelSerializer(serializers.ModelSerializer):
    """
    Serializer for creating an Address record
    """

    class Meta:
        model = reference.Address
        fields = "__all__"

    @staticmethod
    def get_address_by_id(address_id: int):
        """
        Get address by ID and return serialized data.
        Returns None if not found.
        """
        try:
            address = reference.Address.objects.using("fred").get(pk=address_id)
            return AddressModelSerializer(address).data
        except reference.Address.DoesNotExist:
            return None

    def address_match(self, address1, address2, zip, type):
        # 1. Try a simple exact match
        matched_addresses = reference.Address.objects.filter(
            address1__exact=address1,
            address2__exact=address2,
            zip__exact=zip,
            type__exact=type,
        ).values()

        # If we found, return the id.
        if len(matched_addresses) == 1:
            return matched_addresses[0]["id"]

        # 2. Normalize inputs
        normalized_address1 = self.normalize_address_1(address1)
        normalized_address2 = self.normalize_address_2(address2)
        original_zip = zip.strip()
        normalized_zip = zip.strip()[:5]

        # TIER 1: Exact match on normalized values
        address_matches = (
            reference.Address.objects.filter(address1__iexact=normalized_address1)
            .filter(Q(zip=original_zip) | Q(zip__startswith=normalized_zip))
            .filter(type__exact=type)
        )
        if normalized_address2:
            address_matches = address_matches.filter(
                address2__iexact=normalized_address2
            )
        else:
            address_matches = address_matches.filter(Q(address2="") | Q(address2=None))

        matched_addresses = address_matches.order_by("-id").values()
        # If we found, return the id.
        if len(matched_addresses) == 1:
            logger.error("Match in Tier 1")
            return matched_addresses[0]["id"]

        # TIER 2: Try alternative apartment formats
        if normalized_address2:
            # Part A: Alphanumeric apartment extraction and testing with prefixes
            match = re.match(
                r"^(?:.*\s)?([A-Z0-9]+)$", normalized_address2, re.IGNORECASE
            )
            if match:
                apt_letter = match.group(1)
                # Common prefixes to try
                prefixes = [
                    "SUITE ",
                    "STE ",
                    "SUITE #",
                    "STE #",
                    "SUITE#",
                    "STE#",
                    "APT ",
                    "APT #",
                    "APT#",
                    "APARTMENT ",
                    "APARTMENT #",
                    "APARTMENT#",
                    "UNIT ",
                    "UNIT #",
                    "UNIT#",
                    "#",
                    "",
                    "BUILDING ",
                    "BUILDING #",
                    "BUILDING#",
                    "BLDG ",
                    "BLDG #",
                    "BLDG#",
                ]

                # Create all the OR Q filters into a single value to handle.
                q_objects = [
                    Q(**{"address2__iexact": f"{value}{apt_letter}"})
                    for value in prefixes
                ]
                combined_query = reduce(or_, q_objects)
                address_matches = (
                    reference.Address.objects.filter(
                        address1__iexact=normalized_address1
                    )
                    .filter(combined_query)
                    .filter(Q(zip=original_zip) | Q(zip__startswith=normalized_zip))
                    .filter(type__exact=type)
                )
                matched_addresses = address_matches.order_by("-id").values()
                # If we found, return the id.
                if len(matched_addresses) == 1:
                    logger.error("Match in Tier 2.A.1")
                    return matched_addresses[0]["id"]

                # If no match with exact prefixes, try __icontains search with the letter/number
                address_matches = (
                    reference.Address.objects.filter(
                        address1__iexact=normalized_address1
                    )
                    .filter(address2__icontains=normalized_address2)
                    .filter(Q(zip=original_zip) | Q(zip__startswith=normalized_zip))
                    .filter(type__exact=type)
                )
                matched_addresses = address_matches.order_by("-id").values()
                # If we found, return the id.
                if len(matched_addresses) == 1:
                    logger.error("Match in Tier 2.A.2")
                    return matched_addresses[0]["id"]

            # Part B: Floor designation handling
            match = re.search(r"(\d+)\s*FL", normalized_address2, re.IGNORECASE)
            if match:
                floor_number = match.group(1)
                # Common floor formats to try
                floor_formats = [
                    f"{floor_number} FL",
                    f"{floor_number} FLOOR",
                    f"{floor_number}FL",
                    f"{floor_number}F",
                    f"FLOOR {floor_number}",
                    f"{floor_number}TH FLOOR",
                    f"{floor_number}ND FLOOR",
                    f"{floor_number}RD FLOOR",
                    f"{floor_number}ST FLOOR",
                ]

                # Create all the OR Q filters into a single value to handle.
                q_objects = [
                    Q(**{"address2__iexact": f"{value}"}) for value in floor_formats
                ]
                combined_query = reduce(or_, q_objects)
                address_matches = (
                    reference.Address.objects.filter(
                        address1__iexact=normalized_address1
                    )
                    .filter(combined_query)
                    .filter(Q(zip=original_zip) | Q(zip__startswith=normalized_zip))
                    .filter(type__exact=type)
                )
                matched_addresses = address_matches.order_by("-id").values()
                # If we found, return the id.
                if len(matched_addresses) == 1:
                    logger.error("Match in Tier 2.B.1")
                    return matched_addresses[0]["id"]

        # TIER 3: Similarity-based match
        # Get potential matches based on zip code and address type
        address_matches = reference.Address.objects.filter(
            Q(zip=original_zip) | Q(zip__startswith=normalized_zip)
        ).filter(type__exact=type)
        if normalized_address2:
            apt_number = re.search(r"\d+", normalized_address2)
            if apt_number:
                address_matches = address_matches.filter(
                    address2__icontains=apt_number.group()
                )
            else:
                address_matches = address_matches.filter(
                    address2__iexact=normalized_address2
                )

        matched_addresses = address_matches.order_by("-id")[:20].values()
        # Use similarity check
        best_match = None
        highest_similarity = 0
        similarity_threshold = 90  # Configurable threshold

        for address in matched_addresses:
            match_count, percent = self.similar_text(
                address["address1"].upper(), normalized_address1.upper()
            )
            if percent > highest_similarity:
                highest_similarity = percent
                best_match = address["id"]

        # Only use this match if the similarity percent matches or exceeds the threshold
        if highest_similarity >= similarity_threshold:
            logger.error("Match in Tier 3")
            return best_match

        # TIER 3.5: Bidirectional concatenation matching
        # Handles both: DB(addr1+addr2) vs Input(street) AND DB(addr1) vs Input(street+apt)
        address_matches = (
            reference.Address.objects.filter(
                Q(zip=original_zip) | Q(zip__startswith=normalized_zip)
            )
            .filter(type__exact=type)
            .order_by("-id")
            .values()
        )

        for address in address_matches:
            input_combined = self.normalize_address_1(address1 + " " + address2)

            db_normalized_address1 = self.normalize_address_1(address["address1"])

            # Scenario A: Database has separated data (address1 + address2), input has combined (street only)
            if address["address2"]:
                db_combined_normalized = self.normalize_address_1(
                    address["address1"] + " " + address["address2"]
                )

                # Check for exact match
                if db_combined_normalized == normalized_address1:
                    logger.error("Match in Tier 3.5.A")
                    return address["id"]

            # Scenario B: Database has combined data (address1), input has separated (street + apt)
            if input_combined:
                # Check for exact match
                if db_normalized_address1 == input_combined:
                    logger.error("Match in Tier 3.5.B")
                    return address["id"]

        # TIER 4: Try with unnormalized values
        if address2:
            # Try exact match with original values
            address_matches = (
                reference.Address.objects.filter(address1__iexact=address1)
                .filter(address2__iexact=address2)
                .values()
            )

            # If we found, return the id.
            if len(address_matches) == 1:
                logger.error("Match in Tier 4")
                return address_matches[0]["id"]

            # Try with LIKE on the literal value
            address_matches = (
                reference.Address.objects.filter(address1__iexact=address1)
                .filter(address2__icontains=address2)
                .values()
            )

            # If we found, return the id.
            if len(address_matches) == 1:
                logger.error("Match in Tier 4.5")
                return address_matches[0]["id"]

        # TIER 5: Fallback to original method
        address_matches = (
            reference.Address.objects.filter(address1__iexact=address1)
            .filter(zip__exact=zip)
            .filter(type__exact=type)
        )
        if address2:
            address_matches = address_matches.filter(address2__iexact=address2)
        else:
            address_matches = address_matches.filter(Q(address2="") | Q(address2=None))

        matched_addresses = address_matches.order_by("-id").values()
        # If we found, return the id.
        if len(matched_addresses) == 1:
            logger.error("Match in Tier 5")
            return matched_addresses[0]["id"]

        # If still no match and we used a ZIP+4, try with just the 5-digit ZIP
        if zip != normalized_zip:
            address_matches = (
                reference.Address.objects.filter(address1__iexact=address1)
                .filter(zip__exact=normalized_zip)
                .filter(type__exact=type)
            )
            if address2:
                address_matches = address_matches.filter(address2__iexact=address2)
            else:
                address_matches = address_matches.filter(
                    Q(address2="") | Q(address2=None)
                )

            matched_addresses = address_matches.order_by("-id").values()
            # If we found, return the id.
            if len(matched_addresses) == 1:
                logger.error("Match in Tier 5.5")
                return matched_addresses[0]["id"]

        # If We never found it
        logger.error("No Match")
        return False

    def normalize_address_1(self, address1):

        street_types = {
            r"\bSTREET\b": "ST",
            r"\bAVENUE\b": "AVE",
            r"\bBOULEVARD\b": "BLVD",
            r"\bDRIVE\b": "DR",
            r"\bCOURT\b": "CT",
            r"\bROAD\b": "RD",
            r"\bLANE\b": "LN",
            r"\bCIRCLE\b": "CIR",
            r"\bPLACE\b": "PL",
            r"\bPARKWAY\b": "PKWY",
            r"\bTERRACE\b": "TER",
            r"\bHIGHWAY\b": "HWY",
            r"\bSQUARE\b": "SQ",
            r"\bTRAIL\b": "TRL",
            r"\bWAY\b": "WAY",
        }

        directions = {
            r"\bNORTH\b": "N",
            r"\bSOUTH\b": "S",
            r"\bEAST\b": "E",
            r"\bWEST\b": "W",
            r"\bNORTHEAST\b": "NE",
            r"\bNORTHWEST\b": "NW",
            r"\bSOUTHEAST\b": "SE",
            r"\bSOUTHWEST\b": "SW",
        }

        normalized_address = address1.upper().strip()

        # Replace multiple spaces with single space
        normalized_address = re.sub(r"\s+", " ", normalized_address)

        # Replace street types with abbreviation
        for full, abbrev in street_types.items():
            normalized_address = re.sub(full, abbrev, normalized_address)

        # Replace directionals with abbreviations
        for full, abbrev in directions.items():
            normalized_address = re.sub(full, abbrev, normalized_address)

        # Remove periods from abbreviations
        normalized_address = normalized_address.replace(".", "")

        # Standardize spacing around commas
        normalized_address = re.sub(r"\s*,\s*", ", ", normalized_address)

        return normalized_address

    def normalize_address_2(self, address2):
        if not address2:
            return ""

        # Convert to uppercase for processing
        normalized_address = address2.upper()

        # Remove punctuation
        for char in [".", ",", "#"]:
            normalized_address = normalized_address.replace(char, " ")

        # Normalize extra spaces
        normalized_address = re.sub(r"\s+", " ", normalized_address.strip())

        # Store the original format in case we need it
        original_address = address2

        # Try to get just the letter/number part for simple unit designations
        match = re.match(r"^(?:.*\s)?([A-Z0-9]+)$", original_address, re.IGNORECASE)
        if match:
            # If it's just a letter (like "A") or alphanumeric (like "5A"),
            # keep it as-is without adding prefixes
            if len(match.group(1)) <= 3:
                return match.group(1)

        # For more complex formats, standardize common prefixes
        normalized_address = re.sub(
            r"^(APARTMENT|APT\.?)\s*", "APT ", normalized_address, flags=re.IGNORECASE
        )
        normalized_address = re.sub(
            r"^(SUITE|STE\.?)\s*", "STE ", normalized_address, flags=re.IGNORECASE
        )
        normalized_address = re.sub(
            r"^(BUILDING|BLDG\.?)\s*", "BLDG ", normalized_address, flags=re.IGNORECASE
        )
        normalized_address = re.sub(
            r"^(UNIT)\s*", "UNIT ", normalized_address, flags=re.IGNORECASE
        )
        normalized_address = re.sub(
            r"^(NO|NUMBER|#)\s*", "", normalized_address, flags=re.IGNORECASE
        )

        # Handle floor designations
        normalized_address = re.sub(
            r"\b(FLOOR|FL\.?)\b", "FL", normalized_address, flags=re.IGNORECASE
        )

        # Standardize ordinal formats (1ST, 2ND, 3RD, etc.)
        normalized_address = re.sub(
            r"\b([0-9]+)(ST|ND|RD|TH)\s+(FLOOR|FL\.?)\b",
            r"\1 FL",
            normalized_address,
            flags=re.IGNORECASE,
        )

        # Handle "Floor X" format (Floor 2 -> 2 FL)
        normalized_address = re.sub(
            r"\b(FLOOR)\s+([0-9]+)\b", r"\2 FL", normalized_address, flags=re.IGNORECASE
        )

        # Handle word-based floor numbers
        floor_words = {
            "FIRST": "1",
            "SECOND": "2",
            "THIRD": "3",
            "FOURTH": "4",
            "FIFTH": "5",
            "SIXTH": "6",
            "SEVENTH": "7",
            "EIGHTH": "8",
            "NINTH": "9",
            "TENTH": "10",
            "GROUND": "G",
        }

        for word, number in floor_words.items():
            # Handle "Word Floor" format (Second Floor -> 2 FL)
            normalized_address = re.sub(
                rf"\b{word}\s+(FLOOR|FL\.?)\b",
                f"{number} FL",
                normalized_address,
                flags=re.IGNORECASE,
            )

        # Final cleanup
        return normalized_address.strip()

    # Helper function to match PHP's similar_text function
    def similar_text(self, str1, str2):
        matcher = SequenceMatcher(None, str1, str2)
        match_count = sum(block.size for block in matcher.get_matching_blocks())
        max_len = max(len(str1), len(str2))
        percent = (match_count / max_len * 100) if max_len > 0 else 0
        return match_count, percent
