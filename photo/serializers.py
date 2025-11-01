from rest_framework import serializers
from .models import Document
import cloudinary

class DocumentSerializer(serializers.ModelSerializer):
    file_url = serializers.SerializerMethodField()

    class Meta:
        model = Document
        fields = ['id', 'title', 'document_type', 'document_number', 'file', 'file_url', 'uploaded_at']
        read_only_fields = ['uploaded_at']

    def get_file_url(self, obj):
        if not obj.file:
            return None
        
        public_id = getattr(obj.file, 'public_id', None) or str(obj.file)
        if not public_id:
            return None
        
        cloud_name = cloudinary.config().cloud_name
        
        # Use the resource_type stored in database
        resource_type = getattr(obj, 'resource_type', 'image')
        
        url = f"https://res.cloudinary.com/{cloud_name}/{resource_type}/upload/{public_id}"
        
        print(f"Generated URL: {url} (resource_type: {resource_type})")
        return url

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)