# app/views.py
from rest_framework import generics, permissions
from rest_framework.parsers import MultiPartParser, FormParser
from .models import UserProfile
from .serializers import UserProfileSerializer

class UserProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def get_object(self):
        # Get or create ensures the user always has a profile
        profile, _ = UserProfile.objects.get_or_create(user=self.request.user)
        return profile

    def perform_update(self, serializer):
        # Ensure the user field is linked properly during updates
        serializer.save(user=self.request.user)

    def perform_create(self, serializer):
        # (Optional, in case you ever use POST explicitly)
        serializer.save(user=self.request.user)