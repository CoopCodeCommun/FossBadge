import random
import os
from pathlib import Path
from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile
from django.core.files import File
from django.conf import settings
from django.utils import timezone
from datetime import timedelta, datetime
from core.models import Structure, Badge, User, BadgeEndorsement
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

        # Get the --img argument
        self.load_images = kwargs.get('img', False)
        if self.load_images:
            self.stdout.write(self.style.SUCCESS('Images will be loaded'))
        else:
            self.stdout.write(self.style.SUCCESS('Images will NOT be loaded'))

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
            if self.profile_images and (created or not user.avatar) and self.load_images and not settings.PICTURES["USE_PLACEHOLDERS"]:
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
                'description': 'Tiers-lieu de recherche et d\'expérimentation sur les communs, l\'écologie et la technologie.',
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
            if (created or not structure.logo) and self.load_images and not settings.PICTURES["USE_PLACEHOLDERS"]:
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
        Create badges with ESS, Popular Education, Music and Culture themes
        """
        badges = []
        badge_data = [
            # --- BADGES EXISTANTS / EXISTING BADGES ---
            {
                'name': 'Animateur de Vie Sociale',
                'level': 'intermediate',
                'description': 'Capacité à animer des groupes, à favoriser le lien social et à accompagner des projets citoyens.',
                'issuing_structure': 'CCO Villeurbanne'
            },
            {
                'name': 'Médiateur Culturel',
                'level': 'expert',
                'description': 'Expertise dans la conception et l\'animation de dispositifs de médiation entre les œuvres, les savoirs et les publics.',
                'issuing_structure': 'Le Rize'
            },
            {
                'name': 'Réparateur Electronique',
                'level': 'intermediate',
                'description': 'Aptitude à diagnostiquer et réparer des appareils électroniques simples pour prolonger leur durée de vie.',
                'issuing_structure': 'Atelier Soudé'
            },
            {
                'name': 'Bricoleur Bois Partagé',
                'level': 'beginner',
                'description': 'Maîtrise des outils de base du travail du bois en autonomie dans un atelier partagé.',
                'issuing_structure': 'La BRICC / Miete'
            },
            {
                'name': 'Eclaireur Low-Tech',
                'level': 'beginner',
                'description': 'Sensibilisation et mise en pratique des principes de la low-tech : sobriété, accessibilité, durabilité.',
                'issuing_structure': 'KILT (Low Tech)'
            },
            {
                'name': 'Pratique Instrumentale Collective',
                'level': 'intermediate',
                'description': 'Participation active à un ensemble musical et capacité à jouer en groupe.',
                'issuing_structure': 'Ecole Nationale de Musique'
            },
            {
                'name': 'Facilitateur de Communs',
                'level': 'expert',
                'description': 'Capacité à documenter, partager et gérer des ressources partagées au sein d\'un écosystème.',
                'issuing_structure': 'La Myne'
            },
            {
                'name': 'Ciné-Sciences',
                'level': 'beginner',
                'description': 'Participation aux cycles de réflexion croisant septième art et vulgarisation scientifique.',
                'issuing_structure': 'Le Zola'
            },
            {
                'name': 'Engagement Citoyen',
                'level': 'intermediate',
                'description': 'Implication active dans la vie associative locale et soutien aux projets de quartier.',
                'issuing_structure': 'Maison du Citoyen'
            },
            {
                'name': 'Savoir Partagé',
                'level': 'beginner',
                'description': 'Reconnaissance de la transmission de savoirs dans le cadre de l\'éducation populaire.',
                'issuing_structure': 'Université Populaire'
            },

            # --- NOUVEAUX BADGES PAR STRUCTURE (5 par structure) / NEW BADGES PER STRUCTURE (5 per structure) ---
            
            # Le Rize (Mémoire et culture)
            {'name': 'Archiviste Citoyen', 'level': 'intermediate', 'description': 'Aide à la conservation de la mémoire locale.', 'issuing_structure': 'Le Rize'},
            {'name': 'Guide de Mémoire', 'level': 'expert', 'description': 'Animation de parcours patrimoniaux dans Villeurbanne.', 'issuing_structure': 'Le Rize'},
            {'name': 'Chercheur Populaire', 'level': 'intermediate', 'description': 'Participation à des programmes de recherche-action.', 'issuing_structure': 'Le Rize'},
            {'name': 'Médiateur Interculturel', 'level': 'expert', 'description': 'Facilitation du dialogue entre cultures urbaines.', 'issuing_structure': 'Le Rize'},
            {'name': 'Collecteur de Récits', 'level': 'beginner', 'description': 'Recueil de témoignages d\'habitants.', 'issuing_structure': 'Le Rize'},
            
            # CCO Villeurbanne (Innovation sociale)
            {'name': 'Organisateur de Festival', 'level': 'expert', 'description': 'Planification et coordination d\'événements culturels.', 'issuing_structure': 'CCO Villeurbanne'},
            {'name': 'Facilitateur de Débat', 'level': 'intermediate', 'description': 'Animation de discussions citoyennes et de cercles de parole.', 'issuing_structure': 'CCO Villeurbanne'},
            {'name': 'Co-constructeur de Loi', 'level': 'expert', 'description': 'Participation active à la fabrique citoyenne de la loi.', 'issuing_structure': 'CCO Villeurbanne'},
            {'name': 'Ambassadeur de l\'Hospitalité', 'level': 'beginner', 'description': 'Accueil et orientation des nouveaux arrivants.', 'issuing_structure': 'CCO Villeurbanne'},
            {'name': 'Animateur de Laboratoire Social', 'level': 'intermediate', 'description': 'Expérimentation de nouvelles formes de solidarité.', 'issuing_structure': 'CCO Villeurbanne'},

            # La BRICC / Miete (Réemploi et bricolage)
            {'name': 'Menuisier Circulaire', 'level': 'intermediate', 'description': 'Fabrication de meubles à partir de matériaux de récupération.', 'issuing_structure': 'La BRICC / Miete'},
            {'name': 'Opérateur Impression 3D', 'level': 'beginner', 'description': 'Utilisation des outils de fabrication numérique.', 'issuing_structure': 'La BRICC / Miete'},
            {'name': 'Réparateur de Meubles', 'level': 'beginner', 'description': 'Remise en état de mobilier en bois.', 'issuing_structure': 'La BRICC / Miete'},
            {'name': 'Formateur Machines-outils', 'level': 'expert', 'description': 'Transmission des règles de sécurité et d\'usage des machines.', 'issuing_structure': 'La BRICC / Miete'},
            {'name': 'Gestionnaire de Matériauthèque', 'level': 'intermediate', 'description': 'Tri et valorisation des chutes de bois et matériaux.', 'issuing_structure': 'La BRICC / Miete'},

            # Atelier Soudé (Réparation électronique)
            {'name': 'Expert en Soudure', 'level': 'expert', 'description': 'Maîtrise des techniques de soudure électronique complexe.', 'issuing_structure': 'Atelier Soudé'},
            {'name': 'Diagnostiqueur Electronique', 'level': 'intermediate', 'description': 'Identification de pannes sur des circuits imprimés.', 'issuing_structure': 'Atelier Soudé'},
            {'name': 'Sauveur d\'Appareils', 'level': 'beginner', 'description': 'Premiers gestes de réparation pour éviter le gaspillage.', 'issuing_structure': 'Atelier Soudé'},
            {'name': 'Formateur Anti-Obsolescence', 'level': 'expert', 'description': 'Éducation aux enjeux de la durabilité technologique.', 'issuing_structure': 'Atelier Soudé'},
            {'name': 'Démonteur Méthodique', 'level': 'beginner', 'description': 'Ouverture propre et tri des composants d\'un appareil.', 'issuing_structure': 'Atelier Soudé'},

            # Ecole Nationale de Musique (ENM)
            {'name': 'Musicien Hors-les-murs', 'level': 'intermediate', 'description': 'Performance musicale dans l\'espace public.', 'issuing_structure': 'Ecole Nationale de Musique'},
            {'name': 'Eveilleur Musical', 'level': 'beginner', 'description': 'Initiation des enfants aux sons et rythmes.', 'issuing_structure': 'Ecole Nationale de Musique'},
            {'name': 'Pratique Orchestrale', 'level': 'intermediate', 'description': 'Capacité à s\'insérer dans un ensemble symphonique ou jazz.', 'issuing_structure': 'Ecole Nationale de Musique'},
            {'name': 'Compositeur Collectif', 'level': 'expert', 'description': 'Création de morceaux de musique en groupe.', 'issuing_structure': 'Ecole Nationale de Musique'},
            {'name': 'Percussionniste de Rue', 'level': 'beginner', 'description': 'Maîtrise des rythmes de base pour défilés.', 'issuing_structure': 'Ecole Nationale de Musique'},

            # KILT (Low Tech)
            {'name': 'Constructeur de Four Solaire', 'level': 'intermediate', 'description': 'Fabrication d\'un système de cuisson solaire autonome.', 'issuing_structure': 'KILT (Low Tech)'},
            {'name': 'Concepteur de Low-Tech', 'level': 'expert', 'description': 'Design de solutions techniques simples et durables.', 'issuing_structure': 'KILT (Low Tech)'},
            {'name': 'Bidouilleur Économe', 'level': 'beginner', 'description': 'Utilisation de ressources locales pour réparer le quotidien.', 'issuing_structure': 'KILT (Low Tech)'},
            {'name': 'Documentaliste du Faire', 'level': 'intermediate', 'description': 'Rédaction de tutoriels pour partager des solutions techniques.', 'issuing_structure': 'KILT (Low Tech)'},
            {'name': 'Ambassadeur de la Sobriété', 'level': 'beginner', 'description': 'Sensibilisation aux modes de vie résilients.', 'issuing_structure': 'KILT (Low Tech)'},

            # La Myne (Communs et écologie)
            {'name': 'Expérimentateur d\'Écologie', 'level': 'intermediate', 'description': 'Mise en place de protocoles de test environnementaux.', 'issuing_structure': 'La Myne'},
            {'name': 'Documentariste de Communs', 'level': 'intermediate', 'description': 'Enregistrement et partage de l\'histoire d\'un commun.', 'issuing_structure': 'La Myne'},
            {'name': 'Bidouilleur Éthique', 'level': 'beginner', 'description': 'Usage critique et détournement positif des technologies.', 'issuing_structure': 'La Myne'},
            {'name': 'Facilitateur de Recherche Ouverte', 'level': 'expert', 'description': 'Coordination de projets de recherche citoyenne.', 'issuing_structure': 'La Myne'},
            {'name': 'Curateur de Connaissances', 'level': 'expert', 'description': 'Organisation et maintenance des savoirs partagés.', 'issuing_structure': 'La Myne'},

            # Le Zola (Cinéma)
            {'name': 'Critique de Cinéma Scientifique', 'level': 'intermediate', 'description': 'Analyse des thématiques sciences au cinéma.', 'issuing_structure': 'Le Zola'},
            {'name': 'Organisateur de Ciné-Débat', 'level': 'expert', 'description': 'Conception de soirées thématiques autour d\'un film.', 'issuing_structure': 'Le Zola'},
            {'name': 'Projectionniste Bénévole', 'level': 'intermediate', 'description': 'Aide technique à la diffusion de films.', 'issuing_structure': 'Le Zola'},
            {'name': 'Accueillant Public', 'level': 'beginner', 'description': 'Gestion de la billetterie et accueil chaleureux.', 'issuing_structure': 'Le Zola'},
            {'name': 'Programmateur Jeune Public', 'level': 'expert', 'description': 'Sélection de films adaptés aux enfants et écoles.', 'issuing_structure': 'Le Zola'},

            # Maison du Citoyen (Vie associative)
            {'name': 'Accompagnateur de Projet', 'level': 'expert', 'description': 'Soutien méthodologique aux porteurs de projets locaux.', 'issuing_structure': 'Maison du Citoyen'},
            {'name': 'Veilleur de Solidarité', 'level': 'beginner', 'description': 'Identification des besoins et fragilités dans le quartier.', 'issuing_structure': 'Maison du Citoyen'},
            {'name': 'Animateur de Quartier', 'level': 'intermediate', 'description': 'Organisation d\'événements de proximité.', 'issuing_structure': 'Maison du Citoyen'},
            {'name': 'Facilitateur d\'Entraide', 'level': 'beginner', 'description': 'Mise en relation de citoyens pour du troc de services.', 'issuing_structure': 'Maison du Citoyen'},
            {'name': 'Coordonnateur de Bénévoles', 'level': 'intermediate', 'description': 'Gestion et animation de l\'équipe de bénévoles.', 'issuing_structure': 'Maison du Citoyen'},

            # Université Populaire (Savoir pour tous)
            {'name': 'Conférencier Populaire', 'level': 'expert', 'description': 'Capacité à transmettre un savoir complexe simplement.', 'issuing_structure': 'Université Populaire'},
            {'name': 'Apprenant Assidu', 'level': 'beginner', 'description': 'Participation régulière aux cycles de formation.', 'issuing_structure': 'Université Populaire'},
            {'name': 'Facilitateur de Savoirs', 'level': 'intermediate', 'description': 'Aide à la compréhension et à l\'échange entre apprenants.', 'issuing_structure': 'Université Populaire'},
            {'name': 'Organisateur de Rencontres', 'level': 'intermediate', 'description': 'Mise en place logistique de conférences débats.', 'issuing_structure': 'Université Populaire'},
            {'name': 'Passeur de Culture', 'level': 'beginner', 'description': 'Diffusion des opportunités culturelles du territoire.', 'issuing_structure': 'Université Populaire'},
        ]

        # Create a dictionary to easily look up structures by name
        structure_dict = {structure.name: structure for structure in structures}

        for data in badge_data:
            issuing_structure = structure_dict.get(data['issuing_structure'])
            if issuing_structure:
                badge, created = Badge.objects.get_or_create(
                    name=data['name'],
                    issuing_structure=issuing_structure,
                    defaults={
                        'level': data['level'],
                        'description': data['description']
                    }
                )

                # Add an icon image if available and not already set, and --img argument is provided
                if (created or not badge.icon) and self.load_images and not settings.PICTURES["USE_PLACEHOLDERS"]:
                    if self.badge_images:
                        # Get a random image from the available badge images
                        image_path = random.choice(self.badge_images)
                        with open(image_path, 'rb') as f:
                            badge.icon.save(
                                os.path.basename(image_path),
                                File(f),
                                save=True
                            )
                        self.stdout.write(f"Added icon {os.path.basename(image_path)} to {badge.name}")

                # Add some valid structures
                valid_structures = random.sample(structures, random.randint(1, 3))
                for structure in valid_structures:
                    badge.valid_structures.add(structure)

                # Add some holders with realistic dates based on badge level
                holders = random.sample(users, random.randint(1, len(users)))

                # Define a timeline based on badge level
                now = timezone.now()
                if data['level'] == 'beginner':
                    # Beginner badges were assigned 2-3 years ago
                    start_date = now - timedelta(days=365*3)
                    end_date = now - timedelta(days=365*2)
                elif data['level'] == 'intermediate':
                    # Intermediate badges were assigned 1-2 years ago
                    start_date = now - timedelta(days=365*2)
                    end_date = now - timedelta(days=365)
                else:  # expert
                    # Expert badges were assigned within the last year
                    start_date = now - timedelta(days=365)
                    end_date = now

                for user in holders:
                    # Generate a random date within the appropriate range for this badge level
                    days_range = (end_date - start_date).days
                    random_days = random.randint(0, days_range)
                    assignment_date = start_date + timedelta(days=random_days)

                    # Use the add_holder method instead of direct many-to-many
                    # Create a random assigner from the users
                    assigner = random.choice(users) if random.random() > 0.3 else None

                    # Create the assignment with the specific date
                    assignment = badge.add_holder(user, assigned_by=assigner, notes=f"Assigned during database population")

                    # Update the assigned_date field
                    assignment.assigned_date = assignment_date
                    assignment.save()

                    self.stdout.write(f"Assigned {badge.name} to {user.username} on {assignment_date.strftime('%Y-%m-%d')}")

                # Add endorsements for this badge from some structures
                endorsing_structures = random.sample(valid_structures, random.randint(1, len(valid_structures)))
                for structure in endorsing_structures:
                    # Endorsements happen after badge creation but before most assignments
                    endorsement_date = start_date - timedelta(days=random.randint(30, 180))

                    # Create the endorsement
                    endorsement = BadgeEndorsement.objects.create(
                        badge=badge,
                        structure=structure,
                        endorsed_by=random.choice(users) if random.random() > 0.3 else None,
                        endorsed_date=endorsement_date,
                        notes=f"Endorsed during database population"
                    )

                    self.stdout.write(f"Endorsed {badge.name} by {structure.name} on {endorsement_date.strftime('%Y-%m-%d')}")

                badges.append(badge)

        return badges

    def connect_users_to_structures(self, users, structures):
        """
        Connect users to structures
        """
        for user in users:
            # Connect each user to 2-4 random structures
            user_structures = random.sample(structures, random.randint(2, 4))
            for structure in user_structures:
                structure.users.add(user)
