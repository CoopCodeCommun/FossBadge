import uuid

from django.db import models


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
        verbose_name="Identifiant unique",
    )

    # Le nom de la categorie. Il doit etre court et clair.
    # Category name, short and clear.
    name = models.CharField(
        max_length=100,
        verbose_name="Nom de la catégorie",
    )

    # Une description pour expliquer a quoi sert cette categorie.
    # Description explaining the category purpose.
    description = models.TextField(
        blank=True,
        default="",
        verbose_name="Description",
    )

    # Une icone emoji ou texte court pour representer la categorie.
    # Short emoji or text icon for the category.
    icon = models.CharField(
        max_length=10,
        blank=True,
        default="🏷️",
        verbose_name="Icône",
    )

    # La couleur principale de la categorie. On l'utilise pour la bordure du badge.
    # Main color for the category, used for the badge border.
    color = models.CharField(
        max_length=7,
        default="#4A90D9",
        verbose_name="Couleur principale",
        help_text="Code couleur hexadécimal, par exemple #4A90D9",
    )

    # L'abbreviation de la categorie. Par exemple "Cp" pour Competence.
    # Category abbreviation, e.g. "Cp" for Competence.
    abbreviation = models.CharField(
        max_length=5,
        blank=True,
        default="",
        verbose_name="Abréviation",
        help_text="Abréviation courte, par exemple Cp, Sf, Se",
    )

    # La couleur du texte et des illustrations dans le badge.
    # Text and illustration color in the badge.
    text_color = models.CharField(
        max_length=7,
        default="#473467",
        verbose_name="Couleur du texte",
        help_text="Code couleur hexadécimal pour le texte et les illustrations",
    )

    # Le code SVG de l'illustration centrale de la categorie.
    # On le stocke ici pour pouvoir le personnaliser dans l'admin.
    # Central illustration SVG code for this category.
    illustration_svg = models.TextField(
        blank=True,
        default="",
        verbose_name="Illustration SVG",
        help_text="Code SVG de l'illustration centrale du badge",
    )

    # L'ordre d'affichage. Les categories avec un petit nombre s'affichent en premier.
    # Display order. Lower numbers appear first.
    display_order = models.PositiveIntegerField(
        default=0,
        verbose_name="Ordre d'affichage",
    )

    class Meta:
        ordering = ["display_order", "name"]
        verbose_name = "Catégorie de badge"
        verbose_name_plural = "Catégories de badges"

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
        verbose_name="Identifiant unique",
    )

    # Le nom du niveau. Par exemple : "Decouverte" ou "Expert".
    # Level name, e.g. "Beginner" or "Expert".
    name = models.CharField(
        max_length=100,
        verbose_name="Nom du niveau",
    )

    # Un petit texte qui explique ce que ce niveau veut dire.
    # Short text explaining what the level means.
    description = models.TextField(
        blank=True,
        default="",
        verbose_name="Description",
    )

    # Le rang du niveau. 1 = le plus bas, 5 = le plus haut.
    # Level rank. 1 = lowest, 5 = highest.
    rank = models.PositiveIntegerField(
        default=1,
        verbose_name="Rang",
        help_text="1 = débutant, 5 = expert",
    )

    # Le nombre de cotes du polygone qui represente le niveau dans le badge.
    # Par exemple : 3 = triangle (debutant), 6 = hexagone (expert).
    # Number of polygon sides for the badge shape (3=triangle, 6=hexagon).
    shape_sides = models.PositiveIntegerField(
        default=6,
        verbose_name="Nombre de côtés de la forme",
        help_text="3 = triangle, 4 = carré, 5 = pentagone, 6 = hexagone, 0 = cercle",
    )

    # Le texte de posture affiche en courbe en bas du badge.
    # Par exemple : "JE DECOUVRE", "JE COMPRENDS", "JE PRATIQUE".
    # Posture text displayed curved at the bottom of the badge.
    posture_text = models.CharField(
        max_length=50,
        blank=True,
        default="",
        verbose_name="Texte de posture",
        help_text="Texte affiché en bas du badge, ex: JE DÉCOUVRE",
    )

    # L'epaisseur du trait de bordure pour ce niveau.
    # Plus le niveau est eleve, plus le trait est epais.
    # Border stroke width for this level. Higher levels = thicker.
    stroke_width = models.PositiveIntegerField(
        default=3,
        verbose_name="Épaisseur du trait",
        help_text="Épaisseur du trait de bordure en pixels",
    )

    class Meta:
        ordering = ["rank"]
        verbose_name = "Niveau de badge"
        verbose_name_plural = "Niveaux de badges"

    def __str__(self):
        return f"{self.name} (rang {self.rank})"


# ============================================================================
# Modele : Pictogram
# Les pictogrammes sont les petites images au centre du badge.
# Par exemple : un livre, une main, un engrenage.
# Pictograms are the small icons in the center of the badge.
# ============================================================================

class Pictogram(models.Model):
    """
    Un pictogramme est une petite image SVG qui va au centre du badge.
    On peut filtrer les pictogrammes par categorie.
    A pictogram is a small SVG icon placed in the badge center.
    """

    uuid = models.UUIDField(
        default=uuid.uuid4,
        editable=False,
        unique=True,
        verbose_name="Identifiant unique",
    )

    # Le nom du pictogramme. Par exemple : "Livre" ou "Engrenage".
    # Pictogram name, e.g. "Book" or "Gear".
    name = models.CharField(
        max_length=100,
        verbose_name="Nom du pictogramme",
    )

    # Le code SVG du pictogramme. C'est le dessin en format texte.
    # SVG code for the pictogram drawing.
    svg_content = models.TextField(
        verbose_name="Code SVG",
        help_text="Le contenu SVG du pictogramme (balises path, circle, etc.)",
    )

    # Les categories ou ce pictogramme peut etre utilise.
    # Si vide, il est disponible partout.
    # Categories where this pictogram can be used. Empty = available everywhere.
    categories = models.ManyToManyField(
        BadgeCategory,
        blank=True,
        related_name="pictograms",
        verbose_name="Catégories associées",
    )

    # Des mots-cles pour retrouver le pictogramme plus facilement.
    # Keywords to find the pictogram more easily.
    tags = models.CharField(
        max_length=200,
        blank=True,
        default="",
        verbose_name="Mots-clés",
        help_text="Séparer les mots-clés par des virgules",
    )

    class Meta:
        ordering = ["name"]
        verbose_name = "Pictogramme"
        verbose_name_plural = "Pictogrammes"

    def __str__(self):
        return self.name


# ============================================================================
# Modele : GeneratedBadge
# Un badge cree par un utilisateur avec le generateur.
# On garde en memoire les choix faits pour pouvoir le regenerer.
# A badge created through the generator wizard.
# ============================================================================

class GeneratedBadge(models.Model):
    """
    Un badge genere par le generateur.
    On sauvegarde tous les choix faits par l'utilisateur.
    A badge generated through the wizard with all user choices saved.
    """

    uuid = models.UUIDField(
        default=uuid.uuid4,
        editable=False,
        unique=True,
        verbose_name="Identifiant unique",
    )

    # Le titre du badge. C'est le texte principal affiche sur le badge.
    # Badge title, the main text displayed on the badge.
    title = models.CharField(
        max_length=100,
        verbose_name="Titre du badge",
    )

    # Un sous-titre optionnel. Par exemple le nom de l'organisation.
    # Optional subtitle, e.g. organization name.
    subtitle = models.CharField(
        max_length=100,
        blank=True,
        default="",
        verbose_name="Sous-titre",
    )

    # La categorie choisie pour ce badge.
    # Selected category for this badge.
    category = models.ForeignKey(
        BadgeCategory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="generated_badges",
        verbose_name="Catégorie",
    )

    # Le niveau choisi pour ce badge.
    # Selected level for this badge.
    level = models.ForeignKey(
        BadgeLevel,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="generated_badges",
        verbose_name="Niveau",
    )

    # Le pictogramme choisi pour ce badge.
    # Selected pictogram for this badge.
    pictogram = models.ForeignKey(
        Pictogram,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="generated_badges",
        verbose_name="Pictogramme",
    )

    # La couleur principale du badge. Par defaut, c'est la couleur de la categorie.
    # Main badge color, defaults to category color.
    primary_color = models.CharField(
        max_length=7,
        default="#4A90D9",
        verbose_name="Couleur principale",
    )

    # La couleur secondaire du badge. Pour le fond ou les accents.
    # Secondary badge color for background or accents.
    secondary_color = models.CharField(
        max_length=7,
        default="#FFFFFF",
        verbose_name="Couleur secondaire",
    )

    # La couleur du texte sur le badge.
    # Text color on the badge.
    text_color = models.CharField(
        max_length=7,
        default="#FFFFFF",
        verbose_name="Couleur du texte",
    )

    # Le code SVG complet du badge genere. On le garde pour ne pas le recalculer.
    # Complete generated SVG code, cached to avoid recalculation.
    svg_content = models.TextField(
        blank=True,
        default="",
        verbose_name="Code SVG généré",
    )

    # La date de creation du badge.
    # Badge creation date.
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Date de création",
    )

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Badge généré"
        verbose_name_plural = "Badges générés"

    def __str__(self):
        return self.title
