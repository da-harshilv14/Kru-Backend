from django.contrib import admin
from .models import Document, SubsidyApplication
from django.contrib.auth import get_user_model

User = get_user_model()


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ("id", "owner", "document_type", "uploaded_at")
    search_fields = ("owner__full_name", "document_type")


@admin.register(SubsidyApplication)
class SubsidyApplicationAdmin(admin.ModelAdmin):
    list_display = (
        "application_id", "full_name", "subsidy", "status",
        "assigned_officer", "submitted_at"
    )
    list_filter = ("status", "subsidy", "assigned_officer")
    search_fields = ("application_id", "full_name", "mobile", "aadhaar")
    ordering = ("-submitted_at",)

    readonly_fields = (
        "application_id", "user", "submitted_at", "reviewed_at"
    )

    fieldsets = (
        ("Farmer Details", {
            "fields": ("user", "full_name", "mobile", "email", "aadhaar")
        }),

        ("Address", {
            "fields": ("address", "state", "district", "taluka", "village")
        }),

        ("Land Details", {
            "fields": ("land_area", "land_unit", "soil_type", "ownership")
        }),

        ("Bank Details", {
            "fields": ("bank_name", "account_number", "ifsc")
        }),

        ("Subsidy Details", {
            "fields": ("subsidy", "documents")
        }),

        ("Officer Review", {
            "fields": ("assigned_officer", "status", "officer_comment", "reviewed_at")
        }),

        ("System Fields", {
            "fields": ("application_id", "submitted_at")
        }),
    )
