from rest_framework import serializers
from .models import User

class UserSignupSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["full_name", "email_address", "mobile_number", "aadhaar_number", "password"]
        extra_kwargs = {"password": {"write_only": True}}

    def validate(self, data):
        # Ensure that least one of email or mobile is provided
        if not data.get("email_address") or not data.get("mobile_number"):
            raise serializers.ValidationError("You must provide either an email address and a mobile number")

        return data

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)
