from django.contrib import admin
from .models import Document


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ("id", "original_filename", "doc_type", "uploaded_at")
    list_filter = ("doc_type", "uploaded_at")
    search_fields = ("original_filename",)
