from rest_framework import serializers
from .models import Notification

class NotificationSerializer(serializers.ModelSerializer):
    title = serializers.CharField(source="subject")
    type = serializers.SerializerMethodField()
    is_new = serializers.SerializerMethodField()

    class Meta:
        model = Notification
        fields = [
            "id",
            "title",
            "message",
            "type",
            "is_new",
            "created_at",
        ]

    # GLOBAL CLEAN MAPPING TABLE
    TYPE_MAP = {
        "approved": ["application approved", "grievance approved"],
        "submitted": ["application submitted", "grievance submitted"],
        "success": ["payment", "credited"],
        "info": [
            "application under review",
            "application rejected",
            "officer assigned",
            "new subsidy",
            "new grievance",
            "assigned",
            "system",
            "custom",
        ],
    }

    def get_type(self, obj):
        subject = (obj.subject or "").lower()
        notif_type = (obj.notif_type or "").lower()

        # 1️⃣ Check notif_type direct matches
        if notif_type == "payment":
            return "success"
        if notif_type == "application" and "approved" in subject:
            return "approved"
        if notif_type == "application" and "submitted" in subject:
            return "submitted"

        # 2️⃣ Keyword-based matching (dynamic)
        for frontend_type, keywords in self.TYPE_MAP.items():
            if any(keyword in subject for keyword in keywords):
                return frontend_type

        # 3️⃣ Last fallback by notif_type
        if notif_type in ["grievance", "subsidy", "system", "custom"]:
            return "info"

        # 4️⃣ Default fallback
        return "info"

    def get_is_new(self, obj):
        return not obj.is_read

