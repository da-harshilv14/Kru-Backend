from rest_framework import serializers
from .models import User

class UserSignupSerializer(serializers.ModelSerializer):
    confirm_password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = [
            "full_name",
            "email_address",
            "aadhaar_number",
            "password",
            "confirm_password"
        ]
        extra_kwargs = {
            "password": {"write_only": True}
        }

    def validate(self, data):
        # 1. Required fields
        if "confirm_password" not in data:
            raise KeyError("confirm_password is required")

        if "password" not in data:
            raise KeyError("password is required")

        # 2. Password match check (test expects this BEFORE email/mobile checks)
        if data["password"] != data["confirm_password"]:
            raise Exception("Passwords do not match")

        email = data.get("email_address")

        # 3. Duplicate active email
        if User.objects.filter(email_address=email, is_active=True).exists():
            raise Exception("email_address already exists")

        return data

    def create(self, validated_data):
        validated_data.pop("confirm_password", None)

        email = validated_data.get("email_address")

        # 1️⃣ If inactive user exists → update that record instead of creating new
        try:
            user = User.objects.get(email_address=email, is_active=False)
            # Update details (optional)
            user.full_name = validated_data["full_name"]
            user.aadhaar_number = validated_data.get("aadhaar_number")
            user.set_password(validated_data["password"])
            user.save()
            return user
        except User.DoesNotExist:
            pass

        # 2️⃣ No inactive user → create new
        return User.objects.create_user(**validated_data)

