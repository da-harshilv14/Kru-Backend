# subsidy_provider/serializers.py
from rest_framework import serializers
from django.contrib.auth import get_user_model
from subsidy.models import SubsidyApplication, Document  # if Document is in this app; adjust import if different
from app.models import Subsidy as AppSubsidy

User = get_user_model()


class SimpleUserSerializer(serializers.Serializer):
    """
    Defensive serializer for the auth user. Does not depend on 'username' or 'email' being present.
    Best-effort: returns id, username (fallbacks), full_name and email (fallbacks).
    """
    id = serializers.IntegerField(read_only=True)
    username = serializers.SerializerMethodField(read_only=True)
    full_name = serializers.SerializerMethodField(read_only=True)
    email = serializers.SerializerMethodField(read_only=True)

    def _safe(self, obj, *attrs):
        for a in attrs:
            try:
                v = getattr(obj, a, None)
            except Exception:
                v = None
            if v:
                return v
        return None

    def get_username(self, obj):
        # Prefer 'username', else email, else full_name, else first+last
        val = self._safe(obj, "username", "email", "full_name")
        if val:
            return val
        first = getattr(obj, "first_name", "") or ""
        last = getattr(obj, "last_name", "") or ""
        name = (first + " " + last).strip()
        return name or None

    def get_full_name(self, obj):
        val = self._safe(obj, "full_name")
        if val:
            return val
        if hasattr(obj, "get_full_name"):
            try:
                gf = obj.get_full_name()
                if gf:
                    return gf
            except Exception:
                pass
        first = getattr(obj, "first_name", "") or ""
        last = getattr(obj, "last_name", "") or ""
        return (first + " " + last).strip() or None

    def get_email(self, obj):
        return self._safe(obj, "email")


class SubsidySerializer(serializers.ModelSerializer):
    """
    Minimal subsidy serializer for provider listing.
    """
    created_by = SimpleUserSerializer(source="created_by", read_only=True)

    class Meta:
        model = AppSubsidy
        fields = [
            "id", "title", "description", "amount",
            "documents_required", "application_start_date", "application_end_date",
            "created_at", "created_by", "rating"
        ]
        read_only_fields = fields


class ApplicantDocumentSerializer(serializers.ModelSerializer):
    """Return minimal fields for documents attached to an application."""
    class Meta:
        model = Document
        fields = ["id", "document_type", "document_number", "file", "uploaded_at"]


class SubsidyApplicationForProviderSerializer(serializers.ModelSerializer):
    """
    Serializer used by subsidy providers (owners) to view applications.
    Safe nested user serializer is used for applicant / assigned_officer.
    """
    applicant = SimpleUserSerializer(source="user", read_only=True)
    subsidy_title = serializers.CharField(source="subsidy.title", read_only=True)
    documents = ApplicantDocumentSerializer(many=True, read_only=True)

    class Meta:
        model = SubsidyApplication
        fields = [
            "id",
            "application_id",
            "applicant",
            "subsidy_title",
            "full_name",
            "mobile",
            "email",
            "aadhaar",
            "address",
            "state",
            "district",
            "taluka",
            "village",
            "land_area",
            "land_unit",
            "soil_type",
            "ownership",
            "bank_name",
            "account_number",
            "ifsc",
            "status",
            "document_status",
            "documents",
            "assigned_officer",
            "officer_comment",
            "reviewed_at",
            "submitted_at",
            "updated_at",
        ]
        read_only_fields = [
            "id", "application_id", "applicant", "subsidy_title", "documents",
            "submitted_at", "updated_at", "reviewed_at"
        ]
