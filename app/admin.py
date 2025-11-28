from django.contrib import admin
from .models import Subsidy, SubsidyRating

class SubsidyRatingInline(admin.TabularInline):
    model = SubsidyRating
    extra = 0
    fields = ('user', 'rating', 'review', 'created_at')
    readonly_fields = ('created_at',)
    ordering = ('-created_at',)

@admin.register(Subsidy)
class SubsidyAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "amount",
        "rating",
        "created_by",
        "application_start_date",
        "application_end_date",
        "created_at",
    )
    search_fields = ("title", "description", "eligibility")
    list_filter = ("application_start_date", "application_end_date", "rating")
    inlines = [SubsidyRatingInline]
    readonly_fields = ("rating", "created_at")
    raw_id_fields = ("created_by",)

@admin.register(SubsidyRating)
class SubsidyRatingAdmin(admin.ModelAdmin):
    list_display = ("subsidy", "user", "rating", "created_at")
    list_filter = ("rating", "created_at")
    search_fields = ("subsidy__title", "user__full_name", "review")
    ordering = ("-created_at",)
    readonly_fields = ("created_at",)
