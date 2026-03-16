from django.conf import settings
from django.contrib import messages
from django.contrib.auth import logout, get_user_model, authenticate, login
from django.core.exceptions import ValidationError, PermissionDenied
from django.core.signing import SignatureExpired
from django.core.validators import validate_email
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q, Count, Exists, OuterRef
from django.urls import reverse
from django_htmx.http import HttpResponseClientRedirect
from rest_framework import viewsets
from rest_framework.authentication import SessionAuthentication
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.decorators import action,authentication_classes, permission_classes
from .helpers import TokenHelper
from .helpers.utils import get_or_create_user, invite_user_to_structure
from .models import Structure, Badge, User, BadgeAssignment, BadgeEndorsement, BadgeHistory, BadgeCriteria, Course, CourseItem
from .forms import BadgeForm, UserForm, PartialUserForm

from .permissions import IsBadgeEditor, IsStructureAdmin, CanEditUser, CanAssignBadge, CanEndorseBadge, CanEditCourse
from .validators import BadgeAssignmentValidator, BadgeEndorsementValidator, DreamBadgeValidator, InviteUserValidator, \
    CreateCourseValidator, BadgeSelfAssignmentValidator, CreateStructureValidator


def raise403(request, msg=None):
    """
    Return a not authorize error (403).
    To use in another method :
        return raise403(request)
    """
    return render(request, '403.html', status=403, context={
        "message": msg
    })

def raise404(request, msg=None):
    """
    Return a not found error (404).
    To use in another method :
        return raise404(request)
    """
    return render(request, '404.html', status=404, context={
        "message": msg
    })

def reload(request):
    """
    Force reload fo HTMX
    To use in another method :
        return reload(request)
    """
    return HttpResponseClientRedirect(request.headers['Referer'])

def redirect_reload(url):
    """
    Forced redirection for HTMX
    To use in another method :
        return redirect_reload(reverse('url'))
    """
    return HttpResponseClientRedirect(url)



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
        # Page d'accueil — champ de recherche centré + nuage de mots des badges
        # Home page — centered search field + badge word cloud

        # Tous les noms de badges pour le nuage de mots
        # / All badge names for the word cloud
        all_badge_names_for_cloud = list(
            Badge.objects.values_list('name', flat=True).order_by('?')
        )

        return render(request, 'core/home/index.html', {
            'title': 'openbadge.coop',
            'badge_names_for_cloud': all_badge_names_for_cloud,
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

        # Si la requête est vide, retourner un partiel vide.
        # La limite de 4 caractères est gérée côté client (saisie auto uniquement).
        # Entrée et bouton loupe peuvent envoyer des requêtes plus courtes.
        # / If query is empty, return empty partial.
        # The 4-char limit is enforced client-side (auto-search only).
        query_is_empty = len(search_query) < 1
        if query_is_empty:
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
        search_context['title'] = 'openbadge.coop — Recherche'
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

        # Si badge + structure sélectionnés, chercher les critères d'attribution
        # If badge + structure selected, look for attribution criteria
        badge_criteria_for_story = None
        if selected_badge and selected_structure:
            badge_criteria_for_story = BadgeCriteria.objects.filter(
                badge=selected_badge, structure=selected_structure
            ).first()

        # Si badge + structure sélectionnés, chercher l'endorsement entre les deux
        # If badge + structure selected, look for endorsement between them
        endorsement_info = None
        if selected_badge and selected_structure:
            try:
                endorsement_info = BadgeEndorsement.objects.get(
                    badge=selected_badge,
                    structure=selected_structure,
                )
            except BadgeEndorsement.DoesNotExist:
                endorsement_info = None

        # Si badge + structure + personne, chercher aussi l'assignment
        # If badge + structure + person, also look for the assignment
        endorsement_assignment = None
        if selected_badge and selected_structure and selected_person:
            try:
                endorsement_assignment = BadgeAssignment.objects.select_related(
                    'assigned_by'
                ).get(
                    badge=selected_badge,
                    assigned_structure=selected_structure,
                    user=selected_person,
                )
            except BadgeAssignment.DoesNotExist:
                endorsement_assignment = None

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
            'endorsement_info': endorsement_info,
            'endorsement_assignment': endorsement_assignment,
            'badge_criteria_for_story': badge_criteria_for_story,
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
                    'coordinates': [structure.marker.longitude, structure.marker.latitude],
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

    @action(detail=False, methods=["GET"], url_path="structure/(?P<structure_pk>[^/.]+)")
    def lieu(self, request, structure_pk=None):
        """
        Page dédiée d'un lieu (structure).
        Affiche toutes les informations d'une structure sur une seule page :
        en-tête, badges émis et endossés, membres, référent.
        Ce n'est plus de la recherche, c'est de l'exploration.
        / Dedicated structure page — shows all info on a single scrollable page.

        LOCALISATION : core/views.py → HomeViewSet.lieu()

        FLUX :
        1. Reçoit GET depuis un lien /lieu/<uuid>/ (home, focus, ou URL directe)
        2. Charge la structure avec son marker (select_related)
        3. Récupère les badges émis et endossés (sans doublons)
        4. Récupère les membres avec leur rôle annoté (admin/éditeur) et leur nombre de badges
        5. Calcule les permissions (is_admin, is_editor) pour les boutons conditionnels
        6. Rend la page complète core/structure/index.html
        """
        structure = get_object_or_404(
            Structure.objects.select_related('marker'), uuid=structure_pk
        )

        # Badges émis par cette structure
        # Badges issued by this structure
        issued_badges = Badge.objects.filter(
            issuing_structure=structure
        ).select_related('issuing_structure')

        # Badges endossés par cette structure (on exclut ceux déjà émis pour éviter les doublons)
        # Badges endorsed by this structure (exclude already issued to avoid duplicates)
        endorsed_badges = Badge.objects.filter(
            endorsements__structure=structure
        ).exclude(
            issuing_structure=structure
        ).select_related('issuing_structure')

        # Nombre total de badges liés (pour l'affichage)
        # Total badge count (for display)
        badges_total_count = issued_badges.count() + endorsed_badges.count()

        # Membres avec annotation du rôle et du nombre de badges
        # Members with role annotation and badge count
        members_list = User.objects.filter(
            Q(structures_admins=structure)
            | Q(structures_editors=structure)
            | Q(structures_users=structure)
        ).annotate(
            is_structure_admin=Exists(
                structure.admins.filter(pk=OuterRef('pk'))
            ),
            is_structure_editor=Exists(
                structure.editors.filter(pk=OuterRef('pk'))
            ),
            badge_count_for_member=Count('badge_assignments', distinct=True),
        ).distinct()

        # Permissions
        is_admin = structure.is_admin(request.user) if request.user.is_authenticated else False
        is_editor = structure.is_editor(request.user) if request.user.is_authenticated else False

        # Annoter chaque badge avec les permissions d'action pour l'utilisateur courant.
        # On convertit en liste pour pouvoir ajouter des attributs dynamiques.
        # / Annotate each badge with action permissions for the current user.
        user_can_manage_badges = is_admin or is_editor

        # Charger tous les critères de cette structure en un seul appel
        # Load all criteria for this structure in a single query
        all_criteria_for_structure = {
            c.badge_id: c
            for c in BadgeCriteria.objects.filter(structure=structure)
        }

        issued_badges_list = list(issued_badges)
        for badge_item in issued_badges_list:
            badge_item.can_assign = user_can_manage_badges
            badge_item.can_endorse = False  # Badge émis par cette structure / Issued by this structure
            badge_item.criteria_for_lieu = all_criteria_for_structure.get(badge_item.pk)

        endorsed_badges_list = list(endorsed_badges)
        for badge_item in endorsed_badges_list:
            badge_item.can_assign = user_can_manage_badges
            badge_item.can_endorse = False  # Déjà endossé par cette structure / Already endorsed
            badge_item.criteria_for_lieu = all_criteria_for_structure.get(badge_item.pk)

        return render(request, 'core/structure/index.html', {
            'structure': structure,
            'issued_badges': issued_badges_list,
            'endorsed_badges': endorsed_badges_list,
            'badges_total_count': badges_total_count,
            'members_list': members_list,
            'is_admin': is_admin,
            'is_editor': is_editor,
        })

    @action(detail=False, methods=["GET"], url_path="passeport/(?P<person_pk>[^/.]+)")
    def passeport(self, request, person_pk=None):
        """
        Page dédiée du passeport (profil open badge) d'une personne.
        Affiche le parcours complet en timeline chronologique :
        chaque badge est une carte individuelle, triée du plus récent au plus ancien.
        La page est autonome, partageable, et sert de "carnet de route".
        / Dedicated passport page — shows a person's full badge journey as a chronological timeline.

        LOCALISATION : core/views.py → HomeViewSet.passeport()

        FLUX :
        1. Reçoit GET depuis un lien /passeport/<uuid>/ (home, focus, lieu, ou URL directe)
        2. Charge la personne par UUID
        3. Récupère tous les assignments triés du plus récent au plus ancien
        4. Collecte les structures uniques avec marker (pour la carte du parcours)
        5. Calcule les compteurs (badges, lieux)
        6. Rend la page complète core/user/passeport.html
        """
        person = get_object_or_404(User, uuid=person_pk)

        # Tous les assignments, triés du plus récent au plus ancien (timeline)
        # All assignments, sorted most recent first (timeline)
        all_assignments_for_person = BadgeAssignment.objects.filter(
            user=person
        ).select_related(
            'badge', 'badge__issuing_structure',
            'assigned_by', 'assigned_structure', 'assigned_structure__marker',
        ).order_by('-assigned_date')

        # Collecter les structures uniques qui ont un marker (pour la carte)
        # Collect unique structures that have a marker (for the map)
        structures_with_marker = set()
        for assignment in all_assignments_for_person:
            structure = assignment.assigned_structure
            if structure and structure.marker_id:
                structures_with_marker.add(structure.pk)

        structures_pks_csv = ','.join(str(pk) for pk in structures_with_marker)

        # Nombre de lieux distincts (structures ayant attribué au moins un badge)
        # Number of distinct places (structures that assigned at least one badge)
        total_places = len(set(
            a.assigned_structure_id for a in all_assignments_for_person
            if a.assigned_structure_id
        ))

        # Charger les critères pour chaque assignment (badge + structure d'attribution)
        # Load criteria for each assignment (badge + assigning structure)
        criteria_lookup_keys = set()
        for assignment in all_assignments_for_person:
            if assignment.assigned_structure_id:
                criteria_lookup_keys.add((assignment.badge_id, assignment.assigned_structure_id))

        all_criteria_for_passeport = {}
        if criteria_lookup_keys:
            all_criteria_qs = BadgeCriteria.objects.filter(
                Q(*[Q(badge_id=b, structure_id=s) for b, s in criteria_lookup_keys])
            )
            for c in all_criteria_qs:
                all_criteria_for_passeport[(c.badge_id, c.structure_id)] = c

        for assignment in all_assignments_for_person:
            assignment.criteria_for_passeport = all_criteria_for_passeport.get(
                (assignment.badge_id, assignment.assigned_structure_id)
            )

        # Est-ce que l'utilisateur regarde son propre passeport ?
        # Is the user viewing their own passport?
        is_self = request.user.is_authenticated and request.user.pk == person.pk

        return render(request, 'core/user/passeport.html', {
            'person': person,
            'assignments': all_assignments_for_person,
            'total_badges': all_assignments_for_person.count(),
            'total_places': total_places,
            'structures_pks_csv': structures_pks_csv,
            'is_self': is_self,
        })

    @action(detail=False, methods=["GET"], url_path="badge/(?P<badge_pk>[^/.]+)")
    def badge_detail(self, request, badge_pk=None):
        """
        Page dédiée d'un badge.
        Affiche toutes les informations d'un badge sur une seule page :
        en-tête, structures qui le reconnaissent, détenteurs, actions, carte.
        C'est la version complète du badge_focus (home).
        / Dedicated badge page — shows all badge info on a single scrollable page.

        LOCALISATION : core/views.py → HomeViewSet.badge_detail()

        FLUX :
        1. Reçoit GET depuis un lien /badge/<uuid>/ (home, focus, lieu, ou URL directe)
        2. Charge le badge avec sa structure émettrice et son marker (select_related)
        3. Récupère les structures qui endossent ce badge
        4. Récupère les détenteurs avec leur structure d'attribution
        5. Calcule les permissions (is_badge_editor, can_assign, can_endorse)
        6. Rend la page complète core/badge_page/index.html
        """
        badge = get_object_or_404(
            Badge.objects.select_related('issuing_structure', 'issuing_structure__marker'),
            uuid=badge_pk
        )

        # Structures qui endossent ce badge (sans la structure émettrice)
        # Structures that endorse this badge (excluding issuer)
        endorsing_structures = Structure.objects.filter(
            endorsements__badge=badge
        ).select_related('marker')

        # Check if the badge has an issuing structure, if so change the logic behind it
        if badge.issuing_structure:
            endorsing_structures = endorsing_structures.exclude(
                pk=badge.issuing_structure.pk
            )

            # Toutes les structures (émettrice + endosseuses) pour la carte et la liste
            # All structures (issuer + endorsers) for the map and the list
            all_structures_list = [badge.issuing_structure] + list(endorsing_structures)
        else:
            all_structures_list = list(endorsing_structures)



        # Détenteurs avec leur structure d'attribution, triés du plus récent au plus ancien
        # Holders with their assigning structure, sorted most recent first
        holders_assignments = BadgeAssignment.objects.filter(
            badge=badge
        ).select_related('user', 'assigned_structure').order_by('-assigned_date')

        # Critères d'attribution par structure pour ce badge
        # On les indexe par PK de structure pour les attacher a chaque structure
        # / Attribution criteria by structure for this badge
        # Indexed by structure PK to attach to each structure
        all_criteria_for_badge = BadgeCriteria.objects.filter(
            badge=badge
        ).select_related('structure')

        criteria_by_structure_pk = {}
        for criteria in all_criteria_for_badge:
            criteria_by_structure_pk[criteria.structure_id] = criteria

        # Attache le critère a chaque structure de la liste
        # / Attach criteria to each structure in the list
        for structure_item in all_structures_list:
            structure_item.criteria_for_badge = criteria_by_structure_pk.get(structure_item.pk)

        # Permissions
        # / Permissions
        is_badge_editor = False
        can_assign = False
        can_endorse = False
        if request.user.is_authenticated:
            # L'utilisateur peut éditer s'il est admin ou éditeur de la structure émettrice
            # User can edit if admin/editor of the issuing structure
            if badge.issuing_structure :
                is_badge_editor = (
                        badge.issuing_structure.is_admin(request.user)
                        or badge.issuing_structure.is_editor(request.user)
                )
            else :
                is_badge_editor = (
                    badge.user == request.user
                )

            # L'utilisateur peut assigner s'il est admin/éditeur d'une structure liée (émettrice ou endosseuse)
            # User can assign if admin/editor of a related structure (issuer or endorser)
            can_assign = Structure.objects.filter(
                Q(endorsements__badge=badge) | Q(issued_badges=badge),
                Q(admins=request.user) | Q(editors=request.user),
            ).exists()

            # L'utilisateur peut endosser s'il a au moins une structure
            # User can endorse if they have at least one structure
            can_endorse = Structure.objects.filter(
                Q(admins=request.user) | Q(editors=request.user)
            ).exists()

        # PKs des structures avec marker (pour la carte MapLibre)
        # PKs of structures with a marker (for the MapLibre map)
        structures_pks_csv = ','.join(
            str(s.pk) for s in all_structures_list if s.marker_id
        )

        return render(request, 'core/badge/index.html', {
            'badge': badge,
            'all_structures_list': all_structures_list,
            'endorsing_structures': endorsing_structures,
            'holders_assignments': holders_assignments,
            'is_badge_editor': is_badge_editor,
            'can_assign': can_assign,
            'can_endorse': can_endorse,
            'can_self_assign': badge.can_self_assign(request.user),
            'structures_pks_csv': structures_pks_csv,
            'all_criteria_for_badge': all_criteria_for_badge,
        })

    @action(detail=False,methods=["get"],url_path="parcours/(?P<course_pk>[^/.]+)",url_name="parcours-detail")
    def parcours_detail(self, request, course_pk=None):
        """
        Affiche la page d'un parcours avec le graph Cytoscape.
        / Displays a course/journey page with the Cytoscape graph.
        LOCALISATION : core/views.py → HomeViewSet.parcours_detail()
        FLUX :
        1. Reçoit GET depuis un lien /parcours/<uuid>/
        2. Charge le parcours (Course) par UUID
        3. Vérifie les permissions d'édition
        4. Rend la page templates/course/detail.html
        """

        course = get_object_or_404(Course, pk=course_pk)
        # Vérifier si l'utilisateur peut éditer ce parcours
        # / Check if user can edit this course
        can_edit = False
        if request.user.is_authenticated:
            can_edit = course.user == request.user

        return render(
            request, "core/course/detail.html", {"course": course, "can_edit": can_edit}
        )


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
        badges = Badge.get_all_badges_except_dream()

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
                'title': 'openbadge.coop - Liste des Badges',
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
            'title': f'openbadge.coop - Badge {badge.name}',
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
        Modifie un badge existant.
        Si requete HTMX, retourne le formulaire en partiel pour la modale.
        / Edit an existing badge. Returns partial for HTMX modal.

        LOCALISATION : core/views.py
        """
        badge = get_object_or_404(Badge, pk=pk)
        if request.method == 'POST':
            form = BadgeForm(request.POST, request.FILES, instance=badge, request=request)
            if form.is_valid():
                form.save()
                if request.htmx:
                    return HttpResponseClientRedirect(
                        reverse('core:home-badge-detail', kwargs={'badge_pk': badge.pk})
                    )
                return redirect(reverse('core:home-badge-detail', kwargs={'badge_pk': badge.pk}))
        else:
            form = BadgeForm(instance=badge, request=request)

        icon = None
        if badge.icon:
            icon = badge.icon.url

        # Partiel HTMX pour la modale / HTMX partial for modal
        if request.htmx:
            return render(request, "core/badge/partial/badge_edit_form.html", {
                "form": form, "icon": icon, "badge_pk": badge.pk,
            })

        return render(request,"core/badges/edit.html",{"form":form,"icon":icon, "badge_pk":badge.pk})

    @action(detail=True, methods=["get", "post"])
    def delete(self, request, pk=None):
        """
        Supprime un badge existant. Seul un admin de la structure emettrice peut supprimer.
        / Delete an existing badge. Only admin of the issuing structure can delete.
        """
        badge = get_object_or_404(Badge, pk=pk)

        # Seul un admin de la structure emettrice peut supprimer un badge
        # / Only admin of the issuing structure can delete a badge
        if badge.issuing_structure and not badge.issuing_structure.is_admin(request.user):
            return raise403(request)

        if badge.user and not badge.user == request.user:
            return raise403(request)

        if request.method == 'POST':
            badge.delete()
            return redirect(reverse('core:badge-list'))

        badge_holders = badge.get_holders()
        return render(request, 'core/badges/delete.html', {"badge": badge, "holders": badge_holders})

    @action(detail=False, methods=['get', 'post'])
    def create_badge(self, request):
        """
        Cree un nouveau badge.
        Si requete HTMX, retourne le formulaire en partiel pour la modale.
        / Create a new badge. Returns partial for HTMX modal.

        LOCALISATION : core/views.py
        """

        # Pre-remplir le formulaire depuis les query params (recherche ou page lieu)
        # / Pre-fill form from query params (search or structure page)
        default_structure = request.GET.get('structure', '')
        default_name = request.GET.get('name', '')

        if request.method == 'POST':
            form = BadgeForm(request.POST, request.FILES, request=request)
            if form.is_valid():
                badge = form.save()
                # Cree une entree historique pour la creation du badge
                # / Create a history entry for badge creation
                BadgeHistory.objects.create(
                    badge=badge,
                    action="creation",
                    details="Badge crée"
                )
                # Redirige vers la page badge (HTMX ou classique)
                # / Redirect to badge page (HTMX or classic)
                messages.success(request,"Badge ajouté avec succès ! ")
                if request.htmx:
                    return HttpResponseClientRedirect(
                        reverse('core:home-badge-detail', kwargs={'badge_pk': badge.pk})
                    )
                return redirect(reverse('core:home-badge-detail', kwargs={'badge_pk': badge.pk}))
        else:
            initial_data = {}
            if default_structure:
                initial_data['issuing_structure'] = default_structure
            if default_name:
                initial_data['name'] = default_name
            form = BadgeForm(initial=initial_data, request=request)

        # Toutes les structures pour le dropdown / All structures for dropdown
        structures = Structure.objects.all()

        # Partiel HTMX pour la modale / HTMX partial for modal
        if request.htmx:
            return render(request, 'core/badge/partial/badge_create_form.html', {
                'form': form,
            })

        return render(request, 'core/badges/create.html', {
            'title': 'openbadge.coop - Forger un Badge',
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

        # Structures ou l'user est admin, qui n'endossent PAS encore ce badge
        # / Structures where user is admin, that do NOT already endorse this badge
        valid_structures = badge.valid_structures
        user_admin_structures = Structure.objects.filter(admins=request.user)
        user_admin_not_endorsing = user_admin_structures.difference(valid_structures)

        # Si toutes les structures admin endossent deja, erreur
        # / If all admin structures already endorse, error
        if user_admin_not_endorsing.count() == 0:
            return render(request, "errors/popup_errors.html", context={
                "error": 'Toutes vos structures ont déjà endossé ce badge'
            })

        if request.method == "GET":
            # Pre-remplissage optionnel de la structure (utilise par la page lieu)
            # / Optional structure pre-fill (used by the lieu page)
            defaults = {}
            default_structure_pk = request.GET.get('default_structure', '')
            if default_structure_pk:
                defaults['structure'] = default_structure_pk

            # Si une seule structure, la pre-selectionner
            # / If only one structure, pre-select it
            if user_admin_not_endorsing.count() == 1 and 'structure' not in defaults:
                defaults['structure'] = str(user_admin_not_endorsing.first().pk)

            return render(request, 'core/badge/partial/badge_endorsement.html', context={
                "badge_pk": pk,
                "structures": user_admin_not_endorsing,
                "defaults": defaults,
            })

        validator = BadgeEndorsementValidator(data=request.POST)

        if not validator.is_valid():
            return render(request, 'core/badge/partial/badge_endorsement.html',context={
                "errors": validator.errors,
                "defaults": validator.data,
                "badge_pk": validator.data['badge'],
                "structures": user_admin_not_endorsing,
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

        # Structures ou l'utilisateur est admin ET qui reconnaissent ce badge
        # / Structures where user is admin AND that recognize this badge
        user_admin_structures = Structure.objects.filter(admins=request.user)
        structures_endorsing_badge = request.user.get_structures_endorsing_badge(badge)
        structures = structures_endorsing_badge.filter(pk__in=user_admin_structures)

        if request.method == "GET":
            # Pre-remplissage optionnel de la structure (utilise par la page lieu)
            # / Optional structure pre-fill (used by the lieu page)
            defaults = {}
            default_structure_pk = request.GET.get('default_structure', '')
            if default_structure_pk:
                defaults['assigned_by_structure'] = default_structure_pk

            # Si une seule structure, la pre-sélectionner
            # / If only one structure, pre-select it
            if structures.count() == 1 and 'assigned_by_structure' not in defaults:
                defaults['assigned_by_structure'] = str(structures.first().pk)

            return render(request, 'core/badge/partial/badge_assignment.html', context={
                "badge_pk": pk,
                "structures": structures,
                "defaults": defaults,
            })

        validator = BadgeAssignmentValidator(data=request.POST)

        is_valid = validator.is_valid()
        context = {
            "errors": validator.errors,
            "defaults": validator.data,
            "badge_pk": pk,
            "structures": structures,
        }

        if not is_valid:
            return render(request, 'core/badge/partial/badge_assignment.html', context=context)

        # Récupère ou crée l'utilisateur a partir de l'email
        # / Get or create user from email
        assigned_email = validator.validated_data["assigned_email"]
        assigned_user = get_or_create_user(assigned_email)

        assigned_by_structure = get_object_or_404(Structure, pk=validator.validated_data["assigned_by_structure"])
        assigned_by_user = get_object_or_404(User, pk=validator.validated_data["assigned_by_user"])

        notes = request.POST['notes']

        # Vérifie que la structure est dans les structures qui reconnaissent le badge
        # / Check that the structure recognizes this badge
        if not badge.valid_structures.contains(assigned_by_structure):
            messages.add_message(request, messages.ERROR, "Veuillez sélectionner une structure valide")
            return render(request, 'core/badge/partial/badge_assignment.html', context=context)

        # Assigne le badge a l'utilisateur
        # / Assign the badge to the user
        assignment, created = badge.add_holder(assigned_user, assigned_by_user, assigned_by_structure, notes)

        if not created:
            messages.add_message(request, messages.INFO, "L'utilisateur possède déjà ce badge assigné par cette structure")
            return render(request, 'core/badge/partial/badge_assignment.html', context=context)

        messages.add_message(request, messages.SUCCESS, 'Badge assigné !')
        return reload(request)

    @action(detail=True, methods=['get','post'])
    def self_assign(self, request, pk=None):
        """
        Self assign a badge.
        """

        if not request.htmx:
            return raise403(request)

        badge = get_object_or_404(Badge, pk=pk)

        if request.method == "GET":

            return render(request, 'core/badge/partial/badge_assignment.html', context={
                "badge_pk": pk,
                "self_assign":True
            })

        validator = BadgeSelfAssignmentValidator(data=request.POST)

        is_valid = validator.is_valid()
        context = {
            "errors": validator.errors,
            "defaults": validator.data,
            "badge_pk": pk,
            "self_assign":True
        }

        if not is_valid:
            return render(request, 'core/badge/partial/badge_assignment.html', context=context)

        notes = request.POST['notes']

        # Assigne le badge a l'utilisateur
        # / Assign the badge to the user
        assignment, created = badge.self_assign(request.user,notes)

        if not created:
            messages.add_message(request, messages.INFO, "Ce badge est déjà auto-assigné")
            return render(request, 'core/badge/partial/badge_assignment.html', context=context)

        messages.add_message(request, messages.SUCCESS, 'Badge auto-assigné !')
        return reload(request)


    @action(detail=False, methods=['get','post'], url_path="create-dream")
    def create_dream(self,request):
        """
        View for creating a dream badge. Only with HTMX
        """
        if not request.htmx:
            return raise403(request)

        if request.method == "GET":
            return render(request, 'core/badge/partial/dream_badge_create.html')

        validator = DreamBadgeValidator(data=request.data)
        is_valid = validator.is_valid()

        if not is_valid:
            return render(request, 'core/badge/partial/dream_badge_create.html',context={
                "defaults": validator.data,
                "errors" : validator.errors,
            })

        # Create default data for dream badge and add the validator's data to it
        data={
            "is_dream_badge":True,
            "user":request.user,
        }
        data.update(validator.validated_data)

        # Create the dream badge and its associated course
        badge = Badge.objects.create(**data)
        course = Course.objects.create(badge=badge, user=request.user,name=badge.name,is_dream=True)

        messages.success(request, "Votre badge de rêve a bien été créé")
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
            'title': f'openbadge.coop - {assignment.user.username} - {assignment.badge.name}',
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
                'title': 'openbadge.coop - Liste des Structures',
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
            'title': f'openbadge.coop - Structure {structure.name}',
            'structure': structure,
            'issued_badges': issued_badges,
            'is_editor': is_editor,
            'is_admin': is_admin,
        })

    @action(detail=True, methods=["get","post"])
    def edit(self, request, pk=None):
        """
        Update an existing structure.
        """
        if not request.htmx:
            return raise403(request)

        structure = get_object_or_404(Structure, pk=pk)

        if request.method == 'GET':
            return render(request, 'core/structure/partial/structure_edit_form.html', {
                'types':Structure.TYPE_CHOICES,
                "structure":structure,
            })

        validator = CreateStructureValidator(structure, data=request.data)
        is_valid = validator.is_valid()

        if not is_valid:
            return render(request, 'core/structure/partial/structure_edit_form.html', {
                'types':Structure.TYPE_CHOICES,
                "defaults": validator.data,
                "errors" : validator.errors,
                "structure":structure,
            })

        # Edit the structure
        structure = validator.save()

        return redirect_reload(reverse('core:home-lieu', kwargs={'structure_pk': structure.pk}))


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
        if not request.htmx:
            return raise403(request)

        if request.method == 'GET':
            return render(request, 'core/structure/partial/structure_create_form.html', {
                'types':Structure.TYPE_CHOICES,
            })


        validator = CreateStructureValidator(data=request.data)
        is_valid = validator.is_valid()

        if not is_valid:
            return render(request, 'core/structure/partial/structure_create_form.html', {
                'types':Structure.TYPE_CHOICES,
                "defaults": validator.data,
                "errors" : validator.errors,
            })

        # Create the structure
        structure = validator.save()
        structure.admins.add(request.user)


        return redirect_reload(reverse('core:home-lieu', kwargs={'structure_pk': structure.pk}))


    @action(detail=True, methods=['get','post'])
    def invite(self, request, pk):
        """
        Invite a user to a structure.
        """
        if not request.htmx:
            return raise403(request)

        context = {
            "roles" : Structure.ROLES,
            "structure_pk": pk,
        }

        if request.method == 'GET':
            return render(request,"core/structure/partial/structure_invite.html",context=context)

        structure = get_object_or_404(Structure, pk=pk)

        validator = InviteUserValidator(data=request.data)
        is_valid = validator.is_valid()

        if not is_valid:
            context.update({
                "errors" : validator.errors,
                "defaults" : validator.data,
            })
            return render(request,"core/structure/partial/structure_invite.html",context=context)

        email = validator.validated_data['email']
        role = validator.validated_data['role']

        invite_user_to_structure(email, role, structure)

        messages.add_message(request, messages.SUCCESS, 'Invitation envoyé !')
        return reload(request)

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
            permissions_list += [IsAuthenticated, CanEditUser]

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
                'title': 'openbadge.coop - Liste des Profils',
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
            'title': f'openbadge.coop - Profil de {user.get_full_name() or user.username}',
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
            'title': 'openbadge.coop - Créer un utilisateur',
            'form': form,
        })

    @action(detail=True, methods=['get', 'post'],name="edit-profile")
    def edit(self,request,pk=None):
        """
        Edit an existing user.
        """
        if not request.htmx:
            return redirect(reverse('core:user-detail', kwargs={'pk': pk}))


        user = get_object_or_404(User, pk=pk)

        if request.method == 'POST':
            form = PartialUserForm(request.POST, instance=user)
            if form.is_valid():
                form.save()
                user = User.objects.get(pk=pk)

                return redirect_reload(reverse("core:home-passeport",kwargs={"person_pk":pk}))

        form = PartialUserForm(instance=user)
        return render(request, 'core/user/partial/user_profile_edit.html', {'user': user, 'form': form})

    @action(detail=True, methods=['post'])
    def delete(self, request, pk=None):
        """
        Delete a user.
        """
        # TODO when authentication will be added :
        # Send a mail containing a link to delete the account

        if not request.htmx:
            return raise403(request)

        messages.success(request, "L'utilisateur a bien été désactivé")

        user = get_object_or_404(User, pk=pk)
        user.is_active = False
        user.save()

        return redirect_reload(reverse('core:user-list'))

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
            if settings.DEBUG == True:
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

            messages.success(request, f"Connexion réussi !")

            return redirect('core:home-list')
        except SignatureExpired:
            messages.error(request, f"Ce lien est expiré, veuillez refaire une demande de connexion")

            return redirect('core:home-list')
        except Exception:

            messages.error(request, f"Ce lien est invalide, veuillez refaire une demande de connexion")
            return redirect('core:home-list')

    @action(detail=False, methods=['get'])
    def logout(self, request):
        logout(request)
        messages.success(request, f"Déconnexion réussi")
        return redirect('core:home-list')

class CourseViewSet(viewsets.ViewSet):
    """
    ViewSet for course related routes
    """

    def get_permissions(self):
        permissions_list = []

        if self.action in ['retrieve', 'list']:
            permissions_list += [AllowAny]
        elif self.action in ['get_or_create_dream_course']:
            permissions_list += [IsAuthenticated]
        elif self.action in ["add_badge", "remove_badge", "edit"]:
            permissions_list += [CanEditCourse]

        return [permission() for permission in permissions_list]


    def retrieve(self, request, pk=None):

        course = Course.objects.get(pk=pk)
        can_edit = request.user.can_edit_course(course)

        return render(request, "core/courses/detail.html",context={
            "course":course,
            "editable":False,
            "can_edit":can_edit
        })

    def list(self,request):

        template = "core/courses/list.html"

        if request.htmx:
            template = "core/courses/partial/list.html"

        # Get search query
        search_query = request.GET.get('search', '')
        structure_filter = request.GET.get('structure', '')
        badge_filter = request.GET.get('badge', '')

        # Start with all courses
        # courses = Course.objects.all()
        courses = (Course.objects.annotate(num_items=Count("items")).filter(num_items__gt=0))


    # Apply search filter if provided
        if search_query:
            courses = courses.filter(
                Q(name__icontains=search_query) |
                Q(structure__name__icontains=search_query)
            )


        # Apply structure filter if provided
        if structure_filter:
            courses = courses.filter(structure__pk=structure_filter)

        # Apply badge filter if provided
        if badge_filter:
            courses = courses.filter(
                Q(items__badge__pk=badge_filter)
            )




        structures = Structure.objects.all()
        badges = Badge.objects.all()

        return render(request, template, context={
            "courses":courses,
            "structures":structures,
            "badges":badges,
        })

    @action(detail=False, methods=['get','post'])
    def create_course(self,request):
        """
        Create a new course
        """

        if not request.htmx:
            return raise403(request)

        context = {}

        if request.method == 'GET':
            structure = request.GET.get('structure', None)
            badge = request.GET.get('badge', None)

            if not structure and not badge:
                return raise404(request)

            if structure:
                structure = Structure.objects.get(pk=structure)
                badges = structure.endorsed_badges
                context.update({
                    "structure":structure,
                    "badges":badges,
                })

            if badge:
                badge = Badge.objects.get(pk=badge)
                structures = request.user.get_structures_endorsing_badge(badge)
                context.update({
                    "structures":structures,
                    "badge":badge,
                })

            return render(request, "core/courses/partial/create_popup.html", context=context)


        validator = CreateCourseValidator(data=request.data)
        is_valid = validator.is_valid()

        if not is_valid:
            context.update({
                "errors" : validator.errors,
                "defaults" : validator.data,
            })
            return render(request,"core/courses/partial/create_popup.html",context=context)

        structure = validator.validated_data['structure']
        structure = Structure.objects.get(pk=structure)

        badge = validator.validated_data['badge']
        badge = Badge.objects.get(pk=badge)

        course = Course.objects.create(badge=badge,structure=structure)

        return redirect_reload(reverse('core:course-edit',kwargs={"pk":course.pk}))

    @action(detail=True, methods=['get'])
    def edit(self,request, pk=None):
        course = Course.objects.get(pk=pk)
        similar_badges = Badge.objects.order_by('?')[:5]

        return render(request, "core/course/edit.html", context={
            "course":course,
            "editable":True,
            "similar_badges":similar_badges
        })

    @action(detail=True, methods=['get','post'])
    def add_badge(self, request, pk=None):
        if not request.htmx:
            return raise403(request)

        search_query = request.GET.get('name', '')
        parent_pk = request.GET.get('parent_pk', '')

        course = Course.objects.get(pk=pk)

        if request.method == "GET":
            badges = []
            if search_query:
                badges = Badge.objects.filter(name__icontains=search_query)
                for badge in [item.badge for item in course.items.all()]:
                    badges = badges.exclude(course_items__badge=badge)

            return render(request, "core/course/partial/add_badge_popup.html",context={
                "badges":badges,
                "parent_pk":parent_pk,
                "course":course
            })


        child_badge_id = request.POST.get('child_id', '')
        parent_badge_id = request.POST.get('parent_id', None)

        badge = Badge.objects.get(pk=child_badge_id)
        parent = None
        if parent_badge_id:
            parent = Badge.objects.get(pk=parent_badge_id)

        CourseItem.add_to_course(course, badge, parent)

        return HttpResponse()

    @action(detail=True, methods=['post'])
    def remove_badge(self, request, pk=None):
        """

        """

        if not request.htmx:
            return raise403(request)

        course = Course.objects.get(pk=pk)

        badge_pk = request.POST.get('pk', '')
        badge = Badge.objects.get(pk=badge_pk)

        course_item = CourseItem.objects.get(badge=badge, course=course)
        course_item.delete()

        return HttpResponse()

    @action(detail=True, methods=['post'])
    def add_connection(self, request, pk=None):
        if not request.htmx:
            return raise403(request)

        course = Course.objects.get(pk=pk)

        parent_pk = request.POST.get('parent', '')
        badge_parent = Badge.objects.get(pk=parent_pk)

        child_pk = request.POST.get('child', '')
        badge_child = Badge.objects.get(pk=child_pk)

        course_parent = CourseItem.objects.get(badge=badge_parent, course=course)

        course_child = CourseItem.objects.get(badge=badge_child, course=course)

        course_parent.children.add(course_child)

        return HttpResponse()



