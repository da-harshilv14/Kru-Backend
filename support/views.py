from rest_framework import generics, permissions, status
from rest_framework.decorators import action
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework.views import APIView
from loginSignup.models import User
from rest_framework.permissions import IsAuthenticated
from .models import Grievance
from .serializers import GrievanceSerializer
from notifications.utils import notify_user



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
        grievance.officer_remark = remark
        grievance.save()

        # 🔥🔥 NOTIFICATION — Notify Farmer about status update
        if new_status == "Approved":
            notify_user(
                user=grievance.user,
                notif_type="grievance",
                subject="✅ Grievance Approved!",
                message=f"🎉 Great news! Your grievance '{grievance.subject}' has been approved. Remark: {remark}"
            )

        elif new_status == "Rejected":
            notify_user(
                user=grievance.user,
                notif_type="grievance",
                subject="❌ Grievance Rejected",
                message=f"⚠️ Update: Your grievance '{grievance.subject}' has been rejected. Please review the reason. Remark: {remark}"
            )

        elif new_status == "Under Review":
            notify_user(
                user=grievance.user,
                notif_type="grievance",
                subject="⏳ Grievance Under Review",
                message=f"👀 Your grievance '{grievance.subject}' is now Under Review by Officer {user.full_name}. We'll keep you posted!"
            )

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
