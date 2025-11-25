from rest_framework import serializers
from .models import Document


class DocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        fields = [
            "id",
            "file",
            "doc_type",
            "original_filename",
            "uploaded_at",
            "ocr_text",
            "extracted_data",
            "ocr_confidence",
        ]
        read_only_fields = [
            "id",
            "uploaded_at",
            "original_filename",
            "ocr_text",
            "extracted_data",
            "ocr_confidence",
        ]

    def create(self, validated_data):
        file_obj = validated_data.get("file")
        if file_obj and not validated_data.get("original_filename"):
            validated_data["original_filename"] = file_obj.name
        return super().create(validated_data)


class ExtractedDataUpdateSerializer(serializers.Serializer):
    """
    Serializer for updating extracted_data fields on a Document.
    All fields are optional; we only update what is provided.
    """

    # Academic fields
    student_name = serializers.CharField(
        required=False, allow_blank=True, allow_null=True
    )
    university = serializers.CharField(
        required=False, allow_blank=True, allow_null=True
    )
    course = serializers.CharField(
        required=False, allow_blank=True, allow_null=True
    )
    percentage = serializers.FloatField(required=False, allow_null=True)
    gpa = serializers.FloatField(required=False, allow_null=True)
    year_of_passing = serializers.IntegerField(required=False, allow_null=True)

    # Financial fields
    bank_name = serializers.CharField(
        required=False, allow_blank=True, allow_null=True
    )
    account_holder = serializers.CharField(
        required=False, allow_blank=True, allow_null=True
    )
    available_balance = serializers.FloatField(required=False, allow_null=True)
    date = serializers.CharField(
        required=False, allow_blank=True, allow_null=True
    )
