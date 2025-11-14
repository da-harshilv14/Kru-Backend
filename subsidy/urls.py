# subsidy/urls.py
from django.urls import path
from .views import upload_document, apply_subsidy

urlpatterns = [
    path('documents/', upload_document, name='upload_document'),
    path('apply/', apply_subsidy, name='apply_subsidy'),
]
