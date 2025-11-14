from rest_framework import generics, permissions, status
from rest_framework.decorators import action
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework.views import APIView
from loginSignup.models import User
from rest_framework.permissions import IsAuthenticated
from .models import Grievance
from .serializers import GrievanceSerializer


class GrievanceListCreateView(generics.ListCreateAPIView):
    serializer_class = GrievanceSerializer
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def get_queryset(self):
        user = self.request.user

        # Farmer → only his grievances
        if user.role == "farmer":
            return Grievance.objects.filter(user=user).order_by('-created_at')

        # Admin → sees all grievances
        if user.role == "admin":
            return Grievance.objects.all().order_by('-created_at')

        # Officer → only assigned to him
        if user.role == "officer":
            return Grievance.objects.filter(assigned_officer=user).order_by('-created_at')

        return Grievance.objects.none()

    def perform_create(self, serializer):
        serializer.save()


class GrievanceDetailView(generics.RetrieveAPIView):
    serializer_class = GrievanceSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'pk'

    def get_queryset(self):
        user = self.request.user

        if user.role == "admin":
            return Grievance.objects.all()

        if user.role == "officer":
            return Grievance.objects.filter(assigned_officer=user)

        return Grievance.objects.filter(user=user)

class AssignGrievanceView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        if request.user.role != "admin":
            return Response({"error": "Only admin can assign grievances"}, status=403)

        officer_id = request.data.get("officer_id")

        try:
            officer = User.objects.get(id=officer_id, role="officer")
        except User.DoesNotExist:
            return Response({"error": "Invalid officer ID"}, status=400)

        try:
            grievance = Grievance.objects.get(pk=pk)
        except Grievance.DoesNotExist:
            return Response({"error": "Grievance not found"}, status=404)

        grievance.assigned_officer = officer
        grievance.status = "assigned"
        grievance.save()

        return Response({"success": "Grievance assigned successfully"})

class UpdateGrievanceStatusView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def patch(self, request, pk):
        user = request.user

        try:
            grievance = Grievance.objects.get(pk=pk)
        except Grievance.DoesNotExist:
            return Response({"error": "Grievance not found"}, status=404)

        if user.role != "officer" or grievance.assigned_officer != user:
            return Response({"error": "Not authorized"}, status=403)

        new_status = request.data.get("status")

        if new_status not in dict(Grievance.STATUS_CHOICES):
            return Response({"error": "Invalid status"}, status=400)

        grievance.status = new_status
        grievance.save()

        return Response({"success": "Status updated"})

class OfficerUpdateGrievanceStatusView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, pk):
        user = request.user

        if user.role != "officer":
            return Response({"error": "Only officers can update grievances."}, status=403)

        try:
            grievance = Grievance.objects.get(pk=pk)
        except Grievance.DoesNotExist:
            return Response({"error": "Grievance not found."}, status=404)

        if grievance.assigned_officer != user:
            return Response({"error": "Not authorized."}, status=403)

        new_status = request.data.get("status")
        remark = request.data.get("remark", "")

        if new_status not in dict(Grievance.STATUS_CHOICES):
            return Response({"error": "Invalid status"}, status=400)

        grievance.status = new_status
        grievance.officer_remark = remark    # SAVE REMARK
        grievance.save()

        return Response({
            "success": "Status updated",
            "grievance_id": grievance.grievance_id,
            "status": grievance.status,
            "remark": grievance.officer_remark
        })

class OfficerAssignedGrievancesView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        # Only officers can access their assigned grievances
        if user.role != "officer":
            return Response({"error": "Only officers can view assigned grievances."}, status=403)

        grievances = Grievance.objects.filter(
            assigned_officer=user
        ).order_by("-created_at")

        serializer = GrievanceSerializer(grievances, many=True)
        return Response(serializer.data)
