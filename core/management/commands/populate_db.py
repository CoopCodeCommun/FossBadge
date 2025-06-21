import random
import os
from pathlib import Path
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.core.files.base import ContentFile
from django.core.files import File
from django.conf import settings
from django.utils import timezone
from datetime import timedelta, datetime
from core.models import Structure, Badge, UserProfile, BadgeEndorsement

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
            }
        ]

        for data in user_data:
            user, created = User.objects.get_or_create(
                username=data['username'],
                defaults={
                    'first_name': data['first_name'],
                    'last_name': data['last_name'],
                    'email': data['email'],
                }
            )

            if created:
                user.set_password(data['password'])
                user.save()

                # Create user profile
                profile = UserProfile.objects.create(
                    user=user,
                    address=data['address']
                )
            else:
                # Get existing profile
                profile, _ = UserProfile.objects.get_or_create(user=user, defaults={'address': data['address']})

            # Add an avatar image if available and not already set, and --img argument is provided
            if self.profile_images and (created or not profile.avatar) and self.load_images and not settings.PICTURES["USE_PLACEHOLDERS"]:
                # Get a random image from the available profile images
                image_path = random.choice(self.profile_images)
                with open(image_path, 'rb') as f:
                    profile.avatar.save(
                        os.path.basename(image_path),
                        File(f),
                        save=True
                    )
                self.stdout.write(f"Added avatar {os.path.basename(image_path)} to {user.username}")

            users.append(user)

        return users

    def create_structures(self):
        """
        Create about ten different structures for development
        """
        structures = []
        structure_data = [
            {
                'name': 'Structure Python',
                'type': 'association',
                'address': '456 Avenue de l\'Innovation, 75002 Paris',
                'siret': '123 456 789 00012',
                'description': 'La Structure Python est dédiée à la promotion et au développement du langage de programmation Python. Nous organisons des ateliers, des conférences et des formations pour tous les niveaux, du débutant à l\'expert. Notre mission est de créer une communauté inclusive et collaborative autour de Python et de ses applications.',
                'referent_last_name': 'Dubois',
                'referent_first_name': 'Claire',
                'referent_position': 'Présidente',
                'latitude': 48.8566,
                'longitude': 2.3522
            },
            {
                'name': 'Club Web',
                'type': 'association',
                'address': '789 Rue du Code, 69001 Lyon',
                'siret': '987 654 321 00034',
                'description': 'Le Club Web est un groupe de passionnés du développement web. Nous partageons nos connaissances et expériences sur les technologies web modernes.',
                'referent_last_name': 'Martin',
                'referent_first_name': 'Thomas',
                'referent_position': 'Secrétaire',
                'latitude': 45.7640,
                'longitude': 4.8357
            },
            {
                'name': 'Tech Company',
                'type': 'company',
                'address': '101 Boulevard des Startups, 33000 Bordeaux',
                'siret': '456 789 123 00056',
                'description': 'Tech Company est une entreprise innovante spécialisée dans le développement de solutions technologiques pour les entreprises et les particuliers.',
                'referent_last_name': 'Petit',
                'referent_first_name': 'Sophie',
                'referent_position': 'CEO',
                'latitude': 44.8378,
                'longitude': -0.5792
            },
            {
                'name': 'Coding School',
                'type': 'school',
                'address': '202 Avenue de l\'Éducation, 59000 Lille',
                'siret': '789 123 456 00078',
                'description': 'Coding School est une école de programmation qui propose des formations intensives pour apprendre à coder et devenir développeur web ou mobile.',
                'referent_last_name': 'Leroy',
                'referent_first_name': 'Marc',
                'referent_position': 'Directeur',
                'latitude': 50.6292,
                'longitude': 3.0573
            },
            {
                'name': 'Dev Studio',
                'type': 'company',
                'address': '303 Rue des Développeurs, 44000 Nantes',
                'siret': '321 654 987 00090',
                'description': 'Dev Studio est un studio de développement spécialisé dans la création d\'applications web et mobiles sur mesure pour les entreprises.',
                'referent_last_name': 'Moreau',
                'referent_first_name': 'Julie',
                'referent_position': 'CTO',
                'latitude': 47.2184,
                'longitude': -1.5536
            },
            {
                'name': 'Data Science Association',
                'type': 'association',
                'address': '404 Boulevard des Données, 67000 Strasbourg',
                'siret': '654 987 321 00012',
                'description': 'L\'association Data Science promeut l\'utilisation des données et de l\'intelligence artificielle pour résoudre des problèmes complexes.',
                'referent_last_name': 'Fournier',
                'referent_first_name': 'Alexandre',
                'referent_position': 'Président',
                'latitude': 48.5734,
                'longitude': 7.7521
            },
            {
                'name': 'Mobile App Factory',
                'type': 'company',
                'address': '505 Avenue des Applications, 13000 Marseille',
                'siret': '987 321 654 00034',
                'description': 'Mobile App Factory est une entreprise spécialisée dans le développement d\'applications mobiles pour iOS et Android.',
                'referent_last_name': 'Girard',
                'referent_first_name': 'Émilie',
                'referent_position': 'Directrice',
                'latitude': 43.2965,
                'longitude': 5.3698
            },
            {
                'name': 'Open Source Community',
                'type': 'association',
                'address': '606 Rue du Libre, 31000 Toulouse',
                'siret': '123 789 456 00056',
                'description': 'Open Source Community est une communauté dédiée à la promotion et au développement de logiciels libres et open source.',
                'referent_last_name': 'Rousseau',
                'referent_first_name': 'Nicolas',
                'referent_position': 'Coordinateur',
                'latitude': 43.6047,
                'longitude': 1.4442
            },
            {
                'name': 'Digital Learning Institute',
                'type': 'school',
                'address': '707 Boulevard de l\'Apprentissage, 06000 Nice',
                'siret': '456 123 789 00078',
                'description': 'Digital Learning Institute est un centre de formation spécialisé dans les compétences numériques et la transformation digitale.',
                'referent_last_name': 'Blanc',
                'referent_first_name': 'Isabelle',
                'referent_position': 'Directrice pédagogique',
                'latitude': 43.7102,
                'longitude': 7.2620
            },
            {
                'name': 'Blockchain Consortium',
                'type': 'company',
                'address': '808 Avenue de la Blockchain, 38000 Grenoble',
                'siret': '789 456 123 00090',
                'description': 'Blockchain Consortium est un groupe d\'entreprises travaillant ensemble pour développer et promouvoir les technologies blockchain.',
                'referent_last_name': 'Mercier',
                'referent_first_name': 'Antoine',
                'referent_position': 'Président',
                'latitude': 45.1885,
                'longitude': 5.7245
            }
        ]

        for data in structure_data:
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
                    'longitude': data['longitude']
                }
            )

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
        Create some badges for development
        """
        badges = []
        badge_data = [
            {
                'name': 'Python Débutant',
                'level': 'beginner',
                'description': 'Ce badge certifie une connaissance de base en programmation Python. Il atteste de la capacité à écrire des scripts simples, à comprendre les concepts fondamentaux comme les variables, les boucles et les conditions.',
                'issuing_structure': 'Structure Python'
            },
            {
                'name': 'Python Intermédiaire',
                'level': 'intermediate',
                'description': 'Ce badge certifie une connaissance intermédiaire en programmation Python. Il atteste de la capacité à créer des applications plus complexes, à utiliser des bibliothèques externes et à comprendre les concepts de programmation orientée objet.',
                'issuing_structure': 'Structure Python'
            },
            {
                'name': 'Python Expert',
                'level': 'expert',
                'description': 'Ce badge certifie une expertise en programmation Python. Il atteste de la capacité à concevoir, développer et maintenir des applications complexes en utilisant Python et ses frameworks associés. Les compétences validées incluent la maîtrise des concepts avancés comme la programmation orientée objet, la gestion des exceptions, les générateurs, et l\'utilisation de bibliothèques comme Django, Flask, Pandas et NumPy.',
                'issuing_structure': 'Structure Python'
            },
            {
                'name': 'HTML',
                'level': 'expert',
                'description': 'Ce badge certifie une expertise en HTML. Il atteste de la capacité à créer des pages web sémantiques, accessibles et conformes aux standards du W3C.',
                'issuing_structure': 'Club Web'
            },
            {
                'name': 'CSS',
                'level': 'intermediate',
                'description': 'Ce badge certifie une connaissance intermédiaire en CSS. Il atteste de la capacité à créer des mises en page responsives, à utiliser Flexbox et Grid, et à appliquer des animations et transitions.',
                'issuing_structure': 'Club Web'
            },
            {
                'name': 'JavaScript',
                'level': 'beginner',
                'description': 'Ce badge certifie une connaissance de base en JavaScript. Il atteste de la capacité à manipuler le DOM, à gérer les événements et à créer des interactions simples.',
                'issuing_structure': 'Tech Company'
            },
            {
                'name': 'React',
                'level': 'intermediate',
                'description': 'Ce badge certifie une connaissance intermédiaire en React. Il atteste de la capacité à créer des applications web avec React, à utiliser les hooks et à gérer l\'état avec Redux.',
                'issuing_structure': 'Dev Studio'
            },
            {
                'name': 'Data Analysis',
                'level': 'expert',
                'description': 'Ce badge certifie une expertise en analyse de données. Il atteste de la capacité à collecter, nettoyer, analyser et visualiser des données à l\'aide de bibliothèques comme Pandas, NumPy et Matplotlib.',
                'issuing_structure': 'Data Science Association'
            },
            {
                'name': 'Mobile Development',
                'level': 'intermediate',
                'description': 'Ce badge certifie une connaissance intermédiaire en développement mobile. Il atteste de la capacité à créer des applications mobiles pour iOS et Android à l\'aide de frameworks comme React Native ou Flutter.',
                'issuing_structure': 'Mobile App Factory'
            },
            {
                'name': 'Open Source Contribution',
                'level': 'beginner',
                'description': 'Ce badge certifie une connaissance de base en contribution à des projets open source. Il atteste de la capacité à comprendre le fonctionnement de Git, à créer des pull requests et à participer à la communauté open source.',
                'issuing_structure': 'Open Source Community'
            },
            {
                'name': 'Digital Marketing',
                'level': 'intermediate',
                'description': 'Ce badge certifie une connaissance intermédiaire en marketing digital. Il atteste de la capacité à créer et gérer des campagnes publicitaires en ligne, à analyser les performances et à optimiser les conversions.',
                'issuing_structure': 'Digital Learning Institute'
            },
            {
                'name': 'Blockchain',
                'level': 'expert',
                'description': 'Ce badge certifie une expertise en technologies blockchain. Il atteste de la capacité à concevoir, développer et déployer des applications décentralisées (DApps) et des contrats intelligents.',
                'issuing_structure': 'Blockchain Consortium'
            }
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
