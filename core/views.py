from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.models import User
from django.db.models import Q
from django.urls import reverse
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import action

from .models import Structure, Badge, UserProfile
from .forms import BadgeForm, StructureForm

# Create your views here.
class HomeViewSet(viewsets.ViewSet):
    """
    ViewSet for the home page of the site.
    """
    def list(self, request):
        # Get some recent badges and structures for the home page
        recent_badges = Badge.objects.all().order_by('-id')[:4]
        popular_structures = Structure.objects.all().order_by('-id')[:4]

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

        return render(request, 'core/badges/detail.html', {
            'title': f'FossBadge - Badge {badge.name}',
            'badge': badge
        })

    @action(detail=False, methods=['get', 'post'])
    def create_badge(self, request):
        """
        Create a new badge.
        """
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
            form = BadgeForm()

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

        # Get all badges for the filter dropdown
        badges = Badge.objects.all()

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

        # Get all badges and structures for the filter dropdowns
        badges = Badge.objects.all()
        structures = Structure.objects.all()

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
        try:
            profile = user.profile
            badges = Badge.objects.filter(assignments__user=user)
            badge_assignments = user.badge_assignments.all()
            # Create a dictionary to easily look up assignments by badge ID
            badge_assignment_dict = {assignment.badge_id: assignment for assignment in badge_assignments}
        except UserProfile.DoesNotExist:
            badges = Badge.objects.none()
            badge_assignment_dict = {}
        structures = user.structures.all()

        return render(request, 'core/users/detail.html', {
            'title': f'FossBadge - Profil de {user.get_full_name() or user.username}',
            'user_profile': user,
            'badges': badges,
            'badge_assignment_dict': badge_assignment_dict,
            'structures': structures
        })
