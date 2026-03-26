"""
Vues du generateur de badges — page unique avec preview temps reel.
On remplace le wizard 5 etapes par une seule page.
L'utilisateur choisit la categorie, le niveau, et ecrit le titre.
La preview se met a jour a la volee via HTMX.

Badge generator views — single page with real-time preview.
Replaces the 5-step wizard with one page.
User picks category, level, writes title. Preview updates via HTMX.

LOCALISATION : badge_generator/views.py
"""

import re

from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny

from badge_generator.models import BadgeCategory, BadgeLevel, GeneratedBadge
from badge_generator.serializers import GenerateBadgeSerializer, PreviewBadgeSerializer,CreateBadgeValidator
from badge_generator.shapes import ALL_SHAPES, DEFAULT_SHAPE_KEY
from badge_generator.svg_engine import generate_badge_svg
from core.models import Badge, BadgeHistory, BadgeCriteria, Structure
from django.core.files.base import ContentFile


class BadgeGeneratorViewSet(viewsets.ViewSet):
    """
    Le ViewSet du generateur de badges.
    Page unique avec selecteurs en temps reel.
    Single-page badge generator with real-time selectors.
    """

    # Tout le monde peut utiliser le generateur. Pas besoin de connexion.
    # Everyone can use the generator, no login required.
    permission_classes = [AllowAny]

    # ========================================================================
    # Page principale du generateur.
    # On affiche toutes les categories et niveaux sur une seule page.
    # Main generator page with all categories and levels.
    # ========================================================================

    def list(self, request):
        # On recupere les categories qui ont une abbreviation (les 8 du Dome).
        # Les anciennes categories sans abbreviation ne sont pas affichees.
        # Get categories with abbreviation (the 8 Dome categories).
        # Old categories without abbreviation are not displayed.
        all_categories = BadgeCategory.objects.exclude(abbreviation="")
        all_levels = BadgeLevel.objects.all()

        # On compte le nombre total de badges generes.
        # Count total generated badges.
        total_badges_generated = GeneratedBadge.objects.count()

        # On prepare la liste des formes disponibles pour le template.
        # Build shape list for the template.
        all_available_shapes = []
        for shape_key, shape_data in ALL_SHAPES.items():
            all_available_shapes.append({
                "key": shape_key,
                "name": shape_data["name"],
                "description": shape_data["description"],
                "path": shape_data["path"],
            })

        structures = request.user.structures

        return render(request, "badge_generator/badge_creation.html", {
            "categories": all_categories,
            "levels": all_levels,
            "total_badges_generated": total_badges_generated,
            "shapes": all_available_shapes,
            "default_shape_key": DEFAULT_SHAPE_KEY,
            "structures": structures,
        })

    # ========================================================================
    # Previsualisation en direct du badge.
    # On genere le SVG a la volee pour montrer a l'utilisateur ce que ca donne.
    # HTMX appelle cette vue a chaque changement de selection.
    # Live badge preview, generating SVG on the fly via HTMX.
    # ========================================================================

    @action(detail=False, methods=["GET"])
    def preview(self, request):
        # On valide les parametres recus.
        # Validate received parameters.
        serializer = PreviewBadgeSerializer(data=request.GET)

        if not serializer.is_valid():
            return render(request, "badge_generator/partials/_badge_preview.html", {
                "badge_svg": "",
            })

        validated = serializer.validated_data

        # On cherche la categorie si elle est fournie.
        # Find category if provided.
        category_name = ""
        category_color = "#009eb9"
        illustration_svg = ""

        category_uuid = validated.get("category_uuid")
        if category_uuid:
            chosen_category = BadgeCategory.objects.filter(uuid=category_uuid).first()
            if chosen_category:
                category_name = chosen_category.name
                category_color = chosen_category.color
                illustration_svg = chosen_category.illustration_svg

        # On cherche le niveau si il est fourni.
        # Find level if provided.
        level_stroke_width = 3
        level_posture_text = ""

        level_uuid = validated.get("level_uuid")
        if level_uuid:
            chosen_level = BadgeLevel.objects.filter(uuid=level_uuid).first()
            if chosen_level:
                level_stroke_width = chosen_level.stroke_width
                level_posture_text = chosen_level.posture_text

        # On recupere le titre, le sous-titre et la forme.
        # Get title, subtitle and shape.
        title = validated.get("title", "") or "Badge"
        subtitle = validated.get("subtitle", "")
        shape_key = validated.get("shape", DEFAULT_SHAPE_KEY)

        # On genere le SVG du badge avec la forme choisie.
        # Generate badge SVG with chosen shape.
        badge_svg = generate_badge_svg(
            category_name=category_name,
            category_color=category_color,
            level_stroke_width=level_stroke_width,
            level_posture_text=level_posture_text,
            illustration_svg=illustration_svg,
            title=title,
            subtitle=subtitle,
            shape_key=shape_key,
        )

        return render(request, "badge_generator/partials/_badge_preview.html", {
            "badge_svg": badge_svg,
        })

    # ========================================================================
    # Generation finale et sauvegarde du badge.
    # On enregistre le badge dans la base de donnees.
    # Final badge generation and save to database.
    # ========================================================================

    @action(detail=False, methods=["POST"])
    def generate(self, request):
        # On valide toutes les donnees.
        # Validate all data.
        serializer = GenerateBadgeSerializer(data=request.POST)

        if not serializer.is_valid():
            return render(request, "badge_generator/partials/_step_error.html", {
                "errors": serializer.errors,
            })

        validated = serializer.validated_data

        # On cherche les objets dans la base de donnees.
        # Find database objects.
        chosen_category = get_object_or_404(
            BadgeCategory, uuid=validated["category_uuid"]
        )
        chosen_level = get_object_or_404(
            BadgeLevel, uuid=validated["level_uuid"]
        )

        # On recupere la forme choisie.
        # Get the chosen shape.
        shape_key = validated.get("shape", DEFAULT_SHAPE_KEY)

        # On genere le SVG final avec la forme choisie.
        # Generate final SVG with chosen shape.
        badge_svg = generate_badge_svg(
            category_name=chosen_category.name,
            category_color=chosen_category.color,
            level_stroke_width=chosen_level.stroke_width,
            level_posture_text=chosen_level.posture_text,
            illustration_svg=chosen_category.illustration_svg,
            title=validated["title"],
            subtitle=validated.get("subtitle", ""),
            shape_key=shape_key,
        )

        # On sauvegarde le badge dans la base de donnees.
        # Save badge to database.
        generated_badge = GeneratedBadge.objects.create(
            title=validated["title"],
            subtitle=validated.get("subtitle", ""),
            category=chosen_category,
            level=chosen_level,
            primary_color=chosen_category.color,
            svg_content=badge_svg,
        )

        return render(request, "badge_generator/result.html", {
            "badge": generated_badge,
            "badge_svg": badge_svg,
        })

    # ========================================================================
    # Telechargement du badge en SVG.
    # SVG download endpoint.
    # ========================================================================

    @action(detail=True, methods=["GET"], url_path="download-svg")
    def download_svg(self, request, pk=None):
        # On cherche le badge genere.
        # Find the generated badge.
        badge = get_object_or_404(GeneratedBadge, uuid=pk)

        # On renvoie le SVG comme un fichier a telecharger.
        # Return SVG as downloadable file.
        response = HttpResponse(
            badge.svg_content,
            content_type="image/svg+xml",
        )

        # On nettoie le titre pour fabriquer un nom de fichier sur.
        # On garde seulement les lettres, chiffres, tirets et underscores.
        # Les autres caracteres sont remplaces par des underscores.
        # Sanitize title for a safe filename. Keep only alphanumeric, hyphens, underscores.
        safe_filename = re.sub(r'[^\w\-]', '_', badge.title.lower().strip())
        safe_filename = re.sub(r'_+', '_', safe_filename).strip('_')
        if not safe_filename:
            safe_filename = "badge"

        response["Content-Disposition"] = (
            f'attachment; filename="badge_{safe_filename}.svg"'
        )
        return response

    @action(detail=False, methods=["POST"])
    def create_badge(self, request):
        if not request.htmx:
            return HttpResponse("Une erreur est survenue")

        if request.method == "GET":
            # TODO Merge this route with "list" route
            return render(request, "badge_generator/partials/_badge_preview.html", {})

        validator = CreateBadgeValidator(data=request.POST)
        is_valid = validator.is_valid()
        if not is_valid:
            print(validator.errors)
            # TODO add error display
            return HttpResponse(validator.errors)

        validated = validator.validated_data

        # On cherche les objets dans la base de donnees.
        # Find database objects.
        chosen_category = get_object_or_404(
            BadgeCategory, uuid=validated["category_uuid"]
        )
        chosen_level = get_object_or_404(
            BadgeLevel, uuid=validated["level_uuid"]
        )

        # On recupere la forme choisie.
        # Get the chosen shape.
        shape_key = validated.get("shape", DEFAULT_SHAPE_KEY)

        # On genere le SVG final avec la forme choisie.
        # Generate final SVG with chosen shape.
        svg_text = generate_badge_svg(
            category_name=chosen_category.name,
            category_color=chosen_category.color,
            level_stroke_width=chosen_level.stroke_width,
            level_posture_text=chosen_level.posture_text,
            illustration_svg=chosen_category.illustration_svg,
            title=validated["title"],
            subtitle=validated.get("subtitle", ""),
            shape_key=shape_key,
        )
        badge_data = {
            "name":validated["title"],
            "description":validated["description"],
        }
        if validated["creator_type"] == "structure":
            structure = Structure.objects.get(uuid=validated["structure_uuid"])
            badge_data["issuing_structure"] = structure
        else:
            badge_data["user"] = request.user

        badge_data["category"] = chosen_category
        badge_data["level"] = chosen_level


        # Create a badge
        badge = Badge(
            **badge_data
        )

        try:
            svg_file = ContentFile(svg_text.encode("utf-8"))
            badge.icon.save("icon.svg", svg_file)
        except TypeError:
            print("error svg file")

        badge.save()

        # Create a BadgeHistory
        badgeHistory = BadgeHistory(
            badge=badge,
            action="creation",
            details="Badge crée"
        )

        if validated["creator_type"] == "structure":
            # Create a BadgeCriteria
            badgeCriteria = BadgeCriteria(
                badge=badge,
                structure=structure,
                criteria=validated["criteria"],
            )
            print(badgeCriteria)


        print(badge)
        print(badge.icon)
        print(badgeHistory)

        # import ipdb;ipdb.set_trace()

        return HttpResponse("yes")
