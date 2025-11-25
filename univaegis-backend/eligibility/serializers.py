from rest_framework import serializers
from .models import EligibilityCheck


class IELTSScoresSerializer(serializers.Serializer):
    listening = serializers.FloatField()
    reading = serializers.FloatField()
    writing = serializers.FloatField()
    speaking = serializers.FloatField()


class EligibilityRequestSerializer(serializers.Serializer):
    """
    Input serializer for eligibility check.
    We expect:
      - document_id: ID of uploaded Document
      - ielts_scores: IELTS band scores
    """
    document_id = serializers.IntegerField()
    ielts_scores = IELTSScoresSerializer()


class EligibilityCheckSerializer(serializers.ModelSerializer):
    class Meta:
        model = EligibilityCheck
        fields = ["id", "document", "ielts_scores", "is_eligible", "reasons", "created_at"]
        read_only_fields = ["id", "created_at"]
