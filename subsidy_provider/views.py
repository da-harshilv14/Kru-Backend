# subsidy_provider/views.py
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from app.models import Subsidy as AppSubsidy
from subsidy.models import SubsidyApplication
from .serializers import SubsidySerializer, SubsidyApplicationForProviderSerializer
import sys

class MySubsidiesAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def dispatch(self, request, *args, **kwargs):
        # helpful debug prints while developing — remove or lower verbosity in production
        try:
            print(">>> DISPATCH HIT - debug auth info >>>", file=sys.stderr)
            print("request.user:", repr(request.user), file=sys.stderr)
            print("is_authenticated:", getattr(request.user, "is_authenticated", None), file=sys.stderr)
            print("COOKIES:", request.COOKIES, file=sys.stderr)
            print("HTTP_AUTHORIZATION:", request.META.get("HTTP_AUTHORIZATION"), file=sys.stderr)
        except Exception:
            pass
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        # returns subsidies created by the currently authenticated provider
        qs = AppSubsidy.objects.filter(created_by=request.user).order_by("-created_at")
        serializer = SubsidySerializer(qs, many=True, context={"request": request})
        return Response(serializer.data)


class SubsidyApplicationsAPIView(APIView):
    """
    GET: list all applications for subsidy <pk>.
    Only subsidy.creator (created_by) may access.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, pk, *args, **kwargs):
        subsidy = get_object_or_404(AppSubsidy, pk=pk)
        # verify the currently logged in user is the subsidy owner
        if subsidy.created_by_id != getattr(request.user, "id", None):
            return Response({"detail": "Forbidden - you are not the owner of this subsidy."}, status=status.HTTP_403_FORBIDDEN)

        apps_qs = SubsidyApplication.objects.filter(subsidy=subsidy).order_by("-submitted_at")
        serializer = SubsidyApplicationForProviderSerializer(apps_qs, many=True, context={"request": request})
        return Response(serializer.data)
