from django.db import models


class Document(models.Model):
    DOC_TYPE_CHOICES = (
        ("academic", "Academic"),
        ("financial", "Financial"),
    )

    file = models.FileField(upload_to="documents/")
    doc_type = models.CharField(
        max_length=20,
        choices=DOC_TYPE_CHOICES,
        help_text="Type of document: academic or financial",
    )
    original_filename = models.CharField(max_length=255, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    ocr_text = models.TextField(blank=True)
    extracted_data = models.JSONField(null=True, blank=True)
    ocr_confidence = models.FloatField(null=True, blank=True)


    def __str__(self):
        return f"{self.original_filename or self.file.name} ({self.doc_type})"
