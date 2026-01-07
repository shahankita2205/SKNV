from rest_framework.permissions import BasePermission


class HasRole(BasePermission):
    """
    Allow access only to users with one of the allowed roles.
    Expects the view to define `allowed_roles = [...]`
    """

    def has_permission(self, request, view):
        allowed_roles = getattr(view, "allowed_roles", [])

        if not request.user or not request.user.is_authenticated:
            return False

        user_roles = set(role.name for role in request.user.roles.all())
        return bool(set(allowed_roles) & user_roles)
