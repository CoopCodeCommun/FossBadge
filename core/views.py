from django.conf import settings
from django.contrib import messages
from django.contrib.auth import logout, get_user_model, authenticate, login
from django.core.exceptions import ValidationError, PermissionDenied
from django.core.signing import SignatureExpired
from django.core.validators import validate_email
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q
from django.urls import reverse
from django_htmx.http import HttpResponseClientRedirect
from rest_framework import viewsets
from rest_framework.authentication import SessionAuthentication
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.decorators import action,authentication_classes, permission_classes
from .helpers import TokenHelper
from .helpers.utils import get_or_create_user, invite_user_to_structure
from .models import Structure, Badge, User, BadgeAssignment
from .forms import BadgeForm, StructureForm, UserForm, PartialUserForm
import sweetify

from .permissions import IsBadgeEditor, IsStructureAdmin, CanEditUser, CanAssignBadge, CanEndorseBadge
from .validators import BadgeAssignmentValidator, BadgeEndorsementValidator


def raise403(request, msg=None):
    """
    Return a not authorize error (403).
    Usage example (in another method) :
        return raise403(request)
    """
    return render(request, 'errors/403.html', status=403, context={
        "message": msg
    })

def raise404(request, msg=None):
    """
    Return a not found error (404).
    Usage example (in another method) :
        return raise404(request)
    """
    return render(request, 'errors/404.html', status=404, context={
        "message": msg
    })

def reload(request):
    return HttpResponseClientRedirect(request.headers['Referer'])


def read_category_filters(request):
    """
    Lit les filtres de catégorie depuis les paramètres GET.
    Les checkboxes non cochées ne sont pas envoyées.
    Si aucun filtre n'est présent, on active tout par défaut.

    Reads category filters from GET params.
    Unchecked checkboxes are not sent.
    If no filter param is present, all are enabled by default.
    """
    has_any_filter_param = any(
        param in request.GET for param in ('badges', 'structures', 'personnes')
    )
    if has_any_filter_param:
        return {
            'search_badges_enabled': 'badges' in request.GET,
            'search_structures_enabled': 'structures' in request.GET,
            'search_personnes_enabled': 'personnes' in request.GET,
        }
    return {
        'search_badges_enabled': True,
        'search_structures_enabled': True,
        'search_personnes_enabled': True,
    }


class HomeViewSet(viewsets.ViewSet):
    """
    ViewSet pour la page d'accueil avec recherche unifiée.
    ViewSet for the home page with unified search.
    """

    def list(self, request):
        # Page d'accueil — champ de recherche centré, pas de données
        # Home page — centered search field, no data
        return render(request, 'core/home/index.html', {
            'title': 'FossBadge',
        })

    @action(detail=False, methods=["GET"])
    def search(self, request):
        """
        Recherche unifiée sur badges, structures et personnes.
        Fouille dans tous les champs pertinents : noms, descriptions,
        notes d'endorsement, badges assignés, etc.
        Retourne un partiel HTML avec 3 colonnes de résultats.

        Unified search across badges, structures and people.
        Searches all relevant fields: names, descriptions,
        endorsement notes, assigned badges, etc.
        Returns an HTML partial with 3 result columns.
        """
        search_query = request.GET.get('q', '').strip()

        # Si la requête est trop courte, retourner un partiel vide
        # If query is too short, return empty partial
        query_is_too_short = len(search_query) < 4
        if query_is_too_short:
            return HttpResponse('')

        # Lire les filtres de catégorie / Read category filters
        category_filters = read_category_filters(request)
        search_badges_enabled = category_filters['search_badges_enabled']
        search_structures_enabled = category_filters['search_structures_enabled']
        search_personnes_enabled = category_filters['search_personnes_enabled']

        # Limite de résultats par catégorie / Result limit per category
        max_results_per_category = 5

        # --- Badges ---
        badges_found_list = []
        if search_badges_enabled:
            # Cherche dans : nom, description, structure émettrice, notes d'endorsement
            # Search in: name, description, issuing structure, endorsement notes
            badges_found_list = Badge.objects.select_related('issuing_structure').filter(
                Q(name__icontains=search_query)
                | Q(description__icontains=search_query)
                | Q(issuing_structure__name__icontains=search_query)
                | Q(endorsements__notes__icontains=search_query)
            ).distinct()[:max_results_per_category]

        # --- Structures ---
        structures_found_list = []
        if search_structures_enabled:
            # Cherche dans : nom, description, noms des badges émis
            # Search in: name, description, issued badge names
            structures_found_list = Structure.objects.select_related('marker').filter(
                Q(name__icontains=search_query)
                | Q(description__icontains=search_query)
                | Q(issued_badges__name__icontains=search_query)
            ).distinct()[:max_results_per_category]

        # --- Personnes ---
        people_found_list = []
        if search_personnes_enabled:
            # Cherche dans : prénom, nom, pseudo, ET aussi dans les noms/descriptions
            # des badges que la personne possède, et les notes d'assignation
            # Search in: first name, last name, username, AND also in names/descriptions
            # of badges the person holds, and assignment notes
            people_found_list = User.objects.filter(
                Q(first_name__icontains=search_query)
                | Q(last_name__icontains=search_query)
                | Q(username__icontains=search_query)
                | Q(badge_assignments__badge__name__icontains=search_query)
                | Q(badge_assignments__badge__description__icontains=search_query)
                | Q(badge_assignments__notes__icontains=search_query)
            ).distinct()[:max_results_per_category]

        # PKs des structures trouvées avec marker (pour la carte)
        # PKs of found structures with markers (for the map)
        structures_pks_csv = ','.join(
            str(s.pk) for s in structures_found_list
            if hasattr(s, 'marker') and s.marker_id
        )

        search_context = {
            'badges_found_list': badges_found_list,
            'structures_found_list': structures_found_list,
            'people_found_list': people_found_list,
            'search_query': search_query,
            'search_badges_enabled': search_badges_enabled,
            'search_structures_enabled': search_structures_enabled,
            'search_personnes_enabled': search_personnes_enabled,
            'structures_pks_csv': structures_pks_csv,
        }

        # Requête HTMX → retourner seulement le partiel des résultats
        # HTMX request → return only the results partial
        if request.htmx:
            return render(request, 'core/home/partial/search_results.html', search_context)

        # Requête classique (fallback sans JS) → retourner la page complète avec résultats
        # Regular request (no-JS fallback) → return full page with results
        search_context['title'] = 'FossBadge — Recherche'
        return render(request, 'core/home/index.html', search_context)

    @action(detail=False, methods=["GET"], url_path="badge-focus/(?P<badge_pk>[^/.]+)")
    def badge_focus(self, request, badge_pk=None):
        """
        Vue focus sur un badge : affiche le badge en détail dans la colonne gauche,
        les structures liées (émettrice + endorseuses) au centre,
        et les personnes qui possèdent ce badge à droite.
        Remplace les résultats de recherche sans quitter la page /home.

        Badge focus view: shows badge detail in the left column,
        related structures (issuer + endorsers) in the center,
        and people who hold this badge on the right.
        Replaces search results without leaving /home.
        """
        badge_focused = get_object_or_404(
            Badge.objects.select_related('issuing_structure'), uuid=badge_pk
        )

        # Structures liées : la structure émettrice + celles qui endossent ce badge
        # Related structures: the issuing structure + those endorsing this badge
        related_structures_list = Structure.objects.select_related('marker').filter(
            Q(pk=badge_focused.issuing_structure_id)
            | Q(endorsements__badge=badge_focused)
        ).distinct()

        # Personnes qui possèdent ce badge (via BadgeAssignment)
        # People who hold this badge (via BadgeAssignment)
        related_people_list = User.objects.filter(
            badge_assignments__badge=badge_focused
        ).distinct()

        # Conserver la requête de recherche pour le bouton retour
        # Keep the search query for the back button
        search_query_for_back = request.GET.get('q', '')

        # Lire les filtres de catégorie / Read category filters
        category_filters = read_category_filters(request)

        # PKs des structures liées avec marker (pour la carte)
        # PKs of related structures with markers (for the map)
        related_structures_pks = ','.join(
            str(s.pk) for s in related_structures_list
            if hasattr(s, 'marker') and s.marker_id
        )

        badge_focus_context = {
            'focused_badge': badge_focused,
            'related_structures_list': related_structures_list,
            'related_people_list': related_people_list,
            'search_query': search_query_for_back,
            'related_structures_pks': related_structures_pks,
            **category_filters,
        }

        # Requête HTMX → retourner seulement le partiel focus
        # HTMX request → return only the focus partial
        if request.htmx:
            return render(request, 'core/home/partial/badge_focus.html', badge_focus_context)

        # Requête directe (fallback sans JS) → page complète avec focus pré-rempli
        # Direct request (no-JS fallback) → full page with pre-filled focus
        badge_focus_context['focus_partial'] = 'core/home/partial/badge_focus.html'
        return render(request, 'core/home/index.html', badge_focus_context)

    @action(detail=False, methods=["GET"], url_path="structure-focus/(?P<structure_pk>[^/.]+)")
    def structure_focus(self, request, structure_pk=None):
        """
        Vue focus sur une structure : affiche la structure en détail dans la colonne gauche,
        les badges liés (émis + endossés) au centre,
        et les membres de la structure à droite.

        Structure focus view: shows structure detail in the left column,
        related badges (issued + endorsed) in the center,
        and structure members on the right.
        """
        structure_focused = get_object_or_404(Structure, uuid=structure_pk)

        # Badges liés : émis par cette structure OU endossés par elle
        # Related badges: issued by this structure OR endorsed by it
        related_badges_list = Badge.objects.select_related('issuing_structure').filter(
            Q(issuing_structure=structure_focused)
            | Q(endorsements__structure=structure_focused)
        ).distinct()

        # Membres de la structure (admins + éditeurs + utilisateurs)
        # Structure members (admins + editors + users)
        related_people_list = User.objects.filter(
            Q(structures_admins=structure_focused)
            | Q(structures_editors=structure_focused)
            | Q(structures_users=structure_focused)
        ).distinct()

        # Conserver la requête de recherche pour le bouton retour
        # Keep the search query for the back button
        search_query_for_back = request.GET.get('q', '')

        category_filters = read_category_filters(request)

        structure_focus_context = {
            'focused_structure': structure_focused,
            'related_badges_list': related_badges_list,
            'related_people_list': related_people_list,
            'search_query': search_query_for_back,
            **category_filters,
        }

        if request.htmx:
            return render(request, 'core/home/partial/structure_focus.html', structure_focus_context)

        structure_focus_context['focus_partial'] = 'core/home/partial/structure_focus.html'
        return render(request, 'core/home/index.html', structure_focus_context)

    @action(detail=False, methods=["GET"], url_path="multi-focus")
    def multi_focus(self, request):
        """
        Vue multi-focus : sélectionner 2 ou 3 objets de colonnes différentes.
        Avec 2 items : affiche les 2 en détail + l'intersection dans la 3e colonne.
        Avec 3 items : affiche les 3 en détail, pas d'intersection.

        Multi-focus view: select 2 or 3 objects from different columns.
        With 2 items: shows both in detail + intersection in 3rd column.
        With 3 items: shows all 3 in detail, no intersection.
        """
        badge_pk = request.GET.get('badge')
        structure_pk = request.GET.get('structure')
        person_pk = request.GET.get('person')

        # Au moins 2 params sur 3 doivent être fournis
        # At least 2 out of 3 params must be provided
        provided_params_count = sum(1 for p in [badge_pk, structure_pk, person_pk] if p)
        if provided_params_count < 2:
            return HttpResponse('', status=400)

        selected_badge = None
        selected_structure = None
        selected_person = None
        intersection_type = ''
        intersection_list = []

        if badge_pk:
            selected_badge = get_object_or_404(
                Badge.objects.select_related('issuing_structure'), uuid=badge_pk
            )
        if structure_pk:
            selected_structure = get_object_or_404(
                Structure.objects.select_related('marker'), uuid=structure_pk
            )
        if person_pk:
            selected_person = get_object_or_404(User, uuid=person_pk)

        # Intersection seulement avec 2 items / Intersection only with 2 items
        if provided_params_count == 2:
            # Badge + Structure → Personnes à l'intersection
            # Badge + Structure → People at the intersection
            if selected_badge and selected_structure:
                intersection_type = 'personnes'
                intersection_list = User.objects.filter(
                    badge_assignments__badge=selected_badge,
                ).filter(
                    Q(structures_admins=selected_structure)
                    | Q(structures_editors=selected_structure)
                    | Q(structures_users=selected_structure)
                ).distinct()

            # Badge + Personne → Structures à l'intersection
            # Badge + Person → Structures at the intersection
            elif selected_badge and selected_person:
                intersection_type = 'structures'
                intersection_list = Structure.objects.filter(
                    Q(issued_badges=selected_badge)
                    | Q(endorsements__badge=selected_badge)
                ).filter(
                    Q(admins=selected_person)
                    | Q(editors=selected_person)
                    | Q(users=selected_person)
                ).distinct()

            # Structure + Personne → Badges à l'intersection
            # Structure + Person → Badges at the intersection
            elif selected_structure and selected_person:
                intersection_type = 'badges'
                intersection_list = Badge.objects.filter(
                    assignments__user=selected_person,
                ).filter(
                    Q(issuing_structure=selected_structure)
                    | Q(endorsements__structure=selected_structure)
                ).distinct()

        search_query_for_back = request.GET.get('q', '')
        category_filters = read_category_filters(request)

        # PKs des structures avec marker pour la carte
        # PKs of structures with markers for the map
        multi_structures_pks = ''
        if selected_structure and hasattr(selected_structure, 'marker') and selected_structure.marker_id:
            multi_structures_pks = str(selected_structure.pk)

        multi_focus_context = {
            'selected_badge': selected_badge,
            'selected_structure': selected_structure,
            'selected_person': selected_person,
            'intersection_type': intersection_type,
            'intersection_list': intersection_list,
            'items_count': provided_params_count,
            'search_query': search_query_for_back,
            'multi_structures_pks': multi_structures_pks,
            **category_filters,
        }

        if request.htmx:
            return render(request, 'core/home/partial/multi_focus.html', multi_focus_context)

        multi_focus_context['focus_partial'] = 'core/home/partial/multi_focus.html'
        return render(request, 'core/home/index.html', multi_focus_context)

    @action(detail=False, methods=["GET"], url_path="person-focus/(?P<person_pk>[^/.]+)")
    def person_focus(self, request, person_pk=None):
        """
        Vue focus sur une personne : affiche la personne en détail dans la colonne gauche,
        les badges qu'elle possède au centre,
        et les structures auxquelles elle appartient à droite.

        Person focus view: shows person detail in the left column,
        badges they hold in the center,
        and structures they belong to on the right.
        """
        person_focused = get_object_or_404(User, uuid=person_pk)

        # Badges possédés par cette personne (via BadgeAssignment)
        # Badges held by this person (via BadgeAssignment)
        related_badges_list = Badge.objects.select_related('issuing_structure').filter(
            assignments__user=person_focused
        ).distinct()

        # Structures auxquelles la personne appartient (admin, éditeur ou utilisateur)
        # Structures the person belongs to (admin, editor or user)
        related_structures_list = Structure.objects.select_related('marker').filter(
            Q(admins=person_focused)
            | Q(editors=person_focused)
            | Q(users=person_focused)
        ).distinct()

        # Conserver la requête de recherche pour le bouton retour
        # Keep the search query for the back button
        search_query_for_back = request.GET.get('q', '')

        category_filters = read_category_filters(request)

        # PKs des structures liées avec marker (pour la carte)
        # PKs of related structures with markers (for the map)
        related_structures_pks = ','.join(
            str(s.pk) for s in related_structures_list
            if hasattr(s, 'marker') and s.marker_id
        )

        person_focus_context = {
            'focused_person': person_focused,
            'related_badges_list': related_badges_list,
            'related_structures_list': related_structures_list,
            'search_query': search_query_for_back,
            'related_structures_pks': related_structures_pks,
            **category_filters,
        }

        if request.htmx:
            return render(request, 'core/home/partial/person_focus.html', person_focus_context)

        person_focus_context['focus_partial'] = 'core/home/partial/person_focus.html'
        return render(request, 'core/home/index.html', person_focus_context)

    @action(detail=False, methods=["GET"], url_path="map-data")
    def map_data(self, request):
        """
        Retourne les structures avec marker au format GeoJSON,
        filtrées par la recherche en cours.
        Returns structures with markers as GeoJSON, filtered by current search.
        """
        pks_param = request.GET.get('pks', '')
        search_query = request.GET.get('q', '')

        structures_with_markers = Structure.objects.filter(
            marker__isnull=False
        ).select_related('marker')

        # Si des PKs sont fournis, filtrer par ces PKs uniquement
        # If PKs are provided, filter by those PKs only
        if pks_param:
            pk_list = [p.strip() for p in pks_param.split(',') if p.strip()]
            structures_with_markers = structures_with_markers.filter(pk__in=pk_list)
        elif len(search_query) >= 4:
            # Filtrer par la recherche si assez de caractères
            # Filter by search if enough characters
            structures_with_markers = structures_with_markers.filter(
                Q(name__icontains=search_query)
                | Q(description__icontains=search_query)
                | Q(issued_badges__name__icontains=search_query)
                | Q(issued_badges__description__icontains=search_query)
            ).distinct()

        # Pour chaque structure, inclure les badges qui matchent la recherche
        # For each structure, include badges that match the search
        features = []
        for structure in structures_with_markers:
            matching_badges = Badge.objects.filter(
                Q(issuing_structure=structure) | Q(endorsements__structure=structure)
            ).distinct()
            if len(search_query) >= 4:
                matching_badges = matching_badges.filter(
                    Q(name__icontains=search_query)
                    | Q(description__icontains=search_query)
                )

            features.append({
                'type': 'Feature',
                'geometry': {
                    'type': 'Point',
                    'coordinates': [structure.marker.lng, structure.marker.lat],
                },
                'properties': {
                    'pk': str(structure.pk),
                    'name': structure.name,
                    'badges': [
                        {'pk': str(b.pk), 'name': b.name}
                        for b in matching_badges[:10]
                    ],
                    'badge_count': matching_badges.count(),
                },
            })

        return JsonResponse({'type': 'FeatureCollection', 'features': features})

class BadgeViewSet(viewsets.ViewSet):
    """
    ViewSet for badge-related pages.
    """
    authentication_classes = [SessionAuthentication, ]

    def get_permissions(self):
        permissions_list = []

        if self.action in ['list','retrieve']:
            permissions_list += [AllowAny]
        elif self.action in ["create_badge"]:
            permissions_list += [IsAuthenticated]
        elif self.action in ["edit", "delete"]:
            permissions_list += [IsAuthenticated, IsBadgeEditor]
        elif self.action in ["assign"]:
            permissions_list += [IsAuthenticated, CanAssignBadge]
        elif self.action in ["endorse"]:
            permissions_list += [IsAuthenticated, CanEndorseBadge]

        return [permission() for permission in permissions_list]

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
            badges = badges.filter(issuing_structure__pk=structure_filter)

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

        is_editor = badge.issuing_structure.is_editor(request.user)
        is_admin = badge.issuing_structure.is_admin(request.user)
        if request.user.is_authenticated:
            can_endorse = request.user.can_endorse(badge)
            can_assign = request.user.can_assign(badge)
        else:
            can_endorse = False
            can_assign = False

        return render(request, 'core/badges/detail.html', {
            'title': f'FossBadge - Badge {badge.name}',
            'badge': badge,
            'holders': holders,
            'is_editor': is_editor,
            'is_admin': is_admin,
            "can_endorse":can_endorse,
            "can_assign":can_assign
        })

    @action(detail=True, methods=["get","post"])
    def edit(self, request, pk=None):
        """
        Edit an existing badge.
        """
        badge = get_object_or_404(Badge, pk=pk)
        if request.method == 'POST':
            form = BadgeForm(request.POST, request.FILES, instance=badge, request=request)
            if form.is_valid():
                form.save()
                return redirect(reverse('core:badge-detail', kwargs={'pk': badge.pk}))
        else:
            form = BadgeForm(instance=badge, request=request)

        icon = None
        if badge.icon:
            icon = badge.icon.url

        return render(request,"core/badges/edit.html",{"form":form,"icon":icon, "badge_pk":badge.pk})

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
            form = BadgeForm(request.POST, request.FILES, request=request)
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
            form = BadgeForm(initial={'issuing_structure':default_structure}, request=request)

        # Get all structures for the dropdown
        structures = Structure.objects.all()

        return render(request, 'core/badges/create.html', {
            'title': 'FossBadge - Forger un Badge',
            'structures': structures,
            'form': form
        })

    @action(detail=True, methods=["get", "post"])
    def endorse(self, request, pk=None):
        """
        Endorse a badge.
        """

        if not request.htmx:
            return raise403(request)

        badge = get_object_or_404(Badge, pk=pk)

        # Get only user structure that DO NOT endorse the badge
        valid_structures = badge.valid_structures
        user_structures = request.user.structures
        user_structure_not_endorsing = user_structures.difference(valid_structures)

        # If the user structures already endorse the badge, return an error template
        if user_structure_not_endorsing.count() == 0:
            return render(request, "errors/popup_errors.html",context={
                "error":'Toutes les structures dont vous faites parti ont déjà endosser ce badge'
            })

        if request.method == "GET":

            return render(request, 'core/badges/partials/badge_endorsement.html',context={
                "badge_pk": pk,
                "structures": user_structure_not_endorsing,
            })

        validator = BadgeEndorsementValidator(data=request.POST)

        if not validator.is_valid():
            return render(request, 'core/badges/partials/badge_endorsement.html',context={
                "errors": validator.errors,
                "defaults": validator.data,
                "badge_pk": validator.data['badge'],
                "structures": user_structure_not_endorsing,
            })

        # Get all objects
        structure = get_object_or_404(Structure, pk=validator.validated_data["structure"])
        endorsed_by = get_object_or_404(User, pk=validator.validated_data["endorsed_by"])

        notes = request.POST['notes']

        # Assign the badge to the user
        endorsement, created = badge.endorse(endorsed_by, structure, notes)

        if created:
            messages.add_message(request, messages.SUCCESS, 'Badge endorsé !')
        else:
            messages.add_message(request, messages.INFO, "Le badge était déjà endorsé")
        return reload(request)

    @action(detail=True, methods=['get','post'])
    def assign(self, request, pk=None):
        """
        Assign a badge to a user.
        """

        if not request.htmx:
            return raise403(request)

        badge = get_object_or_404(Badge, pk=pk)
        users = User.objects.all()
        structures = request.user.get_structures_endorsing_badge(badge)

        if request.method == "GET":
            return render(request, 'core/badges/partials/badge_assignment.html',context={
                "users": users,
                "badge_pk": pk,
                "structures": structures,
            })

        validator = BadgeAssignmentValidator(data=request.POST)

        is_valid = validator.is_valid()
        context = {
            "users": users,
            "errors": validator.errors,
            "defaults": validator.data,
            "badge_pk": pk,
            "structures": structures
        }

        if not is_valid :
            return render(request, 'core/badges/partials/badge_assignment.html',context=context)

        # Get all objects
        assigned_user = get_object_or_404(User, pk=validator.validated_data["assigned_user"])
        assigned_by_structure = get_object_or_404(Structure, pk=validator.validated_data["assigned_by_structure"])
        assigned_by_user = get_object_or_404(User, pk=validator.validated_data["assigned_by_user"])

        notes = request.POST['notes']

        # Check if the assigned structure is in the badge's valid structures (structure that have endorsed the badge)
        # Because only structures that have endorsed a badge can assign it
        if not badge.valid_structures.contains(assigned_by_structure):
            messages.add_message(request, messages.ERROR, "Veuillez sélectionner une structure valide")
            return render(request, 'core/badges/partials/badge_assignment.html',context=context)

        # Assign the badge to the user
        assignment, created = badge.add_holder(assigned_user,assigned_by_user,assigned_by_structure,notes)

        #
        if not created :
            messages.add_message(request, messages.INFO, "L'utilisateur possède déjà ce badge assigné par cette structure")
            return render(request, 'core/badges/partials/badge_assignment.html',context=context)

        messages.add_message(request, messages.SUCCESS, 'Badge assigné !')
        return reload(request)



class AssignmentViewSet(viewsets.ViewSet):
    """
    ViewSet for BadgeAssignments related pages
    """

    def get_permissions(self):
        permissions_list = []

        if self.action in ['list_user_badge_assignment','retrieve']:
            permissions_list += [AllowAny]

        return [permission() for permission in permissions_list]

    def retrieve(self, request, pk=None):
        """
        Display a specific assignment.
        """
        assignment = get_object_or_404(BadgeAssignment, pk=pk)

        return render(request, 'core/assignments/detail.html', {
            'title': f'FossBadge - {assignment.user.username} - {assignment.badge.name}',
            'assignment': assignment,
        })


    @action(detail=False, methods=['get', 'post'], url_path='user-badge-assignments', url_name='user-badge-assignments')
    def list_user_badge_assignment(self, request):

        badge = request.GET["badge"]
        badge = get_object_or_404(Badge, pk=badge)
        user = request.GET["user"]
        user = get_object_or_404(User, pk=user)
        assignments = user.get_badge_assignments(badge)

        return render(request, 'core/assignments/list_user_assignment.html', context={
            "assignments": assignments,
            "badge":badge,
            "user":user,
        })

class StructureViewSet(viewsets.ViewSet):
    """
    ViewSet for structure/company-related pages.
    """

    def get_permissions(self):
        permissions_list = []

        if self.action in ['list', 'retrieve']:
            permissions_list += [AllowAny]
        elif self.action in ["create_association"]:
            permissions_list += [IsAuthenticated]
        elif self.action in ["edit", "delete","invite"]:
            permissions_list += [IsStructureAdmin]

        return [permission() for permission in permissions_list]

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
                Q(issued_badges__pk=badge_filter) |
                Q(valid_badges__pk=badge_filter)
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
        is_editor = structure.is_editor(request.user)
        is_admin = structure.is_admin(request.user)

        return render(request, 'core/structures/detail.html', {
            'title': f'FossBadge - Structure {structure.name}',
            'structure': structure,
            'issued_badges': issued_badges,
            'is_editor': is_editor,
            'is_admin': is_admin,
            "roles" : Structure.ROLES
        })

    @action(detail=True, methods=["get","post"])
    def edit(self, request, pk=None):
        """
        Edit an existing structure.
        """
        structure = get_object_or_404(Structure, pk=pk)
        if not structure.is_admin(request.user):
            return raise403(request)

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
        if not structure.is_admin(request.user):
            return raise403(request)


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
                structure.admins.add(request.user)
                structure.save()

                return redirect(reverse('core:structure-detail', kwargs={'pk': structure.pk}))
        else:
            form = StructureForm()

        return render(request, 'core/structures/create.html', {
            'title': 'FossBadge - Créer une Structure / Entreprise',
            'form': form
        })

    @action(detail=True, methods=['post'])
    def invite(self, request, pk):
        """
        Invite a user to a structure.
        """
        structure = get_object_or_404(Structure, pk=pk)

        email = request.POST['email']
        role = request.POST['role']

        res = HttpResponse(headers={"HX-Redirect": reverse('core:structure-detail', kwargs={'pk': structure.pk}),})

        if not any(role in item for item in Structure.ROLES):
            messages.add_message(request,messages.ERROR,"Le role fourni est invalide")
            return res

        try:
            validate_email(email)
        except ValidationError:
            messages.add_message(request,messages.ERROR,"Le mail est invalide")
            return res

        invite_user_to_structure(email, role, structure)

        messages.add_message(request, messages.SUCCESS, 'Invitation envoyé !')
        return res

class UserViewSet(viewsets.ViewSet):
    """
    ViewSet for user-related pages.
    """
    def get_permissions(self):
        permissions_list = []

        if self.action in ['list', 'retrieve', 'cv', 'login_request', 'login_from_email']:
            permissions_list += [AllowAny]
        elif self.action in ['logout']:
            permissions_list += [IsAuthenticated]
        elif self.action in ["edit", "delete"]:
            permissions_list += [CanEditUser]

        return [permission() for permission in permissions_list]

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

        structures = user.structures

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
            users = users.filter(badge_assignments__badge__pk=badge_filter).distinct()

        # Apply structure filter if provided
        if structure_filter:
            users = users.filter(
                Q(structures_admins__pk=structure_filter) |
                Q(structures_editors__pk=structure_filter) |
                Q(structures_users__pk=structure_filter)
            ).distinct()

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
        badge_with_badge_assignments = user.get_all_badge_assignments_by_badge()

        structures = user.structures

        return render(request, 'core/users/detail.html', {
            'title': f'FossBadge - Profil de {user.get_full_name() or user.username}',
            'user': user,
            'badge_with_badge_assignments': badge_with_badge_assignments,
            'structures': structures
        })

    @action(detail=False, methods=['get', 'post'])
    def create_user(self, request):
        """
        Create a new user.
        """
        return raise403(request)
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
            user = get_or_create_user(email,send_mail=True)
            if settings.DEBUG:
                login(request, user)



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
            if user_pk is None:
                raise Exception()

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