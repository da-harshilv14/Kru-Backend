from django.urls import path
from .views import recommend_subsidies, recommendation_status

urlpatterns = [
    path('recommend/', recommend_subsidies, name='recommend-subsidies'),
    path('status/', recommendation_status, name='recommendation-status'),
]
