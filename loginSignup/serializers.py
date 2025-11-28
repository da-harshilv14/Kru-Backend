from rest_framework import serializers
from .models import User

class UserSignupSerializer(serializers.ModelSerializer):
    confirm_password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = [
            "full_name",
            "email_address",
            "mobile_number",
            "aadhaar_number",
            "password",
            "confirm_password"
        ]
        extra_kwargs = {
            "password": {"write_only": True}
        }

    def validate(self, data):
        email = data.get("email_address")
        mobile = data.get("mobile_number")

        # Password check
        if data["password"] != data["confirm_password"]:
            raise serializers.ValidationError("Passwords do not match")

        # Check if active user already exists
        if User.objects.filter(email_address=email, is_active=True).exists():
            raise serializers.ValidationError("An active user with this email already exists")

        if User.objects.filter(mobile_number=mobile, is_active=True).exists():
            raise serializers.ValidationError("An active user with this mobile number already exists")

        return data

    def create(self, validated_data):
        validated_data.pop("confirm_password")

        email = validated_data.get("email_address")
        mobile = validated_data.get("mobile_number")

        # 1️⃣ If inactive user exists → update that record instead of creating new
        try:
            user = User.objects.get(email_address=email, is_active=False)
            # Update details (optional)
            user.full_name = validated_data["full_name"]
            user.mobile_number = mobile
            user.aadhaar_number = validated_data.get("aadhaar_number")
            user.set_password(validated_data["password"])
            user.save()
            return user
        except User.DoesNotExist:
            pass

        # 2️⃣ If inactive user found by mobile
        try:
            user = User.objects.get(mobile_number=mobile, is_active=False)
            user.full_name = validated_data["full_name"]
            user.email_address = email
            user.aadhaar_number = validated_data.get("aadhaar_number")
            user.set_password(validated_data["password"])
            user.save()
            return user
        except User.DoesNotExist:
            pass

        # 3️⃣ No inactive user → create new
        return User.objects.create_user(**validated_data)

