"""
Text Serializers Module

Contains serializers related to text message management.
"""

from rest_framework import serializers
from django.db import connections

from fred.models.models import Textsent


class TextPaginationQuerySerializer(serializers.Serializer):
    """Query parameters for paginated text list."""

    page = serializers.IntegerField(default=1, min_value=1, required=False)
    limit = serializers.IntegerField(
        default=25, min_value=1, max_value=100, required=False
    )
    search = serializers.CharField(
        required=False, allow_blank=True, trim_whitespace=True
    )
    order = serializers.IntegerField(default=0, required=False)
    orderDir = serializers.CharField(default="asc", required=False)

    def validate_page(self, value):
        return max(value, 1) if value else 1

    def validate_limit(self, value):
        return min(max(value, 1), 100) if value else 25

    def validate_orderDir(self, value):
        return value.lower() if value and value.lower() in ["asc", "desc"] else "asc"


class TextSentModelSerializer(serializers.ModelSerializer):
    """
    Serializer for TextSent records
    """

    class Meta:
        model = Textsent
        fields = "__all__"

    def list_paginated_failed_pc_delivers(self, **options):
        """Get paginated failed PC delivers texts with search and ordering."""
        limit = options.get("limit", 25)
        page = options.get("page", 1)
        order = options.get("order", 0)
        order_dir = options.get("orderDir", "asc")
        search = options.get("search", "")

        offset = (page - 1) * limit
        params = []

        base_sql = """
            FROM "textSent" ts
            LEFT JOIN patient p ON ts."patientId" = p.id
            LEFT JOIN rx r ON ts."rxId" = r.id
            LEFT JOIN office o ON r.officeid = o.id
            WHERE ts.status <> 'delivered'
            AND ts.type NOT IN ('newrx', 'refill')
            AND o.officetypeid = 1
        """

        if search:
            base_sql += """
                AND (CAST(ts.id AS TEXT) ILIKE %s
                     OR p.name ILIKE %s
                     OR ts."phoneNumber" ILIKE %s
                     OR ts.message ILIKE %s)
            """
            params.extend([f"%{search}%"] * 4)

        with connections["fred"].cursor() as cursor:
            cursor.execute(f"SELECT COUNT(*) {base_sql}", params)
            records_filtered = cursor.fetchone()[0]

        order_columns = {
            0: 'ts.id',
            1: 'p.name',
            2: 'ts."rxId"',
            3: 'ts.type',
            4: 'ts."phoneNumber"',
            5: 'ts.status',
            6: 'ts."dateCreated"',
        }
        order_field = order_columns.get(order, 'ts."dateCreated"')
        order_direction = "DESC" if order_dir.lower() == "desc" else "ASC"

        data_sql = f"""
            SELECT
                ts.id,
                ts."patientId",
                p.name AS patientname,
                ts."rxId",
                ts.type,
                ts."phoneNumber",
                ts.message,
                ts.status,
                ts."dateCreated"
            {base_sql}
            ORDER BY {order_field} {order_direction}
            LIMIT %s OFFSET %s
        """

        with connections["fred"].cursor() as cursor:
            cursor.execute(data_sql, params + [limit, offset])
            cols = [c[0] for c in cursor.description]
            texts = [dict(zip(cols, row)) for row in cursor.fetchall()]

        last_page = (records_filtered + limit - 1) // limit if limit else 1

        return {
            "texts": texts,
            "firstPage": 1,
            "currentPage": page,
            "lastPage": last_page,
            "recordsFiltered": records_filtered,
            "nextPage": page + 1 if page < last_page else None,
            "previousPage": max(page - 1, 1),
            "recordsTotal": records_filtered,
            "limit": limit,
        }

    def list_paginated_failed_no_patient(self, **options):
        """Get paginated failed no-patient texts with search and ordering."""
        limit = options.get("limit", 25)
        page = options.get("page", 1)
        order = options.get("order", 0)
        order_dir = options.get("orderDir", "asc")
        search = options.get("search", "")

        offset = (page - 1) * limit
        params = []

        base_sql = """
            FROM "textSent" ts
            WHERE ts."patientId" IS NULL
            AND ts.status <> 'delivered'
        """

        if search:
            base_sql += """
                AND (CAST(ts.id AS TEXT) ILIKE %s
                     OR ts."phoneNumber" ILIKE %s
                     OR ts.message ILIKE %s)
            """
            params.extend([f"%{search}%"] * 3)

        with connections["fred"].cursor() as cursor:
            cursor.execute(f"SELECT COUNT(*) {base_sql}", params)
            records_filtered = cursor.fetchone()[0]

        order_columns = {
            0: 'ts.id',
            1: 'ts."rxId"',
            2: 'ts.type',
            3: 'ts."phoneNumber"',
            4: 'ts.status',
            5: 'ts."dateCreated"',
        }
        order_field = order_columns.get(order, 'ts."dateCreated"')
        order_direction = "DESC" if order_dir.lower() == "desc" else "ASC"

        data_sql = f"""
            SELECT
                ts.id,
                ts."patientId",
                ts."rxId",
                ts.type,
                ts."phoneNumber",
                ts.message,
                ts.status,
                ts."dateCreated"
            {base_sql}
            ORDER BY {order_field} {order_direction}
            LIMIT %s OFFSET %s
        """

        with connections["fred"].cursor() as cursor:
            cursor.execute(data_sql, params + [limit, offset])
            cols = [c[0] for c in cursor.description]
            texts = [dict(zip(cols, row)) for row in cursor.fetchall()]

        last_page = (records_filtered + limit - 1) // limit if limit else 1

        return {
            "texts": texts,
            "firstPage": 1,
            "currentPage": page,
            "lastPage": last_page,
            "recordsFiltered": records_filtered,
            "nextPage": page + 1 if page < last_page else None,
            "previousPage": max(page - 1, 1),
            "recordsTotal": records_filtered,
            "limit": limit,
        }
