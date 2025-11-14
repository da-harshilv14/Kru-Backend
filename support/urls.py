from django.urls import path
from .views import (
    GrievanceListCreateView, GrievanceDetailView,
    AssignGrievanceView, UpdateGrievanceStatusView,
    OfficerUpdateGrievanceStatusView, OfficerAssignedGrievancesView
)

urlpatterns = [
    path('grievances/', GrievanceListCreateView.as_view()),
    path('grievances/<int:pk>/', GrievanceDetailView.as_view()),
    path('grievances/<int:pk>/assign/', AssignGrievanceView.as_view()),
    path('grievances/<int:pk>/update-status/', UpdateGrievanceStatusView.as_view()),
    path('grievances/<int:pk>/officer-update/', OfficerUpdateGrievanceStatusView.as_view()),
    path('grievances/my-assigned/', OfficerAssignedGrievancesView.as_view()),
]
