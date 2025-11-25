from django.urls import path
from .views import EligibilityCheckView

urlpatterns = [
    path("check/", EligibilityCheckView.as_view(), name="eligibility-check"),
]
