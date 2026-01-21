"""
Legacy permission helpers for fred role checks.
"""

from functools import lru_cache
import re

from rest_framework.permissions import BasePermission

from fred.models import Users

LEGACY_ROLES = (
    "admin",
    "manager",
    "finance",
    "finance-assistant",
    "tech-support",
    "sales",
    "sales-manager",
    "patient",
    "planner",
    "customer-service",
    "customer-service-manager",
    "pharmacist",
    "office",
    "doctor",
)

_ROLE_SPLIT_RE = re.compile(r"[,\s]+")
_LEGACY_ROLE_CACHE_ATTR = "_legacy_roles_cache"


def _normalize_roles(values):
    normalized = set()
    if not values:
        return normalized

    for value in values:
        if value is None:
            continue
        if isinstance(value, (list, tuple, set, frozenset)):
            entries = value
        else:
            entries = [value]

        for entry in entries:
            if entry is None:
                continue
            for token in _ROLE_SPLIT_RE.split(str(entry)):
                role = token.strip().lower()
                if role:
                    normalized.add(role)
    return normalized


def _class_suffix(role):
    return "".join(part.capitalize() for part in role.replace("_", "-").split("-"))


def _legacy_class_name(roles):
    parts = [_class_suffix(role) for role in sorted(roles)]
    return "LEGACY_Allow" + "Or".join(parts)


def get_legacy_user_roles(request):
    cached = getattr(request, _LEGACY_ROLE_CACHE_ATTR, None)
    if cached is not None:
        return cached

    user = getattr(request, "user", None)
    if not user or not user.is_authenticated:
        setattr(request, _LEGACY_ROLE_CACHE_ATTR, set())
        return set()

    email = getattr(user, "email", None)
    if not email:
        setattr(request, _LEGACY_ROLE_CACHE_ATTR, set())
        return set()

    role_value = (
        Users.objects.using("fred")
        .filter(email__iexact=email)
        .values_list("role", flat=True)
        .first()
    )
    roles = _normalize_roles([role_value] if role_value else [])
    setattr(request, _LEGACY_ROLE_CACHE_ATTR, roles)
    return roles


class LegacyRolePermission(BasePermission):
    """
    Legacy role gate: matches the core user by email against fred.users.role.
    """

    allowed_roles = frozenset()

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        if not self.allowed_roles:
            return False
        return bool(get_legacy_user_roles(request) & self.allowed_roles)


def legacy_roles(*roles):
    normalized = _normalize_roles(roles)
    if not normalized:
        raise ValueError("At least one legacy role is required.")
    return _legacy_roles_cached(tuple(sorted(normalized)))


@lru_cache(maxsize=None)
def _legacy_roles_cached(normalized_roles):
    role_set = frozenset(normalized_roles)
    class_name = _legacy_class_name(role_set)
    message = f"Legacy role required: {', '.join(normalized_roles)}."
    return type(
        class_name,
        (LegacyRolePermission,),
        {"allowed_roles": role_set, "message": message},
    )


__all__ = [
    "LEGACY_ROLES",
    "LegacyRolePermission",
    "get_legacy_user_roles",
    "legacy_roles",
]

for legacy_role in LEGACY_ROLES:
    class_name = f"LEGACY_Allow{_class_suffix(legacy_role)}"
    globals()[class_name] = legacy_roles(legacy_role)
    __all__.append(class_name)
