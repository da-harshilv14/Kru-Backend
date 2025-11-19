from django.db import models
from django.conf import settings
from django.utils import timezone
from datetime import timedelta


def expire_in_7_days():
    return timezone.now() + timedelta(days=7)


class Notification(models.Model):
    NOTIF_TYPES = [
        ("application", "Subsidy Application"),
        ("grievance", "Grievance"),
        ("subsidy", "New Subsidy"),
        ("payment", "Payment Update"),
        ("system", "System Update"),
        ("custom", "Custom Message"),
    ]

    receiver = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notifications"
    )

    receiver_role = models.CharField(max_length=20)

    notif_type = models.CharField(max_length=20, choices=NOTIF_TYPES)

    subject = models.CharField(max_length=255)
    message = models.TextField()

    is_read = models.BooleanField(default=False, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    expires_at = models.DateTimeField(default=expire_in_7_days)

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Notification"
        verbose_name_plural = "Notifications"

    def __str__(self):
        return f"{self.receiver.full_name} → {self.subject}"


class NotificationPreference(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notification_pref"
    )

    notify_general = models.BooleanField(default=True)

    def __str__(self):
        return f"Notification preferences for {self.user.full_name}"
