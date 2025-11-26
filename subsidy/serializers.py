# subsidy/serializers.py
from rest_framework import serializers
from .models import SubsidyApplication, Document
from app.models import Subsidy as AppSubsidy
from django.contrib.auth import get_user_model
from .utils import get_best_officer

User = get_user_model()


# --------------------- Document Serializer ---------------------
class DocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        fields = ['id', 'document_type', 'document_number', 'file', 'uploaded_at']
        read_only_fields = ['id', 'uploaded_at']


# --------------------- Officer Serializer (FIXED) ---------------------
class OfficerSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "full_name", "email_address"]   # FIXED EMAIL
        read_only_fields = ["id", "full_name", "email_address"]


# --------------------- Subsidy Mini Serializer ---------------------
class SubsidyMiniSerializer(serializers.ModelSerializer):
    class Meta:
        model = AppSubsidy
        fields = ["id", "title"]


# --------------------- Farmer Application Serializer ---------------------
class SubsidyApplicationSerializer(serializers.ModelSerializer):
    assigned_officer = OfficerSerializer(read_only=True)
    subsidy = SubsidyMiniSerializer(read_only=True)
    subsidy_id = serializers.PrimaryKeyRelatedField(
    queryset=AppSubsidy.objects.all(),
    source='subsidy',
    write_only=True
)

    class Meta:
        model = SubsidyApplication
        fields = [
            "id",
            "application_id",

            # Farmer Info
            "full_name",

            # Subsidy
            "subsidy",
            "subsidy_id",
            # Status
            "status",
            "assigned_officer",

            # Bank
            "account_number",
            "ifsc",

            # Dates
            "submitted_at",
        ]

    def validate(self, attrs):
        request = self.context['request']
        user = request.user

        subsidy = attrs.get('subsidy')
        if SubsidyApplication.objects.filter(user=user, subsidy=subsidy).exists():
            raise serializers.ValidationError({"detail": "You have already applied for this subsidy."})

        return attrs

    def create(self, validated_data):
        doc_ids = validated_data.pop('document_ids', [])
        user = self.context['request'].user
        validated_data['user'] = user

        app = SubsidyApplication.objects.create(**validated_data)

        # Save documents
        if doc_ids:
            docs = Document.objects.filter(id__in=doc_ids, owner=user)
            app.documents.set(docs)

        # Auto assign officer
        best_officer = get_best_officer()
        if best_officer:
            app.assigned_officer = best_officer
            app.status = "Under Review"
        else:
            app.status = "Pending"

        app.save()
        return app


# --------------------- Officer Dashboard Serializer ---------------------
class OfficerSubsidyApplicationSerializer(serializers.ModelSerializer):
    subsidy_name = serializers.CharField(source='subsidy.title', read_only=True)
    subsidy_amount = serializers.CharField(source='subsidy.amount', read_only=True)
    officer = serializers.CharField(source='assigned_officer.full_name', read_only=True)

    class Meta:
        model = SubsidyApplication
        fields = [
            "id",
            "application_id",

            # Personal
            "full_name",
            "mobile",
            "email",   # FIXED EMAIL FIELD
            "aadhaar",
            "address",
            "state",
            "district",
            "taluka",
            "village",

            # Land Info
            "land_area",
            "land_unit",
            "soil_type",
            "ownership",

            # Bank
            "bank_name",
            "account_number",
            "ifsc",

            # Subsidy
            "subsidy_name",
            "subsidy_amount",

            # Status
            "status",
            "officer_comment",
            "reviewed_at",
            "officer",

            # Dates
            "submitted_at",
        ]

        read_only_fields = [
            "id", "application_id", "submitted_at", "reviewed_at",
            "subsidy_name", "subsidy_amount", "officer"
        ]


# --------------------- Officer Review Serializer ---------------------
class OfficerReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubsidyApplication
        fields = ["status", "officer_comment"]

    def validate_status(self, value):
        allowed = ["Approved", "Rejected", "Under Review", "Payment done"]
        if value not in allowed:
            raise serializers.ValidationError("Invalid status supplied.")
        return value
