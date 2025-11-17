from django.contrib import admin
from django.utils.html import format_html
from .models import Article


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "title",
        "provider",
        "source",
        "date",
        "created_at",
        "image_preview",
    )

    search_fields = ("title", "provider__full_name", "source")
    list_filter = ("provider", "created_at", "date")
    readonly_fields = ("image_preview",)

    def image_preview(self, obj):
        if obj.image:
            return format_html("<img src='{}' height='90'/>", obj.image.url)
        return "(No Image)"

    image_preview.short_description = "Preview"
