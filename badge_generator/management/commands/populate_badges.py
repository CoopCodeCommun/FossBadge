"""
Commande pour remplir la base de donnees avec les 8 categories et 5 niveaux.
On cree des categories inspirees de la matrice du Dome,
avec les illustrations SVG et les textes de posture.
Management command to populate 8 categories x 5 levels with Dome-style data.
"""

from django.core.management.base import BaseCommand

from badge_generator.illustrations import ILLUSTRATIONS_BY_ABBREVIATION
from badge_generator.models import BadgeCategory, BadgeLevel, Pictogram


class Command(BaseCommand):
    help = "Remplit la base avec 8 catégories × 5 niveaux style Le Dôme."

    def handle(self, *args, **options):
        self.stdout.write("Création des 8 catégories...")
        self._create_categories()

        self.stdout.write("Création des 5 niveaux...")
        self._create_levels()

        self.stdout.write("Création des pictogrammes...")
        self._create_pictograms()

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
                "shape_sides": 0,
                "posture_text": "JE DÉCOUVRE",
                "stroke_width": 2,
            },
            {
                "name": "Compréhension",
                "description": "Je comprends les bases du sujet.",
                "rank": 2,
                "shape_sides": 4,
                "posture_text": "JE COMPRENDS",
                "stroke_width": 4,
            },
            {
                "name": "Pratique",
                "description": "Je pratique de manière autonome.",
                "rank": 3,
                "shape_sides": 5,
                "posture_text": "JE PRATIQUE",
                "stroke_width": 7,
            },
            {
                "name": "Maîtrise",
                "description": "Maîtrise avancée du sujet.",
                "rank": 4,
                "shape_sides": 6,
                "posture_text": "JE MAÎTRISE",
                "stroke_width": 11,
            },
            {
                "name": "Transmission",
                "description": "Capacité à transmettre et former les autres.",
                "rank": 5,
                "shape_sides": 8,
                "posture_text": "JE TRANSMETS",
                "stroke_width": 16,
            },
        ]

        for level_data in levels_to_create:
            BadgeLevel.objects.update_or_create(
                name=level_data["name"],
                defaults=level_data,
            )

    def _create_pictograms(self):
        """
        On cree des pictogrammes SVG simples comme extras optionnels.
        Ce sont des icones supplementaires que l'on peut ajouter au badge.
        Create simple SVG pictograms as optional extras.
        """

        # On garde les pictogrammes existants comme extras.
        # Keep existing pictograms as extras.
        pictograms_to_create = [
            {
                "name": "Livre",
                "tags": "savoir,lecture,apprentissage,formation",
                "svg_content": (
                    '<path d="M20 15 C20 10, 50 10, 50 15 '
                    'C50 10, 80 10, 80 15 L80 80 '
                    'C80 75, 50 75, 50 80 '
                    'C50 75, 20 75, 20 80 Z" '
                    'fill-opacity="0.9"/>'
                    '<line x1="50" y1="15" x2="50" y2="80" '
                    'stroke="currentColor" stroke-width="2" opacity="0.5"/>'
                ),
            },
            {
                "name": "Étoile",
                "tags": "reussite,excellence,accomplissement",
                "svg_content": (
                    '<polygon points="50,5 61,35 95,35 68,57 79,90 50,70 21,90 32,57 5,35 39,35" '
                    'fill-opacity="0.9"/>'
                ),
            },
            {
                "name": "Engrenage",
                "tags": "technique,mecanique,creation,fabrication",
                "svg_content": (
                    '<path d="M43,10 L57,10 L60,22 L72,16 L80,28 L70,36 '
                    'L78,45 L90,43 L90,57 L78,60 L80,72 L70,76 '
                    'L64,66 L57,72 L57,85 L43,85 L43,72 L36,66 '
                    'L30,76 L20,72 L22,60 L10,57 L10,43 L22,45 '
                    'L20,28 L28,16 L40,22 Z" fill-opacity="0.9"/>'
                    '<circle cx="50" cy="50" r="14" fill="none" '
                    'stroke="currentColor" stroke-width="3" opacity="0.4"/>'
                ),
            },
            {
                "name": "Cœur",
                "tags": "engagement,passion,benevole,solidarite",
                "svg_content": (
                    '<path d="M50,85 L15,50 C5,35 10,15 30,15 '
                    'C40,15 47,22 50,28 C53,22 60,15 70,15 '
                    'C90,15 95,35 85,50 Z" fill-opacity="0.9"/>'
                ),
            },
            {
                "name": "Diplôme",
                "tags": "certification,reussite,formation,diplome",
                "svg_content": (
                    '<rect x="15" y="20" width="70" height="50" rx="3" '
                    'fill="none" stroke="currentColor" stroke-width="3" opacity="0.9"/>'
                    '<line x1="30" y1="35" x2="70" y2="35" '
                    'stroke="currentColor" stroke-width="2" opacity="0.6"/>'
                    '<line x1="30" y1="45" x2="70" y2="45" '
                    'stroke="currentColor" stroke-width="2" opacity="0.4"/>'
                    '<circle cx="50" cy="82" r="8" fill="none" '
                    'stroke="currentColor" stroke-width="2" opacity="0.7"/>'
                ),
            },
        ]

        for pictogram_data in pictograms_to_create:
            Pictogram.objects.update_or_create(
                name=pictogram_data["name"],
                defaults=pictogram_data,
            )
