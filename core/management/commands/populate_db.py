import random
import os
from pathlib import Path
from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile
from django.core.files import File
from django.conf import settings
from django.utils import timezone
from datetime import timedelta, datetime
from core.models import Structure, Badge, User, BadgeEndorsement, BadgeAssignment, BadgeCriteria
from mapview.models import Marker

class Command(BaseCommand):
    help = 'Populate the database with development data'

    def add_arguments(self, parser):
        parser.add_argument(
            '--img',
            action='store_true',
            help='Load images for users, structures, and badges',
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Define paths to image directories
        self.base_dir = Path(__file__).resolve().parent.parent.parent.parent
        self.structure_images_dir = self.base_dir / 'media' / 'structures' / 'examples'
        self.badge_images_dir = self.base_dir / 'media' / 'badges' / 'exemples'
        self.profile_images_dir = self.base_dir / 'media' / 'users' / 'examples'

        # Get available images
        self.structure_images = list(self.structure_images_dir.glob('*.png'))
        self.badge_images = list(self.badge_images_dir.glob('*.png'))
        self.profile_images = list(self.profile_images_dir.glob('*.png'))

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS('Starting database population...'))

        # Les images sont chargees par defaut, --img n'est conserve que pour compatibilite
        # / Images are loaded by default, --img is kept for backward compatibility only
        self.load_images = True

        # Import markers from KML
        self.stdout.write('Importing markers from KML...')
        kml_path = os.path.join(settings.BASE_DIR, 'mapview/fixtures/Université Populaire de Villeurbanne.kml')
        if os.path.exists(kml_path):
            nb_markers = Marker.import_from_kml(kml_path)
            self.stdout.write(self.style.SUCCESS(f'Imported {nb_markers} markers'))
        else:
            self.stdout.write(self.style.WARNING(f'KML file not found at {kml_path}'))

        # Create users
        self.stdout.write('Creating users...')
        users = self.create_users()

        # Create structures
        self.stdout.write('Creating structures...')
        structures = self.create_structures()

        # Create badges
        self.stdout.write('Creating badges...')
        badges = self.create_badges(structures, users)

        # Connect users to structures
        self.stdout.write('Connecting users to structures...')
        self.connect_users_to_structures(users, structures)

        # Creer les criteres d'attribution par structure
        # / Create badge criteria per structure
        self.stdout.write('Creating badge criteria...')
        self.create_badge_criteria(badges, structures)

        self.stdout.write(self.style.SUCCESS('Database population completed!'))
        self.stdout.write(self.style.SUCCESS(f'Created {len(users)} users'))
        self.stdout.write(self.style.SUCCESS(f'Created {len(structures)} structures'))
        self.stdout.write(self.style.SUCCESS(f'Created {len(badges)} badges'))

    def create_users(self):
        """
        Create some users for development
        """
        users = []
        user_data = [
            {
                'username': 'jean.dupont',
                'first_name': 'Jean',
                'last_name': 'Dupont',
                'email': 'jean.dupont@example.com',
                'password': 'password123',
                'address': '123 Rue de la République, 75001 Paris'
            },
            {
                'username': 'marie.durand',
                'first_name': 'Marie',
                'last_name': 'Durand',
                'email': 'marie.durand@example.com',
                'password': 'password123',
                'address': '456 Avenue des Champs-Élysées, 75008 Paris'
            },
            {
                'username': 'pierre.martin',
                'first_name': 'Pierre',
                'last_name': 'Martin',
                'email': 'pierre.martin@example.com',
                'password': 'password123',
                'address': '789 Boulevard Saint-Michel, 75005 Paris'
            },
            {
                'username': 'sophie.lefebvre',
                'first_name': 'Sophie',
                'last_name': 'Lefebvre',
                'email': 'sophie.lefebvre@example.com',
                'password': 'password123',
                'address': '101 Rue de Rivoli, 75001 Paris'
            },
            {
                'username': 'lucas.bernard',
                'first_name': 'Lucas',
                'last_name': 'Bernard',
                'email': 'lucas.bernard@example.com',
                'password': 'password123',
                'address': '202 Avenue Montaigne, 75008 Paris'
            },
            {
                'username': 'thomas.petit',
                'first_name': 'Thomas',
                'last_name': 'Petit',
                'email': 'thomas.petit@example.com',
                'password': 'password123',
                'address': '12 Rue des Lilas, 69100 Villeurbanne'
            },
            {
                'username': 'julie.moreau',
                'first_name': 'Julie',
                'last_name': 'Moreau',
                'email': 'julie.moreau@example.com',
                'password': 'password123',
                'address': '34 Avenue Roger Salengro, 69100 Villeurbanne'
            },
            {
                'username': 'nicolas.girard',
                'first_name': 'Nicolas',
                'last_name': 'Girard',
                'email': 'nicolas.girard@example.com',
                'password': 'password123',
                'address': '56 Rue du 1er Mars 1943, 69100 Villeurbanne'
            },
            {
                'username': 'emilie.rousseau',
                'first_name': 'Émilie',
                'last_name': 'Rousseau',
                'email': 'emilie.rousseau@example.com',
                'password': 'password123',
                'address': '78 Cours Émile Zola, 69100 Villeurbanne'
            },
            {
                'username': 'antoine.mercier',
                'first_name': 'Antoine',
                'last_name': 'Mercier',
                'email': 'antoine.mercier@example.com',
                'password': 'password123',
                'address': '90 Rue de la Doua, 69100 Villeurbanne'
            },
            {
                'username': 'isabelle.blanc',
                'first_name': 'Isabelle',
                'last_name': 'Blanc',
                'email': 'isabelle.blanc@example.com',
                'password': 'password123',
                'address': '12 Boulevard du 11 Novembre, 69100 Villeurbanne'
            },
            {
                'username': 'marc.leroy',
                'first_name': 'Marc',
                'last_name': 'Leroy',
                'email': 'marc.leroy@example.com',
                'password': 'password123',
                'address': '34 Rue de l\'Egalité, 69100 Villeurbanne'
            },
            {
                'username': 'claire.dubois',
                'first_name': 'Claire',
                'last_name': 'Dubois',
                'email': 'claire.dubois@example.com',
                'password': 'password123',
                'address': '56 Avenue de la Fraternité, 69100 Villeurbanne'
            },
            {
                'username': 'alexandre.fournier',
                'first_name': 'Alexandre',
                'last_name': 'Fournier',
                'email': 'alexandre.fournier@example.com',
                'password': 'password123',
                'address': '78 Rue de la Liberté, 69100 Villeurbanne'
            },
            {
                'username': 'sophie.martin',
                'first_name': 'Sophie',
                'last_name': 'Martin',
                'email': 'sophie.martin@example.com',
                'password': 'password123',
                'address': '90 Cours de la République, 69100 Villeurbanne'
            }
        ]

        for data in user_data:
            user, created = User.objects.get_or_create(
                username=data['username'],
                defaults={
                    'first_name': data['first_name'],
                    'last_name': data['last_name'],
                    'email': data['email'],
                    'address': data['address'],
                }
            )

            # Add an avatar image if available and not already set, and --img argument is provided
            if self.profile_images and (created or not user.avatar) and self.load_images:
                # Get a random image from the available profile images
                image_path = random.choice(self.profile_images)
                with open(image_path, 'rb') as f:
                    user.avatar.save(
                        os.path.basename(image_path),
                        File(f),
                        save=True
                    )
                self.stdout.write(f"Added avatar {os.path.basename(image_path)} to {user.username}")

            users.append(user)

        return users

    def create_structures(self):
        """
        Create structures based on KML data and ESS/Culture themes
        """
        structures = []
        structure_data = [
            {
                'name': 'Le Rize',
                'type': 'association',
                'address': '23-25 Rue Valentin Haüy, 69100 Villeurbanne',
                'siret': '123 456 789 00012',
                'description': 'Lieu de mémoire, de culture et de citoyenneté. Animation scientifique, accueil de chercheurs et doctorants, conservation.',
                'referent_last_name': 'Dubois',
                'referent_first_name': 'Claire',
                'referent_position': 'Responsable',
                'latitude': 45.7597974,
                'longitude': 4.8833939
            },
            {
                'name': 'CCO Villeurbanne',
                'type': 'association',
                'address': '39 Rue Georges Courteline, 69100 Villeurbanne',
                'siret': '987 654 321 00034',
                'description': 'Centre de Culture Ouvrière. Human Library, atelier fabrique de la Loi, festival des arts participatifs. Un laboratoire d\'innovation sociale et culturelle.',
                'referent_last_name': 'Martin',
                'referent_first_name': 'Thomas',
                'referent_position': 'Directeur',
                'latitude': 45.7568332,
                'longitude': 4.9182412
            },
            {
                'name': 'La BRICC / Miete',
                'type': 'association',
                'address': '84 Rue du Docteur Rollet, 69100 Villeurbanne',
                'siret': '456 789 123 00056',
                'description': 'Atelier de bricolage bois, imprimante 3D, et espace de mutualisation pour l\'économie circulaire et solidaire.',
                'referent_last_name': 'Petit',
                'referent_first_name': 'Sophie',
                'referent_position': 'Coordinatrice',
                'latitude': 45.7640488,
                'longitude': 4.8908612
            },
            {
                'name': 'Atelier Soudé',
                'type': 'association',
                'address': 'Villeurbanne',
                'siret': '789 123 456 00078',
                'description': 'Repair Café spécialisé dans les réparations électriques et électroniques pour lutter contre l\'obsolescence programmée.',
                'referent_last_name': 'Leroy',
                'referent_first_name': 'Marc',
                'referent_position': 'Animateur',
                'latitude': 45.7618791,
                'longitude': 4.8827956
            },
            {
                'name': 'Ecole Nationale de Musique',
                'type': 'school',
                'address': '85 Rue Cours de la République, 69100 Villeurbanne',
                'siret': '321 654 987 00090',
                'description': 'Enseignement musical avec une forte présence hors les murs (200h d\'enseignement dans les quartiers).',
                'referent_last_name': 'Moreau',
                'referent_first_name': 'Julie',
                'referent_position': 'Directrice',
                'latitude': 45.7669012,
                'longitude': 4.8733113
            },
            {
                'name': 'KILT (Low Tech)',
                'type': 'association',
                'address': 'Villeurbanne',
                'siret': '654 987 321 00012',
                'description': 'Centre Intergalactique des Low Tech. Promotion des technologies sobres, réparables et accessibles.',
                'referent_last_name': 'Fournier',
                'referent_first_name': 'Alexandre',
                'referent_position': 'Président',
                'latitude': 45.7672572,
                'longitude': 4.9070005
            },
            {
                'name': 'La Myne',
                'type': 'association',
                'address': '1 Rue du Platane, 69100 Villeurbanne',
                'siret': '987 321 654 00034',
                'description': 'Tiers-lieu de recherche et d\'expérimentation sur les communs, l\'écologie et la technologie appropriée.',
                'referent_last_name': 'Girard',
                'referent_first_name': 'Émilie',
                'referent_position': 'Facilitatrice',
                'latitude': 45.7835745,
                'longitude': 4.8843974
            },
            {
                'name': 'Le Zola',
                'type': 'association',
                'address': '28 Avenue Roger Salengro, 69100 Villeurbanne',
                'siret': '123 789 456 00056',
                'description': 'Cinéma d\'art et d\'essai proposant des formats innovants comme "science et cinéma".',
                'referent_last_name': 'Rousseau',
                'referent_first_name': 'Nicolas',
                'referent_position': 'Programmateur',
                'latitude': 45.7700454,
                'longitude': 4.8798022
            },
            {
                'name': 'Maison du Citoyen',
                'type': 'association',
                'address': 'Villeurbanne',
                'siret': '456 123 789 00078',
                'description': 'Espace d\'accueil et de soutien aux initiatives citoyennes et à la vie associative locale.',
                'referent_last_name': 'Blanc',
                'referent_first_name': 'Isabelle',
                'referent_position': 'Coordinatrice',
                'latitude': 45.7787708,
                'longitude': 4.8893294
            },
            {
                'name': 'Université Populaire',
                'type': 'association',
                'address': 'Villeurbanne',
                'siret': '789 456 123 00090',
                'description': 'Favoriser l\'accès de tous au savoir et à la culture tout au long de la vie.',
                'referent_last_name': 'Mercier',
                'referent_first_name': 'Antoine',
                'referent_position': 'Président',
                'latitude': 45.766543,
                'longitude': 4.879528
            }
        ]

        for data in structure_data:
            # Try to find a matching marker for this structure
            # Special case for CCO to match CCO in KML
            lookup_name = 'CCO' if data['name'] == 'CCO Villeurbanne' else data['name']
            # Special case for KILT to match KILT in KML
            if data['name'] == 'KILT (Low Tech)': lookup_name = 'KILT'
            # Special case for Université Populaire
            if data['name'] == 'Université Populaire': lookup_name = 'Université Populaire de Villeurbanne'

            matching_marker = Marker.objects.filter(name__icontains=lookup_name).first()

            structure, created = Structure.objects.get_or_create(
                name=data['name'],
                defaults={
                    'type': data['type'],
                    'address': data['address'],
                    'siret': data['siret'],
                    'description': data['description'],
                    'referent_last_name': data['referent_last_name'],
                    'referent_first_name': data['referent_first_name'],
                    'referent_position': data['referent_position'],
                    'latitude': data['latitude'],
                    'longitude': data['longitude'],
                    'marker': matching_marker
                }
            )

            # If the structure already existed but had no marker, update it
            if not created and matching_marker and not structure.marker:
                structure.marker = matching_marker
                structure.save()

            # Add a logo image if available and not already set, and --img argument is provided
            if (created or not structure.logo) and self.load_images:
                if self.structure_images:
                    # Get a random image from the available structure images
                    image_path = random.choice(self.structure_images)
                    with open(image_path, 'rb') as f:
                        structure.logo.save(
                            os.path.basename(image_path),
                            File(f),
                            save=True
                        )
                    self.stdout.write(f"Added logo {os.path.basename(image_path)} to {structure.name}")

            structures.append(structure)

        return structures

    def create_badges(self, structures, users):
        """
        Creer les badges avec des themes ESS, education populaire, fablab, lowtech, culture.
        Chaque badge est attribue a des personnes VIA la structure emettrice ou une structure
        qui l'endosse, avec des notes realistes.
        / Create badges with ESS, popular education, fablab, lowtech, culture themes.
        Each badge is assigned to holders VIA the issuing or endorsing structure,
        with realistic notes.
        """
        badges = []
        badge_data = [
            # --- Le Rize (Memoire et culture) ---
            {
                'name': 'Médiateur Culturel',
                'level': 'expert',
                'description': 'Expertise dans la conception et l\'animation de dispositifs de médiation entre les oeuvres, les savoirs et les publics.',
                'issuing_structure': 'Le Rize'
            },
            {
                'name': 'Archiviste Citoyen',
                'level': 'intermediate',
                'description': 'Aide à la conservation et à la mise en valeur de la mémoire locale.',
                'issuing_structure': 'Le Rize'
            },
            {
                'name': 'Guide de Mémoire',
                'level': 'expert',
                'description': 'Animation de parcours patrimoniaux dans les quartiers de Villeurbanne.',
                'issuing_structure': 'Le Rize'
            },
            {
                'name': 'Médiateur Interculturel',
                'level': 'expert',
                'description': 'Facilitation du dialogue entre cultures et générations dans le quartier.',
                'issuing_structure': 'Le Rize'
            },
            {
                'name': 'Collecteur de Récits',
                'level': 'beginner',
                'description': 'Recueil de témoignages d\'habitants sur l\'histoire du quartier.',
                'issuing_structure': 'Le Rize'
            },
            {
                'name': 'Chercheur Populaire',
                'level': 'intermediate',
                'description': 'Participation à des programmes de recherche-action avec les habitants.',
                'issuing_structure': 'Le Rize'
            },

            # --- CCO Villeurbanne (Innovation sociale et solidaire) ---
            {
                'name': 'Animateur de Vie Sociale',
                'level': 'intermediate',
                'description': 'Capacité à animer des groupes, favoriser le lien social et accompagner des projets citoyens.',
                'issuing_structure': 'CCO Villeurbanne'
            },
            {
                'name': 'Organisateur de Festival',
                'level': 'expert',
                'description': 'Coordination d\'événements culturels participatifs, de la conception à la réalisation.',
                'issuing_structure': 'CCO Villeurbanne'
            },
            {
                'name': 'Facilitateur de Débat',
                'level': 'intermediate',
                'description': 'Animation de discussions citoyennes et de cercles de parole ouverts à tous.',
                'issuing_structure': 'CCO Villeurbanne'
            },
            {
                'name': 'Ambassadeur de l\'Hospitalité',
                'level': 'beginner',
                'description': 'Accueil et orientation des nouveaux arrivants dans le lieu et le quartier.',
                'issuing_structure': 'CCO Villeurbanne'
            },
            {
                'name': 'Animateur de Laboratoire Social',
                'level': 'intermediate',
                'description': 'Expérimentation de nouvelles formes de solidarité et d\'entraide entre habitants.',
                'issuing_structure': 'CCO Villeurbanne'
            },
            {
                'name': 'Co-constructeur de Loi',
                'level': 'expert',
                'description': 'Participation active à la fabrique citoyenne de la loi lors d\'ateliers participatifs.',
                'issuing_structure': 'CCO Villeurbanne'
            },

            # --- La BRICC / Miete (Bricolage, reemploi, fablab) ---
            {
                'name': 'Bricoleur Bois Partagé',
                'level': 'beginner',
                'description': 'Maîtrise des outils de base du travail du bois en autonomie dans un atelier partagé.',
                'issuing_structure': 'La BRICC / Miete'
            },
            {
                'name': 'Menuisier Circulaire',
                'level': 'intermediate',
                'description': 'Fabrication de meubles et objets à partir de matériaux de récupération.',
                'issuing_structure': 'La BRICC / Miete'
            },
            {
                'name': 'Opérateur Impression 3D',
                'level': 'beginner',
                'description': 'Utilisation autonome de l\'imprimante 3D pour des projets personnels ou collectifs.',
                'issuing_structure': 'La BRICC / Miete'
            },
            {
                'name': 'Réparateur de Meubles',
                'level': 'beginner',
                'description': 'Remise en état de mobilier en bois : collage, ponçage, assemblage simple.',
                'issuing_structure': 'La BRICC / Miete'
            },
            {
                'name': 'Formateur Machines-outils',
                'level': 'expert',
                'description': 'Transmission des règles de sécurité et d\'utilisation des machines (scie à ruban, défonceuse, tour).',
                'issuing_structure': 'La BRICC / Miete'
            },
            {
                'name': 'Gestionnaire de Matériauthèque',
                'level': 'intermediate',
                'description': 'Tri, rangement et valorisation des chutes de bois et matériaux donnés.',
                'issuing_structure': 'La BRICC / Miete'
            },

            # --- Atelier Soude (Reparation electronique, anti-obsolescence) ---
            {
                'name': 'Réparateur Electronique',
                'level': 'intermediate',
                'description': 'Aptitude à diagnostiquer et réparer des appareils électroniques simples pour prolonger leur durée de vie.',
                'issuing_structure': 'Atelier Soudé'
            },
            {
                'name': 'Expert en Soudure',
                'level': 'expert',
                'description': 'Maîtrise des techniques de soudure sur circuits imprimés (CMS et traversant).',
                'issuing_structure': 'Atelier Soudé'
            },
            {
                'name': 'Diagnostiqueur Electronique',
                'level': 'intermediate',
                'description': 'Identification de pannes courantes : alimentation, condensateur, connectique.',
                'issuing_structure': 'Atelier Soudé'
            },
            {
                'name': 'Sauveur d\'Appareils',
                'level': 'beginner',
                'description': 'Premiers gestes de réparation : nettoyage, remplacement de câble, remontage.',
                'issuing_structure': 'Atelier Soudé'
            },
            {
                'name': 'Démonteur Méthodique',
                'level': 'beginner',
                'description': 'Ouverture propre d\'un appareil, tri et identification des composants réutilisables.',
                'issuing_structure': 'Atelier Soudé'
            },
            {
                'name': 'Formateur Anti-Obsolescence',
                'level': 'expert',
                'description': 'Animation d\'ateliers de sensibilisation à la durabilité des objets électroniques.',
                'issuing_structure': 'Atelier Soudé'
            },

            # --- Ecole Nationale de Musique (Pratique musicale, education artistique) ---
            {
                'name': 'Pratique Instrumentale Collective',
                'level': 'intermediate',
                'description': 'Participation active à un ensemble musical : écoute, justesse, cohésion de groupe.',
                'issuing_structure': 'Ecole Nationale de Musique'
            },
            {
                'name': 'Musicien Hors-les-murs',
                'level': 'intermediate',
                'description': 'Performance musicale dans l\'espace public et les lieux hors école.',
                'issuing_structure': 'Ecole Nationale de Musique'
            },
            {
                'name': 'Eveilleur Musical',
                'level': 'beginner',
                'description': 'Initiation des enfants aux sons, aux rythmes et au plaisir de jouer ensemble.',
                'issuing_structure': 'Ecole Nationale de Musique'
            },
            {
                'name': 'Compositeur Collectif',
                'level': 'expert',
                'description': 'Création de morceaux de musique en groupe, de l\'écriture à l\'interprétation.',
                'issuing_structure': 'Ecole Nationale de Musique'
            },
            {
                'name': 'Percussionniste de Rue',
                'level': 'beginner',
                'description': 'Maîtrise des rythmes de base pour défilés et animations de quartier.',
                'issuing_structure': 'Ecole Nationale de Musique'
            },
            {
                'name': 'Pratique Orchestrale',
                'level': 'intermediate',
                'description': 'Capacité à tenir sa partie dans un ensemble symphonique ou jazz.',
                'issuing_structure': 'Ecole Nationale de Musique'
            },

            # --- KILT (Low Tech, sobriete) ---
            {
                'name': 'Eclaireur Low-Tech',
                'level': 'beginner',
                'description': 'Sensibilisation et mise en pratique des principes de la low-tech : sobriété, accessibilité, durabilité.',
                'issuing_structure': 'KILT (Low Tech)'
            },
            {
                'name': 'Constructeur de Four Solaire',
                'level': 'intermediate',
                'description': 'Fabrication d\'un système de cuisson solaire à partir de matériaux de récupération.',
                'issuing_structure': 'KILT (Low Tech)'
            },
            {
                'name': 'Concepteur de Low-Tech',
                'level': 'expert',
                'description': 'Conception de solutions techniques simples, réparables et documentées.',
                'issuing_structure': 'KILT (Low Tech)'
            },
            {
                'name': 'Bidouilleur Économe',
                'level': 'beginner',
                'description': 'Réparation et détournement d\'objets du quotidien avec des moyens limités.',
                'issuing_structure': 'KILT (Low Tech)'
            },
            {
                'name': 'Documentaliste du Faire',
                'level': 'intermediate',
                'description': 'Rédaction de tutoriels clairs pour partager des savoir-faire pratiques.',
                'issuing_structure': 'KILT (Low Tech)'
            },
            {
                'name': 'Ambassadeur de la Sobriété',
                'level': 'beginner',
                'description': 'Sensibilisation aux modes de vie résilients et à la consommation raisonnée.',
                'issuing_structure': 'KILT (Low Tech)'
            },

            # --- La Myne (Communs, ecologie, recherche participative) ---
            {
                'name': 'Facilitateur de Communs',
                'level': 'expert',
                'description': 'Capacité à documenter, partager et gérer des ressources partagées au sein d\'un collectif.',
                'issuing_structure': 'La Myne'
            },
            {
                'name': 'Expérimentateur d\'Écologie',
                'level': 'intermediate',
                'description': 'Mise en place de protocoles de test pour la qualité de l\'air, de l\'eau ou des sols.',
                'issuing_structure': 'La Myne'
            },
            {
                'name': 'Bidouilleur Éthique',
                'level': 'beginner',
                'description': 'Usage critique et détournement positif des outils numériques et matériels.',
                'issuing_structure': 'La Myne'
            },
            {
                'name': 'Facilitateur de Recherche Ouverte',
                'level': 'expert',
                'description': 'Coordination de projets de recherche citoyenne ouverts et documentés.',
                'issuing_structure': 'La Myne'
            },
            {
                'name': 'Curateur de Connaissances',
                'level': 'expert',
                'description': 'Organisation et maintenance d\'une base de savoirs partagés (wiki, fiches).',
                'issuing_structure': 'La Myne'
            },
            {
                'name': 'Documentariste de Communs',
                'level': 'intermediate',
                'description': 'Documentation écrite et visuelle de l\'histoire et des pratiques d\'un commun.',
                'issuing_structure': 'La Myne'
            },

            # --- Le Zola (Cinema, culture, mediation) ---
            {
                'name': 'Ciné-Sciences',
                'level': 'beginner',
                'description': 'Participation aux cycles de réflexion croisant septième art et vulgarisation scientifique.',
                'issuing_structure': 'Le Zola'
            },
            {
                'name': 'Organisateur de Ciné-Débat',
                'level': 'expert',
                'description': 'Conception de soirées thématiques autour d\'un film avec intervenant.',
                'issuing_structure': 'Le Zola'
            },
            {
                'name': 'Projectionniste Bénévole',
                'level': 'intermediate',
                'description': 'Aide technique à la projection de films en salle et en plein air.',
                'issuing_structure': 'Le Zola'
            },
            {
                'name': 'Accueillant Public',
                'level': 'beginner',
                'description': 'Accueil du public, gestion de la billetterie associative et orientation.',
                'issuing_structure': 'Le Zola'
            },
            {
                'name': 'Programmateur Jeune Public',
                'level': 'expert',
                'description': 'Sélection de films adaptés aux enfants et aux scolaires.',
                'issuing_structure': 'Le Zola'
            },
            {
                'name': 'Critique de Cinéma Scientifique',
                'level': 'intermediate',
                'description': 'Analyse des thématiques scientifiques portées par le cinéma documentaire.',
                'issuing_structure': 'Le Zola'
            },

            # --- Maison du Citoyen (Vie associative, entraide) ---
            {
                'name': 'Engagement Citoyen',
                'level': 'intermediate',
                'description': 'Implication active dans la vie associative locale et soutien aux projets de quartier.',
                'issuing_structure': 'Maison du Citoyen'
            },
            {
                'name': 'Accompagnateur de Projet',
                'level': 'expert',
                'description': 'Soutien méthodologique aux porteurs de projets associatifs locaux.',
                'issuing_structure': 'Maison du Citoyen'
            },
            {
                'name': 'Veilleur de Solidarité',
                'level': 'beginner',
                'description': 'Identification des besoins et des fragilités dans le quartier.',
                'issuing_structure': 'Maison du Citoyen'
            },
            {
                'name': 'Animateur de Quartier',
                'level': 'intermediate',
                'description': 'Organisation de fêtes de voisins, vide-greniers et goûters partagés.',
                'issuing_structure': 'Maison du Citoyen'
            },
            {
                'name': 'Facilitateur d\'Entraide',
                'level': 'beginner',
                'description': 'Mise en relation de citoyens pour du troc de services et de savoirs.',
                'issuing_structure': 'Maison du Citoyen'
            },
            {
                'name': 'Coordonnateur de Bénévoles',
                'level': 'intermediate',
                'description': 'Animation et fidélisation de l\'équipe de bénévoles d\'une association.',
                'issuing_structure': 'Maison du Citoyen'
            },

            # --- Universite Populaire (Education populaire, transmission) ---
            {
                'name': 'Savoir Partagé',
                'level': 'beginner',
                'description': 'Reconnaissance de la transmission de savoirs dans le cadre de l\'éducation populaire.',
                'issuing_structure': 'Université Populaire'
            },
            {
                'name': 'Conférencier Populaire',
                'level': 'expert',
                'description': 'Capacité à transmettre un savoir complexe de manière accessible à tous.',
                'issuing_structure': 'Université Populaire'
            },
            {
                'name': 'Facilitateur de Savoirs',
                'level': 'intermediate',
                'description': 'Aide à la compréhension et à l\'échange entre apprenants dans un atelier.',
                'issuing_structure': 'Université Populaire'
            },
            {
                'name': 'Passeur de Culture',
                'level': 'beginner',
                'description': 'Diffusion des opportunités culturelles et éducatives du territoire.',
                'issuing_structure': 'Université Populaire'
            },
            {
                'name': 'Organisateur de Rencontres',
                'level': 'intermediate',
                'description': 'Mise en place logistique de conférences-débats et rencontres thématiques.',
                'issuing_structure': 'Université Populaire'
            },
            {
                'name': 'Apprenant Assidu',
                'level': 'beginner',
                'description': 'Participation régulière aux cycles de formation tout au long de l\'année.',
                'issuing_structure': 'Université Populaire'
            },
        ]

        # Dictionnaire de recherche des structures par nom
        # / Lookup dictionary for structures by name
        structure_dict = {structure.name: structure for structure in structures}

        # Notes d'assignment realistes, regroupees par theme
        # / Realistic assignment notes, grouped by theme
        assignment_notes_by_theme = {
            'Le Rize': [
                "A participé activement aux journées du patrimoine en guidant un groupe de 15 personnes.",
                "Très bonne écoute lors des entretiens avec les anciens du quartier des Buers.",
                "A collecté 12 témoignages d'habitants sur l'histoire de la soierie villeurbannaise.",
                "Excellente capacité à mettre les visiteurs à l'aise pendant les visites guidées.",
                "A contribué au classement des archives photographiques du fonds Rize.",
                "Belle initiative de lien entre les familles nouvellement arrivées et les anciens du quartier.",
            ],
            'CCO Villeurbanne': [
                "A co-organisé le festival des arts participatifs avec une équipe de 8 bénévoles.",
                "Animation exemplaire du cercle de parole sur le vivre-ensemble.",
                "Très bon accueil des familles lors de la journée portes ouvertes.",
                "A facilité 3 ateliers de la fabrique de la loi avec les collégiens.",
                "A mis en place un système d'accueil en plusieurs langues pour les nouveaux arrivants.",
                "Belle énergie dans l'animation du laboratoire de solidarité alimentaire.",
            ],
            'La BRICC / Miete': [
                "Utilise la scie à ruban en autonomie dans le respect des consignes de sécurité.",
                "A fabriqué une étagère en palette pour le coin lecture de l'association voisine.",
                "Premières impressions 3D réussies : pot à crayons et crochet de porte.",
                "A remis en état 4 chaises et une table pour la salle commune.",
                "Très bon formateur, patient et pédagogue avec les débutants sur la défonceuse.",
                "A trié et rangé tout le stock de chutes de bois de la matériauthèque.",
            ],
            'Atelier Soudé': [
                "A réparé un aspirateur et un grille-pain lors du dernier Repair Café.",
                "Maîtrise la soudure CMS et a remplacé un condensateur sur une carte mère.",
                "A identifié une alimentation défaillante sur un écran en moins de 10 minutes.",
                "Première réparation réussie : remplacement du câble d'alimentation d'une lampe.",
                "Démontage soigneux d'un lave-linge, avec tri des composants réutilisables.",
                "A animé un atelier sur l'obsolescence programmée avec 12 participants.",
            ],
            'Ecole Nationale de Musique': [
                "A joué dans l'ensemble jazz lors du concert de fin d'année au parc.",
                "Performance remarquée lors de la fête de la musique rue de la République.",
                "Belle séance d'éveil musical avec les enfants de la crèche des Buers.",
                "A composé un morceau à 4 voix pour le spectacle de quartier.",
                "A assuré la partie percussions lors du défilé de carnaval.",
                "Bonne tenue de la partie de clarinette dans le concert symphonique.",
            ],
            'KILT (Low Tech)': [
                "A construit un four solaire fonctionnel lors de l'atelier du samedi.",
                "A fabriqué un déshydrateur alimentaire solaire pour le jardin partagé.",
                "Premières réparations low-tech : lampe à partir d'un bocal, chargeur vélo.",
                "Excellent tutoriel rédigé sur la fabrication d'un rocket stove.",
                "A sensibilisé 20 personnes lors du stand low-tech au marché.",
                "A documenté en photos et textes la construction du séchoir solaire collectif.",
            ],
            'La Myne': [
                "A coordonné la documentation du projet de mesure de la qualité de l'air.",
                "A installé et calibré les capteurs de qualité de l'eau dans le jardin.",
                "A organisé un atelier de sensibilisation aux outils libres.",
                "A mis en place le wiki interne et formé 5 contributeurs.",
                "Excellente documentation du projet de composteur connecté.",
                "A facilité la rencontre entre chercheurs et habitants du quartier.",
            ],
            'Le Zola': [
                "A organisé la soirée ciné-débat sur l'eau avec un intervenant de l'université.",
                "A analysé les documentaires scientifiques de la saison dans le journal du Zola.",
                "A assuré la projection et la technique son lors de la séance plein air.",
                "Accueil chaleureux du public les vendredis soir, gestion impeccable de la caisse.",
                "A sélectionné 8 films pour le cycle jeune public de janvier.",
                "A rédigé les fiches pédagogiques pour les séances scolaires.",
            ],
            'Maison du Citoyen': [
                "A accompagné l'association de couture solidaire dans son dossier de subvention.",
                "A identifié 3 personnes isolées dans le quartier et les a orientées vers le CCAS.",
                "A organisé la fête des voisins avec 40 participants.",
                "A mis en relation une retraitée et une étudiante pour du soutien scolaire.",
                "A coordonné l'équipe de 12 bénévoles pour la collecte alimentaire.",
                "Belle organisation du vide-grenier solidaire du printemps.",
            ],
            'Université Populaire': [
                "A donné un cycle de 3 conférences sur l'histoire de l'éducation populaire.",
                "Participation assidue à l'atelier d'écriture durant tout le semestre.",
                "A aidé les participants à comprendre les bases de la comptabilité associative.",
                "A distribué le programme culturel dans les boîtes aux lettres du quartier.",
                "A organisé la logistique de la conférence-débat sur l'alimentation durable.",
                "A suivi le cycle complet de formation sur les droits des travailleurs.",
            ],
        }

        # Notes d'endossement realistes
        # / Realistic endorsement notes
        endorsement_notes = [
            "Nous reconnaissons cette compétence comme complémentaire à notre propre démarche.",
            "Ce badge correspond à des savoirs que nous valorisons dans nos ateliers.",
            "Les personnes ayant ce badge sont bienvenues dans nos activités sans évaluation supplémentaire.",
            "Nous avons constaté la qualité de cette formation lors de collaborations passées.",
            "Ce badge reflète des valeurs et des pratiques cohérentes avec notre projet associatif.",
            "Les compétences décrites correspondent à ce que nous attendons de nos intervenants.",
            "Nous avons co-construit les critères de ce badge avec la structure émettrice.",
            "Ce badge facilite la mobilité des bénévoles entre nos deux structures.",
        ]

        now = timezone.now()

        for data in badge_data:
            issuing_structure = structure_dict.get(data['issuing_structure'])
            if not issuing_structure:
                continue

            badge, created = Badge.objects.get_or_create(
                name=data['name'],
                issuing_structure=issuing_structure,
                defaults={
                    'level': data['level'],
                    'description': data['description']
                }
            )

            # Add an icon image if available and not already set, and --img argument is provided
            if (created or not badge.icon) and self.load_images:
                if self.badge_images:
                    image_path = random.choice(self.badge_images)
                    with open(image_path, 'rb') as f:
                        badge.icon.save(
                            os.path.basename(image_path),
                            File(f),
                            save=True
                        )
                    self.stdout.write(f"Added icon {os.path.basename(image_path)} to {badge.name}")

            # Structures valides pour l'attribution : emettrice + quelques autres
            # / Valid structures for assignment: issuer + a few others
            valid_structures = random.sample(structures, random.randint(1, 3))
            if issuing_structure not in valid_structures:
                valid_structures.append(issuing_structure)

            # Timeline realiste basee sur le niveau du badge
            # / Realistic timeline based on badge level
            if data['level'] == 'beginner':
                start_date = now - timedelta(days=365 * 3)
                end_date = now - timedelta(days=365 * 2)
            elif data['level'] == 'intermediate':
                start_date = now - timedelta(days=365 * 2)
                end_date = now - timedelta(days=365)
            else:
                start_date = now - timedelta(days=365)
                end_date = now

            # Choisir des detenteurs aleatoires
            # / Pick random holders
            # 1 a 3 detenteurs par badge pour que chaque user ait environ 6 badges
            # (60 badges x 2 holders / 15 users = ~8 badges/user)
            # / 1 to 3 holders per badge so each user has about 6 badges
            holders = random.sample(users, random.randint(1, 3))

            # Notes specifiques a la structure emettrice de ce badge
            # / Notes specific to the issuing structure of this badge
            structure_notes = assignment_notes_by_theme.get(data['issuing_structure'], [])

            for user in holders:
                days_range = (end_date - start_date).days
                random_days = random.randint(0, max(1, days_range))
                assignment_date = start_date + timedelta(days=random_days)

                # L'assigneur est un autre utilisateur (pas le detenteur lui-meme)
                # / The assigner is another user (not the holder themselves)
                possible_assigners = [u for u in users if u.pk != user.pk]
                assigner = random.choice(possible_assigners) if possible_assigners and random.random() > 0.2 else None

                # Choisir une structure d'attribution parmi les structures valides
                # La plupart du temps c'est la structure emettrice
                # / Pick an assigning structure from valid structures
                # Most often it's the issuing structure
                if random.random() < 0.7:
                    assigning_structure = issuing_structure
                else:
                    assigning_structure = random.choice(valid_structures)

                # Notes realistes (pas toujours presentes)
                # / Realistic notes (not always present)
                note = None
                if random.random() < 0.6 and structure_notes:
                    note = random.choice(structure_notes)

                assignment, was_created = badge.add_holder(
                    user,
                    assigned_by=assigner,
                    structure=assigning_structure,
                    notes=note,
                )

                # Mettre a jour la date d'attribution
                # / Update the assignment date
                if was_created:
                    assignment.assigned_date = assignment_date
                    assignment.save(update_fields=['assigned_date'])

                self.stdout.write(
                    f"Assigned {badge.name} to {user.username} "
                    f"via {assigning_structure.name} on {assignment_date.strftime('%Y-%m-%d')}"
                )

            # Creer des endossements pour ce badge par d'autres structures
            # / Create endorsements for this badge from other structures
            other_structures = [s for s in structures if s.pk != issuing_structure.pk]
            endorsing_count = random.randint(0, min(3, len(other_structures)))
            endorsing_structures = random.sample(other_structures, endorsing_count) if endorsing_count > 0 else []

            for structure in endorsing_structures:
                endorsement_date = start_date - timedelta(days=random.randint(30, 180))

                endorsement, e_created = BadgeEndorsement.objects.get_or_create(
                    badge=badge,
                    structure=structure,
                    defaults={
                        'endorsed_by': random.choice(users) if random.random() > 0.3 else None,
                        'endorsed_date': endorsement_date,
                        'notes': random.choice(endorsement_notes),
                    }
                )

                if e_created:
                    self.stdout.write(f"Endorsed {badge.name} by {structure.name}")

            badges.append(badge)

        return badges

    def create_badge_criteria(self, badges, structures):
        """
        Creer des criteres d'attribution pour certains badges dans certaines structures.
        Les criteres decrivent comment la structure evalue si une personne merite le badge.
        / Create attribution criteria for some badges in some structures.
        Criteria describe how the structure evaluates if a person deserves the badge.
        """
        # Criteres types par theme de structure
        # / Typical criteria by structure theme
        criteria_templates = {
            'Le Rize': [
                "Avoir participé à au moins 3 ateliers de médiation ou visites guidées.",
                "Avoir collecté au moins 5 témoignages d'habitants validés par l'équipe.",
                "Avoir animé au moins 2 parcours patrimoniaux en autonomie.",
                "Avoir contribué au classement d'un fonds d'archives pendant 20 heures minimum.",
            ],
            'CCO Villeurbanne': [
                "Avoir animé au moins 2 cercles de parole ou ateliers participatifs.",
                "Avoir co-organisé un événement culturel de bout en bout.",
                "Avoir accueilli et orienté des visiteurs lors de 3 événements minimum.",
                "Avoir participé à un cycle complet d'ateliers de la fabrique de la loi.",
            ],
            'La BRICC / Miete': [
                "Avoir suivi la formation sécurité et réalisé un projet en autonomie.",
                "Avoir fabriqué au moins 2 objets à partir de matériaux de récupération.",
                "Avoir réalisé 3 impressions 3D fonctionnelles en autonomie.",
                "Avoir participé à 10 sessions d'atelier et maîtrisé les outils de base.",
            ],
            'Atelier Soudé': [
                "Avoir réparé au moins 3 appareils lors de Repair Cafés avec succès.",
                "Avoir diagnostiqué correctement 5 pannes sur des appareils différents.",
                "Avoir participé à 3 Repair Cafés et effectué au moins une réparation.",
                "Avoir animé un atelier de sensibilisation avec au moins 8 participants.",
            ],
            'Ecole Nationale de Musique': [
                "Avoir participé à un ensemble pendant au moins un semestre.",
                "Avoir joué lors d'au moins 2 concerts publics.",
                "Avoir animé 3 séances d'éveil musical avec un groupe d'enfants.",
                "Avoir composé au moins un morceau joué en public.",
            ],
            'KILT (Low Tech)': [
                "Avoir construit au moins un objet low-tech fonctionnel documenté.",
                "Avoir participé à 5 ateliers et rédigé un tutoriel partageable.",
                "Avoir sensibilisé au moins 10 personnes lors d'un événement public.",
                "Avoir conçu et documenté une solution technique sobre et réparable.",
            ],
            'La Myne': [
                "Avoir contribué à un projet de recherche citoyenne pendant 3 mois minimum.",
                "Avoir documenté un projet sur le wiki avec photos et textes.",
                "Avoir organisé au moins 2 ateliers ouverts au public.",
                "Avoir maintenu la base de connaissances pendant au moins un semestre.",
            ],
            'Le Zola': [
                "Avoir organisé au moins 2 séances ciné-débat avec intervenant.",
                "Avoir assuré la technique lors de 5 séances de projection.",
                "Avoir accueilli le public lors de 10 séances minimum.",
                "Avoir sélectionné et présenté un cycle de films thématique.",
            ],
            'Maison du Citoyen': [
                "Avoir accompagné au moins 2 associations dans leurs démarches.",
                "Avoir identifié et orienté au moins 5 personnes vers des services adaptés.",
                "Avoir organisé au moins 1 événement de quartier rassemblant 20 personnes.",
                "Avoir coordonné une équipe de bénévoles lors d'une action collective.",
            ],
            'Université Populaire': [
                "Avoir donné au moins 2 conférences ou ateliers accessibles à tous.",
                "Avoir suivi un cycle complet de formation (8 séances minimum).",
                "Avoir aidé au moins 5 apprenants dans leur parcours de formation.",
                "Avoir organisé la logistique d'au moins 3 conférences-débats.",
            ],
        }

        criteria_created_count = 0

        for badge in badges:
            issuing_structure_name = badge.issuing_structure.name

            # Criteres de la structure emettrice (toujours)
            # / Criteria from the issuing structure (always)
            templates_for_structure = criteria_templates.get(issuing_structure_name, [])
            if templates_for_structure:
                criteria_text = random.choice(templates_for_structure)
                _, created = BadgeCriteria.objects.get_or_create(
                    badge=badge,
                    structure=badge.issuing_structure,
                    defaults={'criteria': criteria_text},
                )
                if created:
                    criteria_created_count += 1

            # Criteres des structures qui endossent ce badge (parfois)
            # / Criteria from endorsing structures (sometimes)
            endorsing_structures = BadgeEndorsement.objects.filter(
                badge=badge
            ).select_related('structure')

            for endorsement in endorsing_structures:
                # 50% de chance d'avoir des criteres specifiques pour l'endossement
                # / 50% chance of having specific criteria for the endorsement
                if random.random() < 0.5:
                    endorser_name = endorsement.structure.name
                    endorser_templates = criteria_templates.get(endorser_name, [])
                    if endorser_templates:
                        criteria_text = random.choice(endorser_templates)
                        _, created = BadgeCriteria.objects.get_or_create(
                            badge=badge,
                            structure=endorsement.structure,
                            defaults={'criteria': criteria_text},
                        )
                        if created:
                            criteria_created_count += 1

        self.stdout.write(self.style.SUCCESS(f'Created {criteria_created_count} badge criteria'))

    def connect_users_to_structures(self, users, structures):
        """
        Connect users to structures
        """
        for user in users:
            # Connect each user to 2-4 random structures
            user_structures = random.sample(structures, random.randint(2, 4))
            for structure in user_structures:
                structure.users.add(user)
