from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
import sys
import os
from SubsidyRecommandation import SubsidyRecommander

# Add SubsidyRecommandation to path
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'SubsidyRecommandation'))

from .models import Subsidy, SubsidyRating
from .serializers import SubsidySerializer, SubsidyRatingSerializer
from .permissions import IsSubsidyProviderOrAdmin 


def index(request):
    return render(request, "index.html")


class SubsidyViewSet(viewsets.ModelViewSet):
    """
    Main ViewSet for Subsidy management.
    """
    queryset = Subsidy.objects.all().order_by('-created_at')
    serializer_class = SubsidySerializer

    # 🔹 PERMISSIONS HANDLING
    def get_permissions(self):
        if self.action == 'create':
            return [IsAuthenticated(), IsSubsidyProviderOrAdmin()]
        elif self.action in ['rate', 'my_subsidies']:
            return [IsAuthenticated()]
        return [AllowAny()]

    # 🔹 Auto-assign creator
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    # 🔹 RATE subsidy
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def rate(self, request, pk=None):
        subsidy = self.get_object()
        user = request.user

        rating_value = request.data.get("rating")
        review_text = request.data.get("review", "")

        if not rating_value:
            return Response({"error": "Rating value is required."}, status=400)
        try:
            rating_value = int(rating_value)
        except:
            return Response({"error": "Rating must be an integer."}, status=400)

        if not (1 <= rating_value <= 5):
            return Response({"error": "Rating must be between 1 and 5."}, status=400)

        rating_obj, created = SubsidyRating.objects.update_or_create(
            subsidy=subsidy,
            user=user,
            defaults={"rating": rating_value, "review": review_text}
        )

        serializer = SubsidyRatingSerializer(rating_obj)
        message = "Rating submitted!" if created else "Rating updated!"

        return Response({
            "message": message,
            "subsidy_average": subsidy.rating,
            "rating": serializer.data
        })

    # 🔹 GET ALL Ratings
    @action(detail=True, methods=['get'])
    def ratings(self, request, pk=None):
        subsidy = self.get_object()
        ratings = SubsidyRating.objects.filter(subsidy=subsidy)
        serializer = SubsidyRatingSerializer(ratings, many=True)
        return Response(serializer.data)

    # 🔹 TOP 5 rated subsidies
    @action(detail=False, methods=['get'])
    def top_rated(self, request):
        top = Subsidy.objects.order_by('-rating')[:5]
        serializer = SubsidySerializer(top, many=True)
        return Response(serializer.data)

    # 🔹 MY SUBSIDIES
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def my_subsidies(self, request):
        user = request.user
        qs = Subsidy.objects.filter(created_by=user)
        serializer = SubsidySerializer(qs, many=True)
        return Response(serializer.data)


# 🔹 RECOMMENDATION API (outside the ViewSet)
@api_view(['POST'])
@permission_classes([AllowAny])
def get_subsidy_recommendations(request):
    try:

        farmer_profile = request.data.get("farmer_profile")
        if not farmer_profile:
            return Response({"error": "farmer_profile required"}, status=400)

        recommender = SubsidyRecommander()
        recommendations = recommender.recommend_subsidies(farmer_profile)

        return Response({"success": True, "data": recommendations})
    except Exception as e:
        return Response({"success": False, "error": str(e)}, status=500)
