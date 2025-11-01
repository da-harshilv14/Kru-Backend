from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'documents', views.DocumentViewSet, basename='document')

urlpatterns = [
    path('', views.index, name='photo_index'),
    path('api/', include(router.urls)),
    path('api/debug-cookies/', views.debug_cookies, name='debug_cookies'),
    path('api/test-cookie/', views.test_set_cookie, name='test_cookie'),
    path('api/documents/<int:pk>/debug/', views.debug_document, name='debug_document'),
]