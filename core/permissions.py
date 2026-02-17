from rest_framework import permissions
from django.shortcuts import get_object_or_404

from core.models import Badge, Structure, User

#### Permissions class ####
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

class IsStructureAdmin(permissions.BasePermission):
    """
    Check if a user is structure administrator
    """
    message = "Utilisateur non autorisé"
    def has_permission(self, request, view):
        # Check if the user exist and if it has rights to edit badges
        pk = view.kwargs.get("pk")
        user = request.user
        structure = Structure.objects.get(pk=pk)

        return is_structure_admin(user, structure)

class CanEditUser(permissions.BasePermission):
    """
    Check if a user can edit another user
    """
    message = ""
    def has_permission(self, request, view):
        pk = view.kwargs.get("pk")
        edited_user = User.objects.get(pk=pk)
        user = request.user
        if not user:
            return False

        if not user.is_active or not user.is_authenticated:
            return False

        return any([
            #user.is_superuser,
            edited_user == user
        ])

class CanAssignBadge(permissions.BasePermission):
    def has_permission(self, request, view):

        # Return true because the GET method only show the template
        if request.method == "GET":
            return True

        user = request.user

        if not user:
            return False

        if not user.is_active or not user.is_authenticated:
            return False

        try:
            structure = get_object_or_404(Structure, pk=request.POST["assigned_by_structure"])
        except Exception:
            return True


        return any([
            #user.is_superuser,
            is_structure_editor(user, structure),
            is_structure_admin(user, structure)
        ])

class CanEndorseBadge(permissions.BasePermission):
    def has_permission(self, request, view):
        # Return true because the GET method only show the template
        if request.method == "GET":
            return True

        user = request.user
        structure = get_object_or_404(Structure, pk=request.POST["structure"])

        if not user:
            return False

        if not user.is_active or not user.is_authenticated:
            return False

        return any([
            ##user.is_superuser,
            is_structure_editor(user, structure),
            is_structure_admin(user, structure)
        ])


#### Methods ####
def is_structure_editor(user, structure):
    if not user:
        return False

    if not user.is_active or not user.is_authenticated:
        return False

    return any([
        #user.is_superuser,
        structure.is_editor(user),
        structure.is_admin(user),
    ])

def is_structure_admin(user, structure):
    if not user:
        return False

    if not user.is_active or not user.is_authenticated:
        return False

    return any([
        #user.is_superuser,
        structure.is_admin(user),
    ])

