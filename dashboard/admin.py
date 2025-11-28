from django.contrib import admin
from django.utils.html import format_html
from .models import UserProfile

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ["user", "state", "district", "bank_name", "photo_preview"]
    readonly_fields = ["photo_preview"]

    def photo_preview(self, obj):
        if obj.photo:
            return format_html(
                '<img src="{}" style="width: 80px; height: 80px; object-fit: cover; border-radius: 4px;" />',
                obj.photo.url
            )
        return "-"
    photo_preview.short_description = "Profile Photo"
