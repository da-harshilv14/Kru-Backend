from rest_framework import serializers
from .models import Subsidy

class SubsidySerializer(serializers.ModelSerializer):
    class Meta:
        model = Subsidy
        fields = '__all__'
