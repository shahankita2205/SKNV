from django.contrib import admin
from .models import Hooks_Queue
# Register your models here.
class HookQueueAdmin(admin.ModelAdmin):
    list_display = ("name","date_created","date_processed")


admin.site.register(Hooks_Queue,HookQueueAdmin)