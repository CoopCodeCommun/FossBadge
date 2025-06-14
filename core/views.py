from django.shortcuts import render

# Create your views here.
def home(request):
    """
    View function for the home page of the site.
    """
    return render(request, 'core/index.html', {
        'title': 'FossBadge - Accueil'
    })

def badge_list(request):
    """
    View function for the badge list page.
    """
    return render(request, 'core/badge_list.html', {
        'title': 'FossBadge - Liste des Badges'
    })

def structure_list(request):
    """
    View function for the structure list page.
    """
    return render(request, 'core/structure_list.html', {
        'title': 'FossBadge - Liste des Structures'
    })

def user_list(request):
    """
    View function for the user list page.
    """
    return render(request, 'core/user_list.html', {
        'title': 'FossBadge - Liste des Profils'
    })

def user_profile(request):
    """
    View function for the user profile page.
    """
    return render(request, 'core/user.html', {
        'title': 'FossBadge - Profil Utilisateur'
    })

def badge_detail(request):
    """
    View function for the badge detail page.
    """
    return render(request, 'core/badge.html', {
        'title': 'FossBadge - Détails du Badge'
    })

def association_detail(request):
    """
    View function for the structure/company detail page.
    """
    return render(request, 'core/association.html', {
        'title': 'FossBadge - Structure / Entreprise'
    })

def create_badge(request):
    """
    View function for the badge creation page.
    """
    return render(request, 'core/create_badge.html', {
        'title': 'FossBadge - Forger un Badge'
    })

def create_association(request):
    """
    View function for the structure/company creation page.
    """
    return render(request, 'core/create_association.html', {
        'title': 'FossBadge - Créer une Structure / Entreprise'
    })
