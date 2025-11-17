from rest_framework.permissions import BasePermission


class IsSubsidyProvider(BasePermission):
    """
    Only users with role = subsidy_provider OR admin can create/update/delete.
    """

    def has_permission(self, request, view):
        user = request.user

        if not user.is_authenticated:
            return False

        return user.role in ["subsidy_provider", "admin"]
