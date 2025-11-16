from rest_framework import serializers
from .models import SubsidyApplication, Document
from app.models import Subsidy as AppSubsidy 
from django.contrib.auth import get_user_model
from .utils import get_best_officer

User = get_user_model()


class DocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        fields = ['id', 'document_type', 'document_number', 'file', 'uploaded_at']
        read_only_fields = ['id', 'uploaded_at']


class SubsidyApplicationSerializer(serializers.ModelSerializer):
    subsidy = serializers.PrimaryKeyRelatedField(queryset=AppSubsidy.objects.all())
    document_ids = serializers.ListField(
        child=serializers.IntegerField(), write_only=True, required=False
    )

    class Meta:
        model = SubsidyApplication
        fields = [
            'subsidy', 'document_ids',
            'full_name', 'mobile', 'email', 'aadhaar',
            'address', 'state', 'district', 'taluka', 'village',
            'land_area', 'land_unit', 'soil_type', 'ownership',
            'bank_name', 'account_number', 'ifsc',
        ]

    def validate(self, attrs):
        user = self.context['request'].user
        subsidy = attrs.get('subsidy')
        if SubsidyApplication.objects.filter(user=user, subsidy=subsidy).exists():
            raise serializers.ValidationError({"detail": "You have already applied for this subsidy."})
        return attrs

    def create(self, validated_data):
        doc_ids = validated_data.pop('document_ids', [])
        request = self.context.get('request')
        user = getattr(request, 'user', None)
        validated_data['user'] = user

        app = SubsidyApplication.objects.create(**validated_data)

        if doc_ids:
            docs = Document.objects.filter(id__in=doc_ids, owner=user)
            app.documents.set(docs)

        best_officer = get_best_officer()
        if best_officer:
            app.assigned_officer = best_officer
            app.status = "Under Review"
            app.save()
        else:
            # No officer available → keep pending
            app.status = "Pending"
            app.save()

        return app

class OfficerSubsidyApplicationSerializer(serializers.ModelSerializer):
    subsidy_name = serializers.CharField(source='subsidy.title', read_only=True)
    subsidy_amount = serializers.CharField(source='subsidy.amount', read_only=True)
    officer = serializers.CharField(source='assigned_officer.full_name', read_only=True)

    class Meta:
        model = SubsidyApplication
        fields = [
            "id",
            "application_id",

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

            "subsidy_name",
            "subsidy_amount",

            "status",
            "officer_comment",
            "reviewed_at",
            "officer",

            "submitted_at",
        ]
        read_only_fields = [
            "id", "application_id", "submitted_at", "reviewed_at",
            "subsidy_name", "subsidy_amount", "officer"
        ]


class OfficerReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubsidyApplication
        fields = ["status", "officer_comment"]

    def validate_status(self, value):
        allowed = ["Approved", "Rejected", "Under Review"]
        if value not in allowed:
            raise serializers.ValidationError("Invalid status")
        return value

