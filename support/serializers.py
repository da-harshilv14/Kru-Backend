from rest_framework import serializers
from .models import Grievance
import cloudinary.uploader


class GrievanceSerializer(serializers.ModelSerializer):
    # accept an uploaded file in the request under the 'attachment' key
    attachment = serializers.FileField(required=False, write_only=True, allow_null=True)
    attachment_url = serializers.URLField(read_only=True)

    # officer info
    assigned_officer = serializers.CharField(source="assigned_officer.full_name", read_only=True)

    # ✅ farmer details added here
    farmer_name = serializers.CharField(source="user.full_name", read_only=True)
    farmer_phone = serializers.CharField(source="user.phone", read_only=True)
    farmer_email = serializers.CharField(source="user.email", read_only=True)

    class Meta:
        model = Grievance
        fields = [
            'id', 'grievance_id', 'subject', 'description', 'preferred_contact',
            'attachment', 'attachment_url', 'status', 'assigned_officer',
            'created_at', 'officer_remark',

            # NEW FIELDS
            'farmer_name', 'farmer_phone', 'farmer_email',
        ]

        read_only_fields = [
            'id', 'grievance_id', 'status', 'created_at',
            'assigned_officer', 'attachment_url', 'officer_remark',
            'farmer_name', 'farmer_phone', 'farmer_email',   # ⬅ important
        ]

    def create(self, validated_data):
        request = self.context.get('request')
        user = getattr(request, 'user', None)
        if user and user.is_authenticated:
            validated_data['user'] = user

        # pop attachment from validated_data if present (it's write_only)
        attachment_file = validated_data.pop('attachment', None)

        # create the grievance record first
        grievance = Grievance.objects.create(**validated_data)

        # if a file was uploaded, send to Cloudinary and store secure_url
        if attachment_file:
            try:
                upload_result = cloudinary.uploader.upload(attachment_file)
                secure_url = upload_result.get('secure_url')
                if secure_url:
                    grievance.attachment_url = secure_url
                    grievance.save()
            except Exception:
                pass

        # generate grievance_id based on created pk and year
        if not grievance.grievance_id:
            year = grievance.created_at.year
            grievance.grievance_id = f"GRV{year}{str(grievance.pk).zfill(4)}"
            grievance.save()

        return grievance
