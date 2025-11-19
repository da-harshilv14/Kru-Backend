from django.urls import path
from .views import (
    MyNotificationsView,
    NotificationPreferenceView,
)
from .views import (
    MarkNotificationReadView,
    MarkAllNotificationsReadView
)

urlpatterns = [
    # Get all notifications (with ?unread=true optional)
    path("", MyNotificationsView.as_view(), name="my-notifications"),

    # Notification preferences (opt-in/out)
    path("preferences/", NotificationPreferenceView.as_view(), name="notification-preferences"),

    # Mark a single notification as read
    path("read/<int:pk>/", MarkNotificationReadView.as_view(), name="notification-read"),

    # Mark ALL notifications as read
    path("read-all/", MarkAllNotificationsReadView.as_view(), name="notification-read-all"),
]
