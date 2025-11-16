# least no of grievances - officer
from django.db.models import Count, Q
from django.contrib.auth import get_user_model

User = get_user_model()

def get_best_officer():
    """
    Returns officer with least pending grievances.
    If tie -> officer with least total grievances.
    If no officers available -> None
    """

    officers = User.objects.filter(role="officer")

    if not officers.exists():
        return None

    officers = officers.annotate(
        pending_count=Count(
            "assigned_grievances",
            filter=Q(assigned_grievances__status="Pending")
        ),
        total_count=Count("assigned_grievances")
    ).order_by("pending_count", "total_count")

    return officers.first()


