# documents/serializers.py
from rest_framework import serializers
from .models import Document
import cloudinary
from cloudinary.utils import cloudinary_url

class DocumentSerializer(serializers.ModelSerializer):
    file_url = serializers.SerializerMethodField()
    
    class Meta:
        model = Document
        fields = "__all__"
        read_only_fields = ["user", "uploaded_at"]

    

    def get_file_url(self, obj):
        try:
            return obj.file.url 
        except Exception:
            public_id = getattr(obj.file, "public_id", None) or str(obj.file)
            url, _ = cloudinary_url(public_id, resource_type="auto", secure=True)
            return url

    def create(self, validated_data):
        validated_data["user"] = self.context["request"].user
        return super().create(validated_data)

    def update(self, instance, validated_data):
        validated_data["user"] = self.context["request"].user
        return super().update(instance, validated_data)
