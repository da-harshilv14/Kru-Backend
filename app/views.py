from django.shortcuts import render
from rest_framework import viewsets
from .models import Subsidy 
from .serializers import SubsidySerializer  

# Create your views here.
def index(request):
    return render(request, "index.html")

class SubsidyViewSet(viewsets.ModelViewSet):
    queryset = Subsidy.objects.all().order_by('-created_at')
    serializer_class = SubsidySerializer