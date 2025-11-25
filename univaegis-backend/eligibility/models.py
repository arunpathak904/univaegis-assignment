from django.db import models


class EligibilityCheck(models.Model):
    """
    Stores the result of running eligibility rules on a document + IELTS scores.
    """
    # We'll reference the Document model from documents app
    document = models.ForeignKey(
        "documents.Document",
        on_delete=models.CASCADE,
        related_name="eligibility_checks",
    )

    # We store IELTS scores as a JSON dict:
    # {"listening": 8.0, "reading": 8.0, "writing": 8.0, "speaking": 8.0}
    ielts_scores = models.JSONField()

    is_eligible = models.BooleanField()
    reasons = models.JSONField(default=list)  # list of strings explaining decision

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"EligibilityCheck(document_id={self.document_id}, eligible={self.is_eligible})"
