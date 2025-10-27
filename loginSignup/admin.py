from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User
from .forms import UserCreationFormm, UserChangeFormm


class CustomUserAdmin(UserAdmin):
    model = User
    add_form = UserCreationFormm
    form = UserChangeFormm

    list_display = ("full_name", "email_address", "mobile_number", "role", "aadhaar_number", "is_staff", "is_active")
    list_filter = ("role", "is_staff", "is_active")

    # Fieldsets (for editing users in admin)
    fieldsets = (
        (None, {"fields": ("email_address", "mobile_number", "password")}),
        ("Personal info", {"fields": ("full_name", "aadhaar_number", "role")}),
        ("Permissions", {"fields": ("is_staff", "is_active", "is_superuser", "groups", "user_permissions")}),
    )
    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("full_name", "email_address", "mobile_number", "aadhaar_number", "role", "password1", "password2", "is_staff", "is_active"),
        }),
    )
    search_fields = ("email_address", "mobile_number", "full_name")
    ordering = ("email_address",)
    


admin.site.register(User, CustomUserAdmin)
