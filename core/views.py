from django.contrib.auth import logout, get_user_model, authenticate, login
from django.core.exceptions import ValidationError, PermissionDenied
from django.core.signing import SignatureExpired
from django.core.validators import validate_email
from django.http import HttpResponseForbidden
from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q
from django.urls import reverse
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import action

from .helpers import TokenHelper
from .helpers.utils import get_or_create_user
from .models import Structure, Badge, User
from .forms import BadgeForm, StructureForm, UserForm, PartialUserForm
import sweetify

def raise403(request):
    """
    Return a not authorize error (403).
    Usage example (in another method) :
        return raise403(request)
    """
    return render(request, 'errors/403.html', status=403)


class HomeViewSet(viewsets.ViewSet):
    """
    ViewSet for the home page of the site.
    """
    def list(self, request):
        # Get some recent badges and structures for the home page
        recent_badges = Badge.objects.all().order_by('-pk')[:4]
        popular_structures = Structure.objects.all().order_by('-pk')[:4]

        return render(request, 'core/home/index.html', {
            'title': 'FossBadge - Accueil',
            'recent_badges': recent_badges,
            'popular_structures': popular_structures
        })

class BadgeViewSet(viewsets.ViewSet):
    """
    ViewSet for badge-related pages.
    """
    def list(self, request):
        """
        List all badges.
        """
        # Get search query
        search_query = request.GET.get('search', '')
        level_filter = request.GET.getlist('level', [])
        structure_filter = request.GET.get('structure', '')

        # Start with all badges
        badges = Badge.objects.all()

        # Apply search filter if provided
        if search_query:
            badges = badges.filter(
                Q(name__icontains=search_query) | 
                Q(description__icontains=search_query) |
                Q(issuing_structure__name__icontains=search_query)
            )

        # Apply level filter if provided
        if level_filter:
            badges = badges.filter(level__in=level_filter)

        # Apply structure filter if provided
        if structure_filter:
            badges = badges.filter(issuing_structure_id=structure_filter)

        # Get all structures for the filter dropdown
        structures = Structure.objects.all()

        # Check if this is an HTMX request
        if request.htmx:
            # For HTMX requests, only return the badge list part
            return render(request, 'core/badges/partials/badge_list.html', {
                'badges': badges,
                'search_query': search_query,
                'level_filter': level_filter,
                'structure_filter': structure_filter
            })
        else:
            # For regular requests, return the full page
            return render(request, 'core/badges/list.html', {
                'title': 'FossBadge - Liste des Badges',
                'badges': badges,
                'structures': structures,
                'search_query': search_query,
                'level_filter': level_filter,
                'structure_filter': structure_filter
            })

    def retrieve(self, request, pk=None):
        """
        Display a specific badge.
        """
        badge = get_object_or_404(Badge, pk=pk)
        holders = badge.get_holders()

        return render(request, 'core/badges/detail.html', {
            'title': f'FossBadge - Badge {badge.name}',
            'badge': badge,
            'holders': holders
        })

    @action(detail=True, methods=["get","post"])
    def edit(self, request, pk=None):
        """
        Edit an existing badge.
        """
        badge = get_object_or_404(Badge, pk=pk)
        if request.method == 'POST':
            form = BadgeForm(request.POST, request.FILES, instance=badge)
            if form.is_valid():
                form.save()
                return redirect(reverse('core:badge-detail', kwargs={'pk': badge.pk}))
        else:
            form = BadgeForm(instance=badge)

        icon = None
        if badge.icon:
            icon = badge.icon.url

        return render(request,"core/badges/edit.html",{"form":form,"icon":icon})

    @action(detail=True, methods=["get", "post"])
    def delete(self, request, pk=None):
        """
        Delete an existing badge.
        """
        badge = get_object_or_404(Badge, pk=pk)
        if request.method == 'POST':
            badge.delete()
            return redirect(reverse('core:badge-list'))

        badge_holders = badge.get_holders()
        return render(request, 'core/badges/delete.html', {"badge": badge, "holders": badge_holders})

    @action(detail=False, methods=['get', 'post'])
    def create_badge(self, request):
        """
        Create a new badge.
        """

        # If badge is created from a structure page, get the structure
        default_structure = request.GET.get('structure', '')

        if request.method == 'POST':
            form = BadgeForm(request.POST, request.FILES)
            if form.is_valid():
                badge = form.save()
                # Create a history entry for badge creation
                from .models import BadgeHistory
                BadgeHistory.objects.create(
                    badge=badge,
                    action="creation",
                    details="Badge créé"
                )
                return redirect(reverse('core:badge-detail', kwargs={'pk': badge.pk}))
        else:
            form = BadgeForm(initial={'issuing_structure':default_structure})

        # Get all structures for the dropdown
        structures = Structure.objects.all()

        return render(request, 'core/badges/create.html', {
            'title': 'FossBadge - Forger un Badge',
            'structures': structures,
            'form': form
        })

class StructureViewSet(viewsets.ViewSet):
    """
    ViewSet for structure/company-related pages.
    """
    def list(self, request):
        """
        List all structures.
        """
        # Get search query
        search_query = request.GET.get('search', '')
        type_filter = request.GET.getlist('type', [])
        badge_filter = request.GET.get('badge', '')

        # Start with all structures
        structures = Structure.objects.all()

        # Apply search filter if provided
        if search_query:
            structures = structures.filter(
                Q(name__icontains=search_query) | 
                Q(description__icontains=search_query)
            )

        # Apply type filter if provided
        if type_filter:
            structures = structures.filter(type__in=type_filter)

        # Apply badge filter if provided
        if badge_filter:
            structures = structures.filter(
                Q(issued_badges__id=badge_filter) | 
                Q(valid_badges__id=badge_filter)
            ).distinct()

        # Check if this is an HTMX request
        if request.htmx:
            # For HTMX requests, only return the badge list part
            return render(request, 'core/structures/partials/structure_list.html', {
                'structures': structures,
                'search_query': search_query,
                'type_filter': type_filter,
                'badge_filter': badge_filter
            })
        else:
            # Get all badges for the filter dropdown
            badges = Badge.objects.all()
            # For regular requests, return the full page
            return render(request, 'core/structures/list.html', {
                'title': 'FossBadge - Liste des Structures',
                'structures': structures,
                'badges': badges,
                'search_query': search_query,
                'type_filter': type_filter,
                'badge_filter': badge_filter
            })

    def retrieve(self, request, pk=None):
        """
        Display a specific structure.
        """
        structure = get_object_or_404(Structure, pk=pk)

        # Get badges issued by this structure
        issued_badges = structure.issued_badges.all()

        return render(request, 'core/structures/detail.html', {
            'title': f'FossBadge - Structure {structure.name}',
            'structure': structure,
            'issued_badges': issued_badges
        })

    @action(detail=True, methods=["get","post"])
    def edit(self, request, pk=None):
        """
        Edit an existing structure.
        """
        structure = get_object_or_404(Structure, pk=pk)
        if request.method == 'POST':
            form = StructureForm(request.POST, request.FILES, instance=structure)
            if form.is_valid():
                form.save()
                return redirect(reverse('core:structure-detail', kwargs={'pk': structure.pk}))
        else:
            form = StructureForm(instance=structure)

        logo = None
        if structure.logo:
            logo = structure.logo.url

        return render(request,"core/structures/edit.html",{"form":form,"logo":logo})

    @action(detail=True, methods=["get","post"])
    def delete(self, request, pk=None):
        """
        Delete an existing structure.
        """
        structure = get_object_or_404(Structure, pk=pk)
        if request.method == 'POST':
            structure.delete()
            return redirect(reverse('core:structure-list'))

        issued_badges = structure.issued_badges.all()
        return render(request, 'core/structures/delete.html', {"structure": structure,"badges": issued_badges})

    @action(detail=False, methods=['get', 'post'])
    def create_association(self, request):
        """
        Create a new structure/company.
        """
        if request.method == 'POST':
            form = StructureForm(request.POST, request.FILES)
            if form.is_valid():
                structure = form.save()
                return redirect(reverse('core:structure-detail', kwargs={'pk': structure.pk}))
        else:
            form = StructureForm()

        return render(request, 'core/structures/create.html', {
            'title': 'FossBadge - Créer une Structure / Entreprise',
            'form': form
        })

class UserViewSet(viewsets.ViewSet):
    """
    ViewSet for user-related pages.
    """
    @action(detail=True, methods=['get'])
    def cv(self, request, pk=None):
        """
        Display a user's CV based on their badges.

        Query Parameters:
            template (str): The template to use. Options: 'bootstrap' or 'classic' (default).
        """
        user = get_object_or_404(User, pk=pk)

        # Check which template to use
        template_type = request.GET.get('template', 'classic')
        if template_type == 'bootstrap':
            template_name = 'core/users/cv_bootstrap.html'
        elif template_type == 'material':
            template_name = 'core/users/cv_material.html'
        elif template_type == 'liquid_glass':
            template_name = 'core/users/cv_liquid_glass.html'
        else:
            template_name = 'core/users/cv.html'

        # Get user's badges, badge assignments, and structures
        badges = Badge.objects.filter(assignments__user=user)
        badge_assignments = user.badge_assignments.all()
        # Create a dictionary to easily look up assignments by badge ID
        badge_assignment_dict = {assignment.badge_id: assignment for assignment in badge_assignments}

        structures = user.structures.all()

        return render(request, template_name, {
            'title': f'CV de {user.get_full_name() or user.username}',
            'user': user,
            'badges': badges,
            'badge_assignment_dict': badge_assignment_dict,
            'structures': structures,
            'template_type': template_type
        })

    def list(self, request):
        """
        List all users.
        """
        # Get search query and filters
        search_query = request.GET.get('search', '')
        badge_filter = request.GET.get('badge', '')
        structure_filter = request.GET.get('structure', '')
        level_filter = request.GET.getlist('level', [])

        # Start with all users
        users = User.objects.all()

        # Apply search filter if provided
        if search_query:
            users = users.filter(
                Q(username__icontains=search_query) | 
                Q(first_name__icontains=search_query) |
                Q(last_name__icontains=search_query) |
                Q(email__icontains=search_query)
            )

        # Apply badge filter if provided
        if badge_filter:
            users = users.filter(badge_assignments__badge__id=badge_filter).distinct()

        # Apply structure filter if provided
        if structure_filter:
            users = users.filter(structures__id=structure_filter).distinct()

        # Apply level filter if provided
        if level_filter:
            users = users.filter(badge_assignments__badge__level__in=level_filter).distinct()

        # Check if this is an HTMX request
        if request.htmx:
            # For HTMX requests, only return the user list part
            return render(request, 'core/users/partials/user_list.html',{
                'users': users,
                'search_query': search_query,
                'badge_filter': badge_filter,
                'structure_filter': structure_filter,
                'level_filter': level_filter,
            })
        else:
            # Get all badges and structures for the filter dropdowns
            badges = Badge.objects.all()
            structures = Structure.objects.all()

            # For regular requests, return the full page
            return render(request, 'core/users/list.html', {
                'title': 'FossBadge - Liste des Profils',
                'users': users,
                'badges': badges,
                'structures': structures,
                'search_query': search_query,
                'badge_filter': badge_filter,
                'structure_filter': structure_filter,
                'level_filter': level_filter
            })

    def retrieve(self, request, pk=None):
        """
        Display a specific user profile.
        """
        user = get_object_or_404(User, pk=pk)

        # Get user's badges, badge assignments, and structures
        badges = Badge.objects.filter(assignments__user=user)
        badge_assignments = user.badge_assignments.all()
        # Create a dictionary to easily look up assignments by badge ID
        badge_assignment_dict = {assignment.badge_id: assignment for assignment in badge_assignments}

        structures = user.structures.all()

        return render(request, 'core/users/detail.html', {
            'title': f'FossBadge - Profil de {user.get_full_name() or user.username}',
            'user': user,
            'badges': badges,
            'badge_assignment_dict': badge_assignment_dict,
            'structures': structures
        })

    @action(detail=False, methods=['get', 'post'])
    def create_user(self, request):
        """
        Create a new user.
        """
        if request.method == 'POST':
            form = UserForm(request.POST, request.FILES)
            if form.is_valid():
                user = form.save(commit=False)
                user.username = f"{form.cleaned_data['first_name']}.{form.cleaned_data['last_name']}".lower()
                user.set_password(form.cleaned_data['password'])
                user.save()

                return redirect(reverse('core:user-detail', kwargs={'pk': user.pk}))
        else:
            form = UserForm()

        return render(request, 'core/users/create.html', {
            'title': 'FossBadge - Créer un utilisateur',
            'form': form,
        })

    @action(detail=True, methods=['get', 'post'],name="edit-profile")
    def edit(self,request,pk=None):
        """
        Edit an existing user.
        """
        if request.user.pk != pk:
            return raise403(request)

        user = get_object_or_404(User, pk=pk)

        if request.method == 'POST':
            form = PartialUserForm(request.POST, instance=user)
            if form.is_valid():
                form.save()
                user = User.objects.get(pk=pk)
                return render(request, 'core/users/partials/user_profile_info.html', {'user': user})

        if not request.htmx:
            return redirect(reverse('core:user-detail', kwargs={'pk': pk}))
        form = PartialUserForm(instance=user)
        return render(request, 'core/users/partials/user_profile_edit.html', {'user': user, 'form': form})

    @action(detail=True, methods=['post'])
    def delete(self, request, pk=None):
        """
        Delete a user.
        """
        # TODO when authentication will be added :
        # Send a mail containing a link to delete the account
        if request.user.pk != pk:
            return raise403(request)

        sweetify.toast(request, "L'utilisateur a bien été désactivé",showCloseButton=True, timer=10000)
        user = get_object_or_404(User, pk=pk)
        user.is_active = False
        user.save()
        return redirect('core:user-list')

    @action(detail=False, methods=['get','post'], url_name="login")
    def login_request(self, request):
        if not request.htmx:
            return raise403(request)

        if request.method == 'GET':
            return render(request, 'authentication/login.html')

        email = request.POST['email']
        try:
            # Raise an exception if mail is invalide
            validate_email(email)

            # Send an email to the user
            get_or_create_user(email,send_mail=True)

            return render(request, 'authentication/login.html', {
                "success": "Le mail a bien été envoyé",
            })

        except ValidationError as e:
            # return same templates, with error
            return render(request, 'authentication/login.html', {
                "error":e.message,
                "placeholder": email,
            })

    @action(detail=False, methods=['get'])
    def login_from_email(self, request):
        token = request.GET['token']
        try:
            user_pk = TokenHelper.is_user_token_valid(token)
            user = get_user_model().objects.get(pk=user_pk)

            # Set user to active
            if not user.is_active:
                user.is_active = True
                user.save()

            login(request, user)

            sweetify.toast(request, f"Connexion réussi !", showCloseButton=True, timer=10000)
            return redirect('core:home-list')
        except SignatureExpired:
            sweetify.toast(request, f"Ce lien est expiré, veuillez refaire une demande de connexion", icon="error",showCloseButton=True, timer=10000)
            return redirect('core:home-list')
        except Exception:
            sweetify.toast(request, f"Ce lien est invalide, veuillez refaire une demande de connexion", icon="error",showCloseButton=True, timer=10000)
            return redirect('core:home-list')

    @action(detail=False, methods=['get'])
    def logout(self, request):
        logout(request)
        sweetify.toast(request, f"Déconnexion réussi", icon="success", showCloseButton=True, timer=10000)
        return redirect('core:home-list')