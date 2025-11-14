from rest_framework.permissions import BasePermission

class IsSubsidyProviderOrAdmin(BasePermission):
    # Allow access if user.role == 'subsidy_provider' OR user.role == 'admin' (and authenticated).

    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return False
        return getattr(user, "role", "") in ("subsidy_provider", "admin")
