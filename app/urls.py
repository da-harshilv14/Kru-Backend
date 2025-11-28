from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import SubsidyViewSet, get_subsidy_recommendations,index

router = DefaultRouter()
router.register(r'subsidies', SubsidyViewSet, basename='subsidy')

urlpatterns = [
    path('', index, name="index"),
    path('', include(router.urls)),
    path('recommend-subsidies/', get_subsidy_recommendations, name='recommend-subsidies'),
]
