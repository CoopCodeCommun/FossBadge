"""
Modeles du generateur de badges.
On range les badges par categorie et par niveau.
Chaque badge genere garde en memoire les choix faits par l'utilisateur.

Badge generator models.
Badges are organized by category and level.
Each generated badge stores the user's choices.

LOCALISATION : badge_generator/models.py
"""

import uuid

from django.db import models
from django.utils.translation import gettext_lazy as _


# ============================================================================
# Modele : BadgeCategory
# On range les badges par grande famille.
# Par exemple : "Savoir", "Engagement", "Technique".
# Badge categories group badges into families.
# ============================================================================

class BadgeCategory(models.Model):
    """
    Une categorie regroupe des badges de la meme famille.
    Exemple : "Savoir et competence", "Engagement et participation".
    A category groups badges of the same family.
    """

    uuid = models.UUIDField(
        default=uuid.uuid4,
        editable=False,
        unique=True,
        verbose_name=_("Identifiant unique"),
    )

    # Le nom de la categorie. Il doit etre court et clair.
    # Category name, short and clear.
    name = models.CharField(
        max_length=100,
        verbose_name=_("Nom de la catégorie"),
    )

    # Une description pour expliquer a quoi sert cette categorie.
    # Description explaining the category purpose.
    description = models.TextField(
        blank=True,
        default="",
        verbose_name=_("Description"),
    )

    # Une icone emoji ou texte court pour representer la categorie.
    # Short emoji or text icon for the category.
    icon = models.CharField(
        max_length=10,
        blank=True,
        default="🏷️",
        verbose_name=_("Icône"),
    )

    # La couleur principale de la categorie. On l'utilise pour la bordure du badge.
    # Main color for the category, used for the badge border.
    color = models.CharField(
        max_length=7,
        default="#4A90D9",
        verbose_name=_("Couleur principale"),
        help_text=_("Code couleur hexadécimal, par exemple #4A90D9"),
    )

    # L'abbreviation de la categorie. Par exemple "Cp" pour Competence.
    # Category abbreviation, e.g. "Cp" for Competence.
    abbreviation = models.CharField(
        max_length=5,
        blank=True,
        default="",
        verbose_name=_("Abréviation"),
        help_text=_("Abréviation courte, par exemple Cp, Sf, Se"),
    )

    # La couleur du texte et des illustrations dans le badge.
    # Text and illustration color in the badge.
    text_color = models.CharField(
        max_length=7,
        default="#473467",
        verbose_name=_("Couleur du texte"),
        help_text=_("Code couleur hexadécimal pour le texte et les illustrations"),
    )

    # Le code SVG de l'illustration centrale de la categorie.
    # On le stocke ici pour pouvoir le personnaliser dans l'admin.
    # Central illustration SVG code for this category.
    illustration_svg = models.TextField(
        blank=True,
        default="",
        verbose_name=_("Illustration SVG"),
        help_text=_("Code SVG de l'illustration centrale du badge"),
    )

    # L'ordre d'affichage. Les categories avec un petit nombre s'affichent en premier.
    # Display order. Lower numbers appear first.
    display_order = models.PositiveIntegerField(
        default=0,
        verbose_name=_("Ordre d'affichage"),
    )

    class Meta:
        ordering = ["display_order", "name"]
        verbose_name = _("Catégorie de badge")
        verbose_name_plural = _("Catégories de badges")

    def __str__(self):
        return self.name


# ============================================================================
# Modele : BadgeLevel
# Chaque categorie a plusieurs niveaux.
# Par exemple : "Decouverte", "Pratique", "Maitrise", "Expert", "Transmission".
# Badge levels within a category (e.g. beginner, intermediate, expert).
# ============================================================================

class BadgeLevel(models.Model):
    """
    Un niveau represente un degre de competence ou d'engagement.
    Chaque niveau a une forme et un style different dans le badge.
    A level represents a degree of skill or engagement.
    """

    uuid = models.UUIDField(
        default=uuid.uuid4,
        editable=False,
        unique=True,
        verbose_name=_("Identifiant unique"),
    )

    # Le nom du niveau. Par exemple : "Decouverte" ou "Expert".
    # Level name, e.g. "Beginner" or "Expert".
    name = models.CharField(
        max_length=100,
        verbose_name=_("Nom du niveau"),
    )

    # Un petit texte qui explique ce que ce niveau veut dire.
    # Short text explaining what the level means.
    description = models.TextField(
        blank=True,
        default="",
        verbose_name=_("Description"),
    )

    # Le rang du niveau. 1 = le plus bas, 5 = le plus haut.
    # Level rank. 1 = lowest, 5 = highest.
    rank = models.PositiveIntegerField(
        default=1,
        verbose_name=_("Rang"),
        help_text=_("1 = débutant, 5 = expert"),
    )

    # Le texte de posture affiche en courbe en bas du badge.
    # Par exemple : "JE DECOUVRE", "JE COMPRENDS", "JE PRATIQUE".
    # Posture text displayed curved at the bottom of the badge.
    posture_text = models.CharField(
        max_length=50,
        blank=True,
        default="",
        verbose_name=_("Texte de posture"),
        help_text=_("Texte affiché en bas du badge, ex: JE DÉCOUVRE"),
    )

    # L'epaisseur du trait de bordure pour ce niveau.
    # Plus le niveau est eleve, plus le trait est epais.
    # Border stroke width for this level. Higher levels = thicker.
    stroke_width = models.PositiveIntegerField(
        default=3,
        verbose_name=_("Épaisseur du trait"),
        help_text=_("Épaisseur du trait de bordure en pixels"),
    )

    class Meta:
        ordering = ["rank"]
        verbose_name = _("Niveau de badge")
        verbose_name_plural = _("Niveaux de badges")

    def __str__(self):
        return f"{self.name} (rang {self.rank})"


# ============================================================================
# Modele : GeneratedBadge
# Un badge cree par un utilisateur avec le generateur.
# On garde en memoire les choix faits pour pouvoir le regenerer.
# A badge created through the generator.
# ============================================================================

class GeneratedBadge(models.Model):
    """
    Un badge genere par le generateur.
    On sauvegarde tous les choix faits par l'utilisateur.
    A badge generated through the generator with all user choices saved.
    """

    uuid = models.UUIDField(
        default=uuid.uuid4,
        editable=False,
        unique=True,
        verbose_name=_("Identifiant unique"),
    )

    # Le titre du badge. C'est le texte principal affiche sur le badge.
    # Badge title, the main text displayed on the badge.
    title = models.CharField(
        max_length=100,
        verbose_name=_("Titre du badge"),
    )

    # Un sous-titre optionnel. Par exemple le nom de l'organisation.
    # Optional subtitle, e.g. organization name.
    subtitle = models.CharField(
        max_length=100,
        blank=True,
        default="",
        verbose_name=_("Sous-titre"),
    )

    # La categorie choisie pour ce badge.
    # Selected category for this badge.
    category = models.ForeignKey(
        BadgeCategory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="generated_badges",
        verbose_name=_("Catégorie"),
    )

    # Le niveau choisi pour ce badge.
    # Selected level for this badge.
    level = models.ForeignKey(
        BadgeLevel,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="generated_badges",
        verbose_name=_("Niveau"),
    )

    # La couleur principale du badge. Par defaut, c'est la couleur de la categorie.
    # Main badge color, defaults to category color.
    primary_color = models.CharField(
        max_length=7,
        default="#4A90D9",
        verbose_name=_("Couleur principale"),
    )

    # Le code SVG complet du badge genere. On le garde pour ne pas le recalculer.
    # Complete generated SVG code, cached to avoid recalculation.
    svg_content = models.TextField(
        blank=True,
        default="",
        verbose_name=_("Code SVG généré"),
    )

    # La date de creation du badge.
    # Badge creation date.
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("Date de création"),
    )

    class Meta:
        ordering = ["-created_at"]
        verbose_name = _("Badge généré")
        verbose_name_plural = _("Badges générés")

    def __str__(self):
        return self.title
