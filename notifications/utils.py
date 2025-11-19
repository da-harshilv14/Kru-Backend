from .models import NotificationPreference, Notification

def notify_user(user, notif_type, subject, message):
    """
    notif_type:
    - application (critical)
    - grievance (critical)
    - payment (critical)
    - subsidy (general)
    - system (general)
    """

    critical = ["application", "grievance", "payment"]

    # If NOT critical → check general preferences
    if notif_type not in critical:
        pref = getattr(user, "notification_pref", None)

        # If preferences exist and general notifications disabled → skip
        if pref and pref.notify_general is False:
            return

    # Create notification
    Notification.objects.create(
        receiver=user,
        receiver_role=user.role,
        notif_type=notif_type,
        subject=subject,
        message=message
    )
