from rest_framework import permissions
from django.shortcuts import get_object_or_404

from core.models import Badge, Structure, User, Course


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
        badge = Badge.objects.get(pk=pk)

        if badge.issuing_structure:
            return is_structure_editor(user, badge.issuing_structure)
        elif badge.user:
            return badge.user==request.user

        return False


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
    """
    Verifie que l'utilisateur est admin de la structure pour attribuer un badge.
    / Check that the user is admin of the structure to assign a badge.
    """
    message = "Seuls les admins peuvent attribuer un badge"

    def has_permission(self, request, view):
        # GET affiche le formulaire, on laisse passer (le filtre se fait dans la vue)
        # / GET shows the form, let it through (filtering is done in the view)
        if request.method == "GET":
            return True

        user = request.user

        if not user or not user.is_active or not user.is_authenticated:
            return False

        try:
            structure = get_object_or_404(Structure, pk=request.POST["assigned_by_structure"])
        except Exception:
            return True

        return is_structure_admin(user, structure)


class CanEndorseBadge(permissions.BasePermission):
    """
    Verifie que l'utilisateur est admin de la structure pour endosser un badge.
    / Check that the user is admin of the structure to endorse a badge.
    """
    message = "Seuls les admins peuvent endosser un badge"

    def has_permission(self, request, view):
        # GET affiche le formulaire, on laisse passer (le filtre se fait dans la vue)
        # / GET shows the form, let it through (filtering is done in the view)
        if request.method == "GET":
            return True

        user = request.user

        if not user or not user.is_active or not user.is_authenticated:
            return False

        try:
            structure = get_object_or_404(Structure, pk=request.POST["structure"])
        except Exception:
            return False

        return is_structure_admin(user, structure)


class CanEditCourse(permissions.BasePermission):
    def has_permission(self, request, view):
        pk = view.kwargs.get("pk")
        course = Course.objects.get(pk=pk)
        if course.is_dream:
            return course.user == request.user

        return is_structure_editor(request.user, course.structure)


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

