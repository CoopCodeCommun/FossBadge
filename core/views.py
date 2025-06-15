from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import action

# Create your views here.
class HomeViewSet(viewsets.ViewSet):
    """
    ViewSet for the home page of the site.
    """
    def list(self, request):
        return render(request, 'core/home/index.html', {
            'title': 'FossBadge - Accueil'
        })

class BadgeViewSet(viewsets.ViewSet):
    """
    ViewSet for badge-related pages.
    """
    def list(self, request):
        """
        List all badges.
        """
        return render(request, 'core/badges/list.html', {
            'title': 'FossBadge - Liste des Badges'
        })

    def retrieve(self, request, pk=None):
        """
        Display a specific badge.
        """
        return render(request, 'core/badges/detail.html', {
            'title': 'FossBadge - Détails du Badge'
        })

    @action(detail=False, methods=['get', 'post'])
    def create_badge(self, request):
        """
        Create a new badge.
        """
        return render(request, 'core/badges/create.html', {
            'title': 'FossBadge - Forger un Badge'
        })

class StructureViewSet(viewsets.ViewSet):
    """
    ViewSet for structure/company-related pages.
    """
    def list(self, request):
        """
        List all structures.
        """
        return render(request, 'core/structures/list.html', {
            'title': 'FossBadge - Liste des Structures'
        })

    def retrieve(self, request, pk=None):
        """
        Display a specific structure.
        """
        return render(request, 'core/structures/detail.html', {
            'title': 'FossBadge - Structure / Entreprise'
        })

    @action(detail=False, methods=['get', 'post'])
    def create_association(self, request):
        """
        Create a new structure/company.
        """
        return render(request, 'core/structures/create.html', {
            'title': 'FossBadge - Créer une Structure / Entreprise'
        })

class UserViewSet(viewsets.ViewSet):
    """
    ViewSet for user-related pages.
    """
    def list(self, request):
        """
        List all users.
        """
        return render(request, 'core/users/list.html', {
            'title': 'FossBadge - Liste des Profils'
        })

    def retrieve(self, request, pk=None):
        """
        Display a specific user profile.
        """
        return render(request, 'core/users/detail.html', {
            'title': 'FossBadge - Profil Utilisateur'
        })
