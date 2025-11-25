from django.contrib import admin
from .models import EligibilityCheck


@admin.register(EligibilityCheck)
class EligibilityCheckAdmin(admin.ModelAdmin):
    list_display = ("id", "document", "is_eligible", "created_at")
    list_filter = ("is_eligible", "created_at")
    search_fields = ("document__original_filename", "document__id")
