import os
from pathlib import Path
from dotenv import load_dotenv
import django
from celery import Celery
from django.conf import settings

load_dotenv(Path(__file__).resolve().parent.parent / ".env")

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")

# Ensure Django is fully initialized before Celery starts
django.setup()

app = Celery("core")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks(
    [
        "tasks",
        "tasks.twilio",
        "tasks.call_queue",
        "tasks.md_prescriptions",
        "tasks.hubspot",
    ]
)
