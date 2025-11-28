from django.contrib import admin
from .models import Grievance


@admin.register(Grievance)
class GrievanceAdmin(admin.ModelAdmin):
    list_display = ('id', 'grievance_id', 'subject', 'status', 'user', 'created_at', 'assigned_officer')
    list_filter = ('status', 'created_at')
    search_fields = ('grievance_id', 'subject', 'description', 'user__email')
    list_editable = ('status',)
    actions = ['mark_approved', 'mark_rejected', 'mark_pending']

    def mark_approved(self, request, queryset):
        updated = queryset.update(status=Grievance.STATUS_APPROVED)
        self.message_user(request, f"{updated} grievance(s) marked as Approved.")
    mark_approved.short_description = 'Mark selected grievances as Approved'

    def mark_rejected(self, request, queryset):
        updated = queryset.update(status=Grievance.STATUS_REJECTED)
        self.message_user(request, f"{updated} grievance(s) marked as Rejected.")
    mark_rejected.short_description = 'Mark selected grievances as Rejected'

    def mark_pending(self, request, queryset):
        updated = queryset.update(status=Grievance.STATUS_PENDING)
        self.message_user(request, f"{updated} grievance(s) marked as Pending.")
    mark_pending.short_description = 'Mark selected grievances as Pending'
