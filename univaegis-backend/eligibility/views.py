from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from django.shortcuts import get_object_or_404

from documents.models import Document
from .models import EligibilityCheck
from .serializers import EligibilityRequestSerializer, EligibilityCheckSerializer
from .utils import compute_eligibility


class EligibilityCheckView(APIView):
    """
    POST /api/eligibility/check/

    Request body:
    {
      "document_id": 6,
      "ielts_scores": {
        "listening": 8.0,
        "reading": 8.5,
        "writing": 8.0,
        "speaking": 8.0
      }
    }

    Response:
    {
      "success": true,
      "eligible": true,
      "reasons": [],
      "document_id": 6,
      "ielts_scores": {...},
      "check": { ... saved EligibilityCheck data ... }
    }
    """

    def post(self, request, format=None):
        # 1) Validate input
        serializer = EligibilityRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {"success": False, "errors": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )

        data = serializer.validated_data
        document_id = data["document_id"]
        ielts_scores = data["ielts_scores"]

        # 2) Load Document from DB
        document = get_object_or_404(Document, pk=document_id)

        # Ensure we have extracted_data from OCR step
        extracted_data = document.extracted_data or {}
        if not extracted_data:
            return Response(
                {
                    "success": False,
                    "eligible": False,
                    "reasons": ["No extracted data available for this document."],
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Optionally, ensure it's academic doc, since eligibility rules apply to academics
        if document.doc_type != "academic":
            # We don't strictly have to block, but it's clearer for this assignment
            return Response(
                {
                    "success": False,
                    "eligible": False,
                    "reasons": ["Eligibility rules are defined only for academic documents."],
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # 3) Compute eligibility
        is_eligible, reasons = compute_eligibility(extracted_data, ielts_scores)

        # 4) Save record to DB
        eligibility_check = EligibilityCheck.objects.create(
            document=document,
            ielts_scores=ielts_scores,
            is_eligible=is_eligible,
            reasons=reasons,
        )

        check_serializer = EligibilityCheckSerializer(eligibility_check)

        # 5) Build response
        response_data = {
            "success": True,
            "eligible": is_eligible,
            "reasons": reasons,
            "document_id": document.id,
            "ielts_scores": ielts_scores,
            "check": check_serializer.data,
        }

        return Response(response_data, status=status.HTTP_200_OK)
