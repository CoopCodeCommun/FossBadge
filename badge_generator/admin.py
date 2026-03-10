"""
Configuration de l'admin Django pour le generateur de badges.
On enregistre les modeles pour les gerer dans l'interface admin.
Admin configuration for the badge generator models.

LOCALISATION : badge_generator/admin.py
"""

from django.contrib import admin

from badge_generator.models import BadgeCategory, BadgeLevel, GeneratedBadge


@admin.register(BadgeCategory)
class BadgeCategoryAdmin(admin.ModelAdmin):
    list_display = ["name", "abbreviation", "icon", "color", "text_color", "display_order"]
    list_editable = ["display_order"]
    search_fields = ["name", "abbreviation"]


@admin.register(BadgeLevel)
class BadgeLevelAdmin(admin.ModelAdmin):
    list_display = ["name", "rank", "posture_text", "stroke_width"]
    list_editable = ["rank", "stroke_width"]
    ordering = ["rank"]


@admin.register(GeneratedBadge)
class GeneratedBadgeAdmin(admin.ModelAdmin):
    list_display = ["title", "category", "level", "created_at"]
    list_filter = ["category", "level"]
    readonly_fields = ["uuid", "svg_content", "created_at"]
