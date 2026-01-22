from rest_framework import permissions

from core.models import Badge


class IsBadgeEditor(permissions.BasePermission):
    """
    Check if a user has the right to edit a specific badge
    """
    message = "Utilisateur non autorisé"
    def has_permission(self, request, view):
        # Check if the user exist and if it has rights to edit badges
        pk = view.kwargs.get("pk")
        user = request.user
        structure = Badge.objects.get(pk=pk).issuing_structure

        return is_structure_editor(user, structure)


def is_structure_editor(user, structure):
    if not user:
        return False

    if not user.is_active or not user.is_authenticated:
        return False

    return any([
        user.is_superuser,
        structure.is_editor(user),
        structure.is_admin(user),
    ])

def is_structure_admin(user, structure):
    if not user:
        return False

    if not user.is_active or not user.is_authenticated:
        return False

    return any([
        user.is_superuser,
        structure.is_admin(user),
    ])