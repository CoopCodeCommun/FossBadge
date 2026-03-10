"""
Commande pour remplir la base de donnees avec les 8 categories et 5 niveaux.
On cree des categories inspirees de la matrice du Dome,
avec les illustrations SVG et les textes de posture.
Management command to populate 8 categories x 5 levels with Dome-style data.

LOCALISATION : badge_generator/management/commands/populate_badges.py
"""

from django.core.management.base import BaseCommand

from badge_generator.illustrations import ILLUSTRATIONS_BY_ABBREVIATION
from badge_generator.models import BadgeCategory, BadgeLevel


class Command(BaseCommand):
    help = "Remplit la base avec 8 catégories × 5 niveaux style Le Dôme."

    def handle(self, *args, **options):
        self.stdout.write("Création des 8 catégories...")
        self._create_categories()

        self.stdout.write("Création des 5 niveaux...")
        self._create_levels()

        self.stdout.write(self.style.SUCCESS("Base de données peuplée avec succès !"))

    def _create_categories(self):
        """
        On cree les 8 grandes familles de badges.
        Chaque categorie a une couleur, une abbreviation et une illustration.
        Create the 8 badge families with color, abbreviation and illustration.
        """

        # Les 8 categories avec leurs parametres.
        # Chaque categorie a un nom, une abbreviation, une couleur et une icone.
        # 8 categories with their parameters.
        categories_to_create = [
            {
                "name": "Compétence",
                "abbreviation": "Cp",
                "description": "Reconnaître un savoir ou une compétence acquise.",
                "icon": "💡",
                "color": "#0077B6",
                "display_order": 1,
            },
            {
                "name": "Savoir-faire",
                "abbreviation": "Sf",
                "description": "Reconnaître un savoir-faire technique ou manuel.",
                "icon": "🔧",
                "color": "#E76F51",
                "display_order": 2,
            },
            {
                "name": "Savoir-être",
                "abbreviation": "Se",
                "description": "Reconnaître des qualités humaines et relationnelles.",
                "icon": "❤️",
                "color": "#E63946",
                "display_order": 3,
            },
            {
                "name": "Savoir-vivre",
                "abbreviation": "Sv",
                "description": "Reconnaître le vivre-ensemble et le respect mutuel.",
                "icon": "🤝",
                "color": "#2A9D8F",
                "display_order": 4,
            },
            {
                "name": "Projet",
                "abbreviation": "Pj",
                "description": "Reconnaître l'initiative et le lancement de projets.",
                "icon": "🚀",
                "color": "#F4A261",
                "display_order": 5,
            },
            {
                "name": "Participation",
                "abbreviation": "Pc",
                "description": "Reconnaître la participation active et le volontariat.",
                "icon": "🙌",
                "color": "#50B83C",
                "display_order": 6,
            },
            {
                "name": "Groupe",
                "abbreviation": "Gp",
                "description": "Reconnaître le travail en équipe et la communauté.",
                "icon": "👥",
                "color": "#9C6ADE",
                "display_order": 7,
            },
            {
                "name": "Expérience",
                "abbreviation": "Xp",
                "description": "Reconnaître l'expérience acquise et les défis relevés.",
                "icon": "🏔️",
                "color": "#264653",
                "display_order": 8,
            },
        ]

        for category_data in categories_to_create:
            # On recupere l'illustration SVG correspondante.
            # Get the matching SVG illustration.
            abbreviation = category_data["abbreviation"]
            illustration_svg = ILLUSTRATIONS_BY_ABBREVIATION.get(abbreviation, "")

            # On ajoute l'illustration et la couleur de texte par defaut.
            # Add illustration and default text color.
            category_data["illustration_svg"] = illustration_svg
            category_data["text_color"] = "#473467"

            # On utilise update_or_create pour ne pas creer de doublons.
            # Use update_or_create to avoid duplicates.
            BadgeCategory.objects.update_or_create(
                name=category_data["name"],
                defaults=category_data,
            )

    def _create_levels(self):
        """
        On cree les 5 niveaux de progression.
        Chaque niveau a un texte de posture et une epaisseur de trait.
        Create 5 progression levels with posture text and stroke width.
        """

        levels_to_create = [
            {
                "name": "Découverte",
                "description": "Premier contact avec le sujet.",
                "rank": 1,
                "posture_text": "JE DÉCOUVRE",
                "stroke_width": 2,
            },
            {
                "name": "Compréhension",
                "description": "Je comprends les bases du sujet.",
                "rank": 2,
                "posture_text": "JE COMPRENDS",
                "stroke_width": 4,
            },
            {
                "name": "Pratique",
                "description": "Je pratique de manière autonome.",
                "rank": 3,
                "posture_text": "JE PRATIQUE",
                "stroke_width": 7,
            },
            {
                "name": "Maîtrise",
                "description": "Maîtrise avancée du sujet.",
                "rank": 4,
                "posture_text": "JE MAÎTRISE",
                "stroke_width": 11,
            },
            {
                "name": "Transmission",
                "description": "Capacité à transmettre et former les autres.",
                "rank": 5,
                "posture_text": "JE TRANSMETS",
                "stroke_width": 16,
            },
        ]

        for level_data in levels_to_create:
            BadgeLevel.objects.update_or_create(
                name=level_data["name"],
                defaults=level_data,
            )
