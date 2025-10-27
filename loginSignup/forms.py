from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import User

class UserCreationFormm(UserCreationForm):
    class Meta:
        model = User
        fields = ("full_name", "email_address", "mobile_number", "aadhaar_number", "is_staff")

class UserChangeFormm(UserChangeForm):
    class Meta:
        model = User
        fields = ("full_name", "email_address", "mobile_number", "aadhaar_number", "role", "is_active", "is_staff")
