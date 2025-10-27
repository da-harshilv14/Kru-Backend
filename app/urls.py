from django.urls import path,include
from rest_framework.routers import DefaultRouter
from .views import SubsidyViewSet
from . import views

router = DefaultRouter()
router.register(r'subsidies', SubsidyViewSet, basename='subsidy')   

urlpatterns = [
    path('', views.index, name="index"),
    path('', include(router.urls)),
]

