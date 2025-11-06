from rest_framework import serializers
from .models import Grievance
import cloudinary.uploader


class GrievanceSerializer(serializers.ModelSerializer):
    # accept an uploaded file in the request under the 'attachment' key
    attachment = serializers.FileField(required=False, write_only=True, allow_null=True)
    attachment_url = serializers.URLField(read_only=True)

    class Meta:
        model = Grievance
        fields = ['id', 'grievance_id', 'subject', 'description', 'preferred_contact', 'attachment', 'attachment_url', 'status', 'created_at']
        read_only_fields = ['id', 'grievance_id', 'status', 'created_at', 'attachment_url']

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
                # swallow upload errors for now; in production surface an error
                pass

        # generate grievance_id based on created pk and year
        if not grievance.grievance_id:
            year = grievance.created_at.year
            grievance.grievance_id = f"GRV{year}{str(grievance.pk).zfill(4)}"
            grievance.save()

        return grievance
