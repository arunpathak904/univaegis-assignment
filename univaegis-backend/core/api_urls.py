from django.urls import path, include

urlpatterns = [
    path("documents/", include("documents.urls")),
    path("eligibility/", include("eligibility.urls")),
    # later: path("accounts/", include("accounts.urls")),
]
