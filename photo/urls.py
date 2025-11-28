from django.urls import path
from .views import (
    UserDocumentsListCreateView,
    UserDocumentRetrieveUpdateView,
    UserDocumentDeleteView
)

urlpatterns = [
    path('documents/', UserDocumentsListCreateView.as_view(), name='documents-list-create'),
    path('documents/<int:pk>/', UserDocumentRetrieveUpdateView.as_view(), name='documents-retrieve-update'),
    path('documents/<int:pk>/delete/', UserDocumentDeleteView.as_view(), name='documents-delete'),
]

