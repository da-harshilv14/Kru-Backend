from django.urls import path
from .views import GrievanceListCreateView, GrievanceDetailView

urlpatterns = [
    path('grievances/', GrievanceListCreateView.as_view(), name='grievance-list-create'),
    path('grievances/<int:pk>/', GrievanceDetailView.as_view(), name='grievance-detail'),
]
