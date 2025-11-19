from rest_framework import generics, permissions
from .models import Notification, NotificationPreference
from .serializers import NotificationSerializer
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status


class MyNotificationsView(generics.ListAPIView):
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qs = Notification.objects.filter(receiver=self.request.user)

        params = self.request.query_params

        if params.get("unread") == "true":
            qs = qs.filter(is_read=False)
        elif params.get("all") == "true":
            return qs.order_by("-created_at")

        # DEFAULT → unread only
        qs = qs.filter(is_read=False)

        return qs.order_by("-created_at")




class NotificationPreferenceView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        pref, _ = NotificationPreference.objects.get_or_create(user=request.user)

        return Response({
            "notify_general": pref.notify_general
        })

    def patch(self, request):
        pref, _ = NotificationPreference.objects.get_or_create(user=request.user)

        notify_general = request.data.get("notify_general")
        if notify_general is not None:
            pref.notify_general = bool(notify_general)
            pref.save()

        return Response({
            "message": "Preferences updated",
            "notify_general": pref.notify_general
        })

class MarkNotificationReadView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, pk):
        try:
            notif = Notification.objects.get(pk=pk, receiver=request.user)
        except Notification.DoesNotExist:
            return Response({"error": "Notification not found"}, status=404)

        notif.is_read = True
        notif.save(update_fields=["is_read"])


        return Response({"success": True})

class MarkAllNotificationsReadView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request):
        Notification.objects.filter(receiver=request.user, is_read=False).update(is_read=True)
        return Response({"success": True})

