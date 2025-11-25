from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework import status

from django.shortcuts import get_object_or_404

from .serializers import DocumentSerializer, ExtractedDataUpdateSerializer
from .models import Document
from .utils import ocr_file, extract_fields, compute_confidence_placeholder


class DocumentUploadView(APIView):
    """
    POST /api/documents/upload/

    Accepts:
      - file: PDF/JPG/PNG
      - doc_type: "academic" or "financial"

    Steps:
      1. Save Document record + file
      2. Run OCR on the saved file
      3. Extract structured fields based on doc_type
      4. Save OCR text, extracted data, and confidence to the Document
      5. Return structured data in response
    """
    parser_classes = (MultiPartParser, FormParser,)
    serializer_class = DocumentSerializer 

    def post(self, request, format=None):
        # The rest of your post method remains the same
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            # 1) Save Document
            document: Document = serializer.save()

            # 2) Run OCR
            file_path = document.file.path  # local path in media/documents/
            try:
                ocr_text = ocr_file(file_path)
            except Exception as e:
                # In production you'd log this
                ocr_text = ""
                extracted = {"error": f"OCR failed: {str(e)}"}
                confidence = 0.0
            else:
                # 3) Extract fields from OCR text
                extracted = extract_fields(document.doc_type, ocr_text)
                confidence = compute_confidence_placeholder(ocr_text)

            # 4) Save OCR + extracted data to DB
            document.ocr_text = ocr_text
            document.extracted_data = extracted
            document.ocr_confidence = confidence
            document.save(update_fields=["ocr_text", "extracted_data", "ocr_confidence"])

            # Re-serialize with updated fields
            updated_serializer = DocumentSerializer(document)

            response_data = {
                "success": True,
                "document": updated_serializer.data,
                "extracted": extracted,
                "confidence": confidence,
            }
            return Response(response_data, status=status.HTTP_201_CREATED)

        return Response(
            {"success": False, "errors": serializer.errors},
            status=status.HTTP_400_BAD_REQUEST,
        )


class DocumentExtractedUpdateView(APIView):
    """
    PATCH /api/documents/<id>/update-extracted/

    Allows updating the extracted_data JSON for a Document.
    We accept only a subset of allowed fields, and merge them into existing extracted_data.
    """

    def patch(self, request, pk, format=None):
        # 1) Find document
        document = get_object_or_404(Document, pk=pk)

        # 2) Validate incoming fields
        serializer = ExtractedDataUpdateSerializer(data=request.data, partial=True)
        if not serializer.is_valid():
            return Response(
                {"success": False, "errors": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )

        update_data = serializer.validated_data

        # 3) Merge into existing extracted_data
        existing = document.extracted_data or {}
        # Update only provided keys
        for key, value in update_data.items():
            existing[key] = value

        document.extracted_data = existing
        document.save(update_fields=["extracted_data"])

        # 4) Return updated document
        doc_serializer = DocumentSerializer(document)
        return Response(
            {
                "success": True,
                "document": doc_serializer.data,
                "updated_fields": update_data,
            },
            status=status.HTTP_200_OK,
        )
