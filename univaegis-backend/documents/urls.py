from django.urls import path
from .views import DocumentUploadView, DocumentExtractedUpdateView

urlpatterns = [
    path("upload/", DocumentUploadView.as_view(), name="document-upload"),
    path("<int:pk>/update-extracted/", DocumentExtractedUpdateView.as_view(), name="document-update-extracted",),
]
