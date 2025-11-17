from rest_framework import serializers
from .models import Article

class ArticleSerializer(serializers.ModelSerializer):
    provider_name = serializers.CharField(source="provider.full_name", read_only=True)
    image = serializers.ImageField(required=False, allow_null=True)

    class Meta:
        model = Article
        fields = [
            "id",
            "title",
            "date",
            "source",
            "provider_name",
            "description",
            "image",
            "tag",
        ]
        read_only_fields = ["provider"]

    def get_image(self, obj):
        # Safely return Cloudinary URL
        try:
            return obj.image.url if obj.image else None
        except:
            return None

    def create(self, validated_data):
        # Attach logged-in provider automatically
        validated_data["provider"] = self.context["request"].user
        return super().create(validated_data)

    def update(self, instance, validated_data):
        # Let Django REST handle image replacement automatically
        return super().update(instance, validated_data)
