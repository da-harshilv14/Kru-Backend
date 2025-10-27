from django.contrib import admin
from .models import Subsidy

@admin.register(Subsidy)
class SubsidyAdmin(admin.ModelAdmin):
	list_display = ("title", "amount", "application_start_date", "application_end_date", "created_at")
	search_fields = ("title", "description", "eligibility")
	list_filter = ("application_start_date", "application_end_date")
