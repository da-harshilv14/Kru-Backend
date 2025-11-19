from django.utils import timezone
from .models import Notification

def cleanup_old_notifications():
    Notification.objects.filter(expires_at__lt=timezone.now()).delete()