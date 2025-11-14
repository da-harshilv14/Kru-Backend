# subsidy/serializers.py
from rest_framework import serializers
from .models import Document, SubsidyApplication, Subsidy

class DocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        fields = ('id', 'owner', 'document_type', 'document_number', 'file', 'uploaded_at')
        read_only_fields = ('id', 'owner', 'uploaded_at')

    def create(self, validated_data):
        # Set owner from request.user if available
        request = self.context.get('request')
        user = getattr(request, 'user', None)
        if user and not user.is_anonymous:
            validated_data['owner'] = user
        return super().create(validated_data)


class SubsidyApplicationSerializer(serializers.ModelSerializer):
    # Accept list of document IDs from client
    document_ids = serializers.ListField(child=serializers.IntegerField(), write_only=True)

    class Meta:
        model = SubsidyApplication
        # include explicit fields you want to accept (flat structure)
        fields = [
            'id', 'subsidy', 'subsidy_id', 'user',
            'full_name', 'mobile', 'email', 'aadhaar',
            'address', 'state', 'district', 'taluka', 'village',
            'land_area', 'land_unit', 'soil_type', 'ownership',
            'bank_name', 'account_number', 'ifsc',
            'documents', 'document_ids',
        ]
        read_only_fields = ('id', 'user', 'documents')
    def validate(self, attrs):
        user = self.context['request'].user
        subsidy = attrs.get('subsidy')

        if SubsidyApplication.objects.filter(user=user, subsidy=subsidy).exists():
            raise serializers.ValidationError(
                {"detail": "You have already applied for this subsidy."}
            )

        return attrs

    def to_internal_value(self, data):
        """
        Allow clients to send either subsidy (pk) or subsidy_id.
        We also accept both `subsidy_id` and `subsidy` (pk).
        """
        data = data.copy()
        if 'subsidy_id' in data and 'subsidy' not in data:
            data['subsidy'] = data.pop('subsidy_id')
        return super().to_internal_value(data)

    def create(self, validated_data):
        doc_ids = validated_data.pop('document_ids', [])
        request = self.context.get('request')
        user = getattr(request, 'user', None)
        if user and not user.is_anonymous:
            validated_data['user'] = user
        # create application
        app = SubsidyApplication.objects.create(**validated_data)
        if doc_ids:
            docs = Document.objects.filter(id__in=doc_ids)
            app.documents.set(docs)
        return app
