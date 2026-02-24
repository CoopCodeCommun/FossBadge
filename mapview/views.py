from django.shortcuts import render
from django.http import JsonResponse
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.authentication import SessionAuthentication
from rest_framework.permissions import AllowAny

from django.db.models import Count
from mapview.models import Marker, MapViewConfig
from core.models import Structure, Badge

# Icône par défaut pour les structures sans logo (marqueur SVG orange encodé en data URI)
# Default icon for structures without a logo (orange SVG marker encoded as data URI)
DEFAULT_STRUCTURE_ICON = (
    "data:image/svg+xml;charset=utf-8,"
    "%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 36' width='48' height='72'%3E"
    "%3Cpath d='M12 0C5.4 0 0 5.4 0 12c0 9 12 24 12 24s12-15 12-24C24 5.4 18.6 0 12 0z' "
    "fill='%23E65100'/%3E"
    "%3Ccircle cx='12' cy='12' r='5' fill='white'/%3E"
    "%3C/svg%3E"
)


class IndexViewSet(viewsets.ViewSet):
    permission_classes = [AllowAny]
    authentication_classes = [SessionAuthentication,]

    def list(self, request):
        """
        Rendu de la page principale de la carte.
        Render the main map page.
        """
        # Annoter chaque structure avec le nombre de personnes badgées
        # Annotate each structure with the number of badged people
        structures = Structure.objects.filter(
            marker__isnull=False
        ).select_related('marker').annotate(
            holders_count=Count('issued_badges__assignments')
        )

        context = {
            "markers" : Marker.objects.all(),
            "m_config" : MapViewConfig.get_solo(),
            "structures" : structures,
        }
        return render(request, 'mapview/index.html', context)

    @action(detail=False, methods=['get'])
    def config(self, request):
        """
        Retourne le panneau de configuration (HTMX).
        Return the configuration panel (HTMX).
        """
        context = {
            "m_config" : MapViewConfig.get_solo(),
        }
        return render(request, 'mapview/partials/config_panel.html', context)

    @action(detail=False, methods=['get'])
    def structures(self, request):
        """
        Retourne la liste des structures (HTMX).
        Accepte un paramètre ?bounds=west,south,east,north pour filtrer par viewport.
        Return the list of structures (HTMX).
        Accepts a ?bounds=west,south,east,north parameter to filter by viewport.
        """
        structures = Structure.objects.filter(
            marker__isnull=False
        ).select_related('marker').annotate(
            holders_count=Count('issued_badges__assignments')
        )

        # Filtrage par limites géographiques du viewport
        # Filter by geographic bounds of the viewport
        bounds = request.GET.get('bounds', '')
        if bounds:
            try:
                west, south, east, north = [float(x) for x in bounds.split(',')]
                structures = structures.filter(
                    marker__lng__gte=west,
                    marker__lng__lte=east,
                    marker__lat__gte=south,
                    marker__lat__lte=north,
                )
            except (ValueError, TypeError):
                pass

        context = {
            "structures" : structures,
        }
        return render(request, 'mapview/partials/structure_list.html', context)

    @action(detail=False, methods=['get'])
    def data_json(self, request):
        """
        Retourne les données des badges et des structures pour Deck.gl.
        Returns badge and structure data for Deck.gl.
        """
        import math
        from collections import defaultdict
        from core.models import BadgeAssignment

        # On récupère toutes les attributions de badges (jetons/tokens)
        # pour les structures qui ont un emplacement physique (marqueur).
        # We fetch all badge assignments (tokens) for structures
        # that have a physical location (marker).
        attributions = BadgeAssignment.objects.filter(
            badge__issuing_structure__marker__isnull=False
        ).select_related(
            'badge',
            'badge__issuing_structure',
            'badge__issuing_structure__marker'
        )

        # Mapping des niveaux vers des hauteurs réelles en mètres (1, 2, 3).
        # Mapping levels to real heights in meters (1, 2, 3).
        hauteurs_metres = {
            'beginner': 1.0,
            'intermediate': 2.0,
            'expert': 3.0
        }

        badges_donnees = []

        # Étape 1 : Regrouper les attributions par structure,
        # puis compter les détenteurs par badge unique.
        # Step 1: Group assignments by structure,
        # then count holders per unique badge.
        attributions_par_structure = defaultdict(list)
        for attribution in attributions:
            structure = attribution.badge.issuing_structure
            attributions_par_structure[structure].append(attribution)

        # Pour chaque structure, on compte combien de personnes ont chaque badge.
        # For each structure, we count how many people have each badge.
        # Clé = structure, Valeur = dict {objet badge -> nombre de détenteurs}
        # Key = structure, Value = dict {badge object -> holder count}
        badges_uniques_par_structure_obj = {}
        for structure, liste_attributions in attributions_par_structure.items():
            compteur_par_badge = defaultdict(int)
            for attribution in liste_attributions:
                compteur_par_badge[attribution.badge] += 1
            badges_uniques_par_structure_obj[structure] = compteur_par_badge

        # Étape 2 : Répartir les badges UNIQUES en spirale autour du centre.
        # Un seul hexagone par badge unique (pas un par personne badgée).
        # Step 2: Distribute UNIQUE badges in a spiral around each center.
        # One hexagon per unique badge (not one per badged person).
        badges_uniques_par_structure = {}

        for structure, compteur_par_badge in badges_uniques_par_structure_obj.items():
            marker = structure.marker
            structure_id = str(structure.uuid)

            # Trier les badges : expert d'abord, puis par nom
            # Sort badges: expert first, then by name
            liste_badges_tries = sorted(
                compteur_par_badge.items(),
                key=lambda item: (-hauteurs_metres.get(item[0].level, 1.0), item[0].name)
            )

            # Algorithme de répartition : Spirale de Fibonacci (Phyllotaxis).
            # Distribution algorithm: Fibonacci Spiral (Phyllotaxis).
            espacement_metres = 5.0

            liste_badges_panel = []
            for index, (badge, nb_detenteurs) in enumerate(liste_badges_tries):
                # Calcul de la position en spirale
                # Spiral position calculation
                distance_r = espacement_metres * math.sqrt(index)
                angle_theta = index * 2.399963

                decalage_x = distance_r * math.cos(angle_theta)
                decalage_y = distance_r * math.sin(angle_theta)

                delta_latitude = decalage_y / 111111.0
                delta_longitude = decalage_x / (111111.0 * math.cos(math.radians(marker.lat)))

                poids_niveau = hauteurs_metres.get(badge.level, 1.0)

                badges_donnees.append({
                    "type": "badge",
                    "name": badge.name,
                    "lat": marker.lat + delta_latitude,
                    "lng": marker.lng + delta_longitude,
                    "weight": poids_niveau,
                    "holders_count": nb_detenteurs,
                    "structure": structure.name,
                    "structure_id": structure_id,
                    "level_display": badge.get_level_display(),
                })

                # Données pour le panneau latéral
                # Data for the side panel
                liste_badges_panel.append({
                    "name": badge.name,
                    "level_display": badge.get_level_display(),
                    "weight": poids_niveau,
                    "holders_count": nb_detenteurs,
                })

            badges_uniques_par_structure[structure_id] = liste_badges_panel

        # On récupère toutes les structures qui ont un marqueur pour l'IconLayer.
        # We fetch all structures with a marker for the IconLayer.
        toutes_les_structures = Structure.objects.filter(
            marker__isnull=False
        ).select_related('marker')

        structures_donnees = []
        for structure in toutes_les_structures:
            marker = structure.marker
            structure_id = str(structure.uuid)

            # Utiliser le logo de la structure, ou l'icône par défaut
            # Use the structure's logo, or the default icon
            icon_url = DEFAULT_STRUCTURE_ICON
            if structure.logo:
                icon_url = structure.logo.url

            # Badges uniques de cette structure (pour le panneau latéral)
            # Unique badges for this structure (for the side panel)
            badges_uniques = badges_uniques_par_structure.get(structure_id, [])

            # Nombre total de personnes badgées dans cette structure
            # Total number of badged people in this structure
            nombre_personnes = sum(b["holders_count"] for b in badges_uniques)

            structures_donnees.append({
                "type": "structure",
                "name": structure.name,
                "description": structure.description or "",
                "lat": marker.lat,
                "lng": marker.lng,
                "icon_url": icon_url,
                "badge_count": len(badges_uniques),
                "holders_count": nombre_personnes,
                "structure_id": structure_id,
                "type_display": structure.get_type_display(),
                "badges": badges_uniques,
            })

        return JsonResponse({
            "badges": badges_donnees,
            "structures": structures_donnees,
        }, safe=False)
