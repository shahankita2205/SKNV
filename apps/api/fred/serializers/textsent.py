# app/services/textsent.py
from django.utils import timezone
from django.db import transaction
from fred.models.models import Textsent
from django.db import connections

class TextSentService:

    ERROR_TEXTSENT_NOT_FOUND = 23302

    def get_one_by_token(self, token: str) -> Textsent:
        try:
            return Textsent.objects.get(token=token)
        except Textsent.DoesNotExist:
            raise Exception("Text Message not found")

    def add(self, data: dict) -> dict:
        result = {}

        if not data:
            return result

        text = Textsent(
            patientid=None if data.get("patientId") == 0 else data.get("patientId"),
            rxid=None if data.get("rxId") == 0 else data.get("rxId"),
            type=data.get("type"),
            phonenumber=data.get("phone"),
            status=data.get("status"),
            sid=data.get("sid"),
            message=data.get("message"),
            token=data.get("token"),
            datecreated=timezone.now(),
        )

        try:
            text.save()
            result["msg"] = "added"
        except Exception as e:
            result["msg"] = str(e)

        return result

    def update(self, text: Textsent, status: str, message: str = None) -> bool:
        if message:
            text.message = self.format_twilio_error(message)

        text.status = status
        text.datemodified = timezone.now()

        try:
            text.save(update_fields=["status", "message", "datemodified"])
            return True
        except Exception:
            return False

    def get_not_delivered_pc_delivers(self):
        with connections["fred"].cursor() as cursor:
            cursor.execute("""
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
                FROM "textSent" ts
                LEFT JOIN patient p ON ts."patientId" = p.id
                LEFT JOIN rx r ON ts."rxId" = r.id
                LEFT JOIN office o ON r.officeid = o.id
                WHERE ts.status <> 'delivered'
                AND ts.type NOT IN ('newrx', 'refill')
                AND o.officetypeid = 1
                ORDER BY ts."dateCreated" DESC
            """)

            columns = [col[0] for col in cursor.description]
            return [dict(zip(columns, row)) for row in cursor.fetchall()]

    def get_not_delivered_no_patient(self):
        with connections["fred"].cursor() as cursor:
            cursor.execute("""
                SELECT
                    id,
                    type,
                    "phoneNumber" AS phonenumber,
                    message,
                    status,
                    "dateCreated" AS datecreated
                FROM "textSent"
                WHERE status <> 'delivered'
                AND "patientId" IS NULL
                ORDER BY "dateCreated" DESC
            """)

            columns = [col[0] for col in cursor.description]
            return [
                dict(zip(columns, row))
                for row in cursor.fetchall()
            ]

    def transfer_by_patient(self, from_id: int, to_id: int) -> bool:
        with transaction.atomic():
            texts = Textsent.objects.filter(patientid=from_id)
            if not texts.exists():
                return False

            texts.update(patientid=to_id)
            return True

    def format_twilio_error(self, error: str) -> str:
        error_map = {
            "30006": " - Landline or unreachable carrier.",
            "30003": " - Unreachable destination handset.",
            "30008": " - Unknown error.",
            "30005": " - Unknown destination handset.",
            "32021": " - SHAKEN/STIR call verification failed.",
            "21408": " - Not able to send SMS to this region.",
        }
        return error + error_map.get(str(error), ".")