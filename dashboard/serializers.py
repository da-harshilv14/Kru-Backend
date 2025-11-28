from rest_framework import serializers
from phonenumber_field.serializerfields import PhoneNumberField
from .models import UserProfile


class UserProfileSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(source="user.full_name", read_only=True)
    email_address = serializers.EmailField(source="user.email_address", read_only=True)
    role = serializers.CharField(source="user.role", read_only=True)
    mobile_number = PhoneNumberField(source="user.mobile_number", read_only=True)

    # URLs for uploaded Cloudinary files
    photo_url = serializers.SerializerMethodField()
    land_proof_url = serializers.SerializerMethodField()
    pan_card_url = serializers.SerializerMethodField()
    aadhaar_card_url = serializers.SerializerMethodField()

    class Meta:
        model = UserProfile
        fields = "__all__"
        read_only_fields = ["user"]

    def get_photo_url(self, obj):
        return obj.photo.url if obj.photo else None

    def get_land_proof_url(self, obj):
        return obj.land_proof.url if obj.land_proof else None

    def get_pan_card_url(self, obj):
        return obj.pan_card.url if obj.pan_card else None

    def get_aadhaar_card_url(self, obj):
        return obj.aadhaar_card.url if obj.aadhaar_card else None


class UserPhotoSerializer(serializers.ModelSerializer):
    photo_url = serializers.SerializerMethodField()

    class Meta:
        model = UserProfile
        fields = ["photo_url"]

    def get_photo_url(self, obj):
        try:
            return obj.photo.url if obj.photo else None
        except:
            return None