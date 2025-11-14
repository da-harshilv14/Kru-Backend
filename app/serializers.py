from rest_framework import serializers
from .models import Subsidy, SubsidyRating
from django.conf import settings

class SubsidyRatingSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.username', read_only=True)
    class Meta:
        model = SubsidyRating
        fields = ['id', 'user_name', 'rating', 'review', 'created_at']

class SubsidySerializer(serializers.ModelSerializer):
    ratings = SubsidyRatingSerializer(many=True, read_only=True)
    created_by = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Subsidy
        fields = [
            'id', 'title', 'description', 'amount',
            'eligibility', 'documents_required',
            'application_start_date', 'application_end_date',
            'rating', 'ratings', 'created_by',
        ]

    def get_created_by(self, obj):
        if not obj.created_by:
            return None
        return {
            "id": obj.created_by.pk,
            "full_name": getattr(obj.created_by, "full_name", ""),
            "email": getattr(obj.created_by, "email_address", ""),
            "role": getattr(obj.created_by, "role", ""),
        }
