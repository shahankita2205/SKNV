from django.apps import AppConfig
from django.conf import settings
import posthog


class CoreConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "core"

    def ready(self):
        posthog.api_key = getattr(settings, "POSTHOG_PROJECT_API_KEY", "")
        posthog.host = getattr(settings, "POSTHOG_HOST", "https://us.i.posthog.com")
