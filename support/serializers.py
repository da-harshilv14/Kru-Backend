from rest_framework import serializers
from .models import Grievance
import cloudinary.uploader
from .utils import get_best_officer   # <-- IMPORTANT
from notifications.utils import notify_user


class GrievanceSerializer(serializers.ModelSerializer):
    # accept an uploaded file in the request under the 'attachment' key
    attachment = serializers.FileField(required=False, write_only=True, allow_null=True)
    attachment_url = serializers.URLField(read_only=True)

    # officer info
    assigned_officer = serializers.CharField(source="assigned_officer.full_name", read_only=True)

    # farmer info
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
            'farmer_name', 'farmer_phone', 'farmer_email',
        ]

    def create(self, validated_data):
        request = self.context.get('request')
        user = getattr(request, 'user', None)

        # attach user (farmer)
        if user and user.is_authenticated:
            validated_data['user'] = user

        # extract attachment
        attachment_file = validated_data.pop('attachment', None)

        # 1️⃣ Create grievance first (needs ID later)
        grievance = Grievance.objects.create(**validated_data)

        # 2️⃣ Upload file to Cloudinary (optional)
        if attachment_file:
            try:
                upload_result = cloudinary.uploader.upload(attachment_file)
                secure_url = upload_result.get('secure_url')
                if secure_url:
                    grievance.attachment_url = secure_url
                    grievance.save(update_fields=["attachment_url"])
            except Exception:
                pass

        # 3️⃣ Generate grievance ID
        if not grievance.grievance_id:
            year = grievance.created_at.year
            grievance.grievance_id = f"GRV{year}{str(grievance.pk).zfill(4)}"
            grievance.save(update_fields=["grievance_id"])

        # 4️⃣ AUTO-ASSIGN OFFICER USING LOAD BALANCER
        best_officer = get_best_officer()

        if best_officer:
            grievance.assigned_officer = best_officer
            grievance.status = "Under Review"
            grievance.save(update_fields=["assigned_officer", "status"])
        else:
            # No officer available → keep Pending
            grievance.status = "Pending"
            grievance.save(update_fields=["status"])

        # ⭐⭐⭐ NOTIFICATION — Farmer submitted grievance
        notify_user(
            user=user,
            notif_type="grievance",
            subject="📬 Grievance Submitted Successfully!",
            message=f"🌱 Thank you! Your grievance about '{grievance.subject}' has been received. Your tracking ID is {grievance.grievance_id}. We'll start working on it right away!"
        )

        # ⭐⭐⭐ NOTIFICATION — Officer gets assigned grievance
        if best_officer:
            notify_user(
                user=best_officer,
                notif_type="grievance",
                subject="🚨 Action Required: New Grievance Assignment",
                message=f"🔔 You have been assigned a New Grievance (ID: {grievance.grievance_id}) for immediate review. Topic: '{grievance.subject}'. Please check the details and begin processing."
            )

        return grievance

