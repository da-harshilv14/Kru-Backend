from django.urls import path
from .views import (
    upload_document, apply_subsidy,
    assign_officer, officer_dashboard, review_application, officer_application_detail, officer_application_documents, officer_verify_documents
)

urlpatterns = [
    path('documents/', upload_document),
    path('apply/', apply_subsidy),

    path('officer/dashboard/', officer_dashboard),
    path('officer/review/<int:app_id>/', review_application),

    path('officer/applications/<int:app_id>/', officer_application_detail),
    path('officer/applications/<int:app_id>/documents/', officer_application_documents),
    path('officer/applications/<int:app_id>/documents/verify/', officer_verify_documents),
]

