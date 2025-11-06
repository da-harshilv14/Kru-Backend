from rest_framework import generics, permissions
from rest_framework.parsers import MultiPartParser, FormParser
from .models import Grievance
from .serializers import GrievanceSerializer


class GrievanceListCreateView(generics.ListCreateAPIView):
    serializer_class = GrievanceSerializer
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def get_queryset(self):
        # return grievances for the current user
        user = self.request.user
        return Grievance.objects.filter(user=user).order_by('-created_at')

    def perform_create(self, serializer):
        serializer.save()


class GrievanceDetailView(generics.RetrieveAPIView):
    serializer_class = GrievanceSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'pk'

    def get_queryset(self):
        return Grievance.objects.filter(user=self.request.user)
