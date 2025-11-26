# subsidy_provider/urls.py
from django.urls import path
from .views import MySubsidiesAPIView, SubsidyApplicationsAPIView

app_name = "subsidy_provider"

urlpatterns = [
    path("subsidies/my/", MySubsidiesAPIView.as_view(), name="my-subsidies"),
    path("subsidies/<int:pk>/applications/", SubsidyApplicationsAPIView.as_view(), name="subsidy-applications"),
]
