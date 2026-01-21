from django.urls import path, include
from .views import new_script_received

urlpatterns = [
    path("new-script-received",new_script_received,name="new-script-received")
]