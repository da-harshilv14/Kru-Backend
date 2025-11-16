# least no of applications - officer
from django.db.models import Count, Q
from django.contrib.auth import get_user_model

User = get_user_model()

def get_best_officer():
    """
    Returns officer with least pending applications.
    If tie -> officer with least total applications.
    If no officers available -> None
    """

    officers = User.objects.filter(role="officer")

    if not officers.exists():
        return None

    officers = officers.annotate(
        pending_count=Count(
            "assigned_subsidy_applications",
            filter=Q(assigned_subsidy_applications__status="Pending")
        ),
        total_count=Count("assigned_subsidy_applications")
    ).order_by("pending_count", "total_count")

    return officers.first()


