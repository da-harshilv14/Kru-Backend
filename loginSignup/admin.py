from django.contrib import admin
from .models import User, OTP
from .forms import UserCreationFormm, UserChangeFormm
from django.contrib.auth.admin import UserAdmin


# --------------------------------------------
# Custom User Admin (your existing code)
# --------------------------------------------

class CustomUserAdmin(UserAdmin):
    model = User
    add_form = UserCreationFormm
    form = UserChangeFormm

    list_display = ("id", "full_name", "email_address", "mobile_number", "role", "aadhaar_number", "is_staff", "is_active")
    list_filter = ("role", "is_staff", "is_active")

    fieldsets = (
        (None, {"fields": ("email_address", "mobile_number", "password")}),
        ("Personal info", {"fields": ("full_name", "aadhaar_number", "role")}),
        ("Permissions", {"fields": ("is_staff", "is_active", "is_superuser", "groups", "user_permissions")}),
    )
    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": (
                "full_name", "email_address", "mobile_number", "aadhaar_number",
                "role", "password1", "password2", "is_staff", "is_active"
            ),
        }),
    )
    search_fields = ("email_address", "mobile_number", "full_name")
    ordering = ("email_address",)


admin.site.register(User, CustomUserAdmin)


# --------------------------------------------
# OTP Admin — NEW
# --------------------------------------------

@admin.register(OTP)
class OTPAdmin(admin.ModelAdmin):
    list_display = ("id", "user_email", "user_id_display", "otp", "purpose", "attempts", "created_at")
    list_filter = ("purpose", "created_at")
    search_fields = ("otp", "user__email_address", "user__mobile_number", "user__id")
    ordering = ("-created_at",)

    def user_email(self, obj):
        return obj.user.email_address
    user_email.short_description = "User Email"

    def user_id_display(self, obj):
        return obj.user.id
    user_id_display.short_description = "User ID"
