from django.contrib import admin
from django.shortcuts import redirect
from django.urls import path
from django.contrib import messages
from django.template.response import TemplateResponse
from .models import Notification
from .forms import BroadcastForm
from notifications.utils import notify_user
from loginSignup.models import User


class NotificationBroadcastAdmin(admin.ModelAdmin):
    change_list_template = "admin/broadcast_notifications.html"

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                "broadcast/",
                self.admin_site.admin_view(self.broadcast_view),
                name="broadcast-notifications",
            ),
        ]
        return custom_urls + urls

    def broadcast_view(self, request):
        if request.method == "POST":
            form = BroadcastForm(request.POST)

            if form.is_valid():
                target_group = form.cleaned_data["target_group"]
                users = form.cleaned_data["users"]
                subject = form.cleaned_data["subject"]
                message = form.cleaned_data["message"]

                # Determine recipients
                if target_group == "all":
                    recipients = User.objects.filter(is_active=True)
                elif target_group == "custom":
                    recipients = users
                else:
                    recipients = User.objects.filter(role=target_group, is_active=True)

                count = 0
                for user in recipients:
                    notify_user(
                        user=user,
                        notif_type="system",
                        subject=subject,
                        message=message,
                    )
                    count += 1

                messages.success(request, f"Broadcast sent to {count} users!")
                return redirect("admin:broadcast-notifications")

        else:
            form = BroadcastForm()

        context = {
            **self.admin_site.each_context(request),
            "form": form,
        }

        return TemplateResponse(request, "admin/broadcast_form.html", context)


@admin.register(Notification)
class NotificationAdmin(NotificationBroadcastAdmin):
    list_display = ("receiver", "subject", "notif_type", "created_at", "is_read")
    list_filter = ("notif_type", "receiver_role", "is_read")
