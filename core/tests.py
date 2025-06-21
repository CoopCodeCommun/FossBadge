from django.test import TestCase
from django.urls import reverse
from django.test import Client
from django.core.files.uploadedfile import SimpleUploadedFile
import os
from pathlib import Path
from bs4 import BeautifulSoup

# Create your tests here.
class HomePageTest(TestCase):
    """Test the home page view"""

    def test_home_page_loads_correctly(self):
        """Test that the home page loads correctly with a 200 status code"""
        response = self.client.get(reverse('core:home-list'))
        self.assertEqual(response.status_code, 200)

    def test_home_page_uses_correct_template(self):
        """Test that the home page uses the correct template"""
        response = self.client.get(reverse('core:home-list'))
        self.assertTemplateUsed(response, 'core/home/index.html')
        self.assertTemplateUsed(response, 'base.html')

    def test_home_page_contains_static_files(self):
        """Test that the home page contains references to all required static files"""
        response = self.client.get(reverse('core:home-list'))
        content = response.content.decode('utf-8')

        # Check for Bootstrap CSS
        self.assertIn('bootstrap.min.css', content)

        # Check for Bootstrap JS
        self.assertIn('bootstrap.bundle.min.js', content)

        # Check for HTMX
        self.assertIn('htmx.min.js', content)

        # Check for custom CSS
        self.assertIn('custom.css', content)


class UserProfileTest(TestCase):
    """Test the user profile page view"""

    def setUp(self):
        """Set up test data"""
        from django.contrib.auth.models import User
        from .models import UserProfile, Structure, Badge
        from django.utils import timezone
        from datetime import timedelta

        # Create a test user with a profile
        self.user_with_profile = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword',
            first_name='Test',
            last_name='User'
        )

        # Create a user profile
        self.profile = UserProfile.objects.create(
            user=self.user_with_profile,
            address='123 Test Street'
        )

        # Create a test user without a profile
        self.user_without_profile = User.objects.create_user(
            username='testuserwithnoprofile',
            email='testnoprofile@example.com',
            password='testpassword',
            first_name='TestNo',
            last_name='Profile'
        )

        # Create a test structure
        self.structure = Structure.objects.create(
            name="Test Structure",
            type="association",
            address="123 Test Street",
            description="Test Description",
            referent_last_name="Test",
            referent_first_name="User",
            referent_position="Tester"
        )

        # Create a test badge
        self.badge = Badge.objects.create(
            name="Test Badge",
            level="intermediate",
            description="Test Badge Description",
            issuing_structure=self.structure
        )

        # Assign the badge to the user with a specific date
        self.assignment_date = timezone.now() - timedelta(days=30)
        assignment = self.badge.add_holder(self.user_with_profile)
        assignment.assigned_date = self.assignment_date
        assignment.save()

    def test_user_profile_page_loads_correctly(self):
        """Test that the user profile page loads correctly with a 200 status code"""
        response = self.client.get(reverse('core:user-detail', kwargs={'pk': self.user_with_profile.id}))
        self.assertEqual(response.status_code, 200)

    def test_user_profile_page_uses_correct_template(self):
        """Test that the user profile page uses the correct template"""
        response = self.client.get(reverse('core:user-detail', kwargs={'pk': self.user_with_profile.id}))
        self.assertTemplateUsed(response, 'core/users/detail.html')
        self.assertTemplateUsed(response, 'base.html')

    def test_user_profile_page_contains_expected_content(self):
        """Test that the user profile page contains expected content"""
        response = self.client.get(reverse('core:user-detail', kwargs={'pk': self.user_with_profile.id}))
        content = response.content.decode('utf-8')

        # Check for user profile specific content
        self.assertIn('Profil de Test User', content)
        self.assertIn('Informations personnelles', content)
        self.assertIn('Mes badges', content)
        self.assertIn('Mes structures', content)

    def test_user_profile_page_displays_badge_assignment_dates(self):
        """Test that the user profile page displays badge assignment dates correctly"""
        response = self.client.get(reverse('core:user-detail', kwargs={'pk': self.user_with_profile.id}))
        content = response.content.decode('utf-8')

        # Check that the badge is displayed
        self.assertIn('Test Badge', content)

        # Check that the assignment date is displayed in the exact format
        formatted_date = self.assignment_date.strftime('%d/%m/%Y')
        self.assertIn(f'Assigné le {formatted_date}', content)

        # Check that the humanized date is displayed
        self.assertIn('il y a', content.lower())  # "il y a" is the French equivalent of "ago"

    def test_user_without_profile_page_loads_correctly(self):
        """Test that the user profile page loads correctly for a user without a UserProfile"""
        response = self.client.get(reverse('core:user-detail', kwargs={'pk': self.user_without_profile.id}))
        self.assertEqual(response.status_code, 200)

        content = response.content.decode('utf-8')

        # Check for user profile specific content
        self.assertIn('Profil de TestNo Profile', content)
        self.assertIn('Informations personnelles', content)

        # Check that the placeholder image is used
        self.assertIn('https://via.placeholder.com/150', content)

        # Check that the address field is empty
        self.assertIn('<div class="col-md-4 fw-bold">Adresse:</div>', content)
        self.assertIn('<div class="col-md-8"></div>', content)

        # Check that the "no badges" message is displayed
        self.assertIn('Aucun badge n\'est associé à ce profil', content)


class BadgeDetailTest(TestCase):
    """Test the badge detail page view"""

    def setUp(self):
        """Set up test data"""
        from .models import Structure, Badge

        # Create a test structure
        self.structure = Structure.objects.create(
            name="Test Structure",
            type="association",
            address="123 Test Street",
            description="Test Description",
            referent_last_name="Test",
            referent_first_name="User",
            referent_position="Tester"
        )

        # Create a test badge
        self.badge = Badge.objects.create(
            name="Test Badge",
            level="intermediate",
            description="Test Badge Description",
            issuing_structure=self.structure
        )

    def test_badge_detail_page_loads_correctly(self):
        """Test that the badge detail page loads correctly with a 200 status code"""
        response = self.client.get(reverse('core:badge-detail', kwargs={'pk': self.badge.id}))
        self.assertEqual(response.status_code, 200)

    def test_badge_detail_page_uses_correct_template(self):
        """Test that the badge detail page uses the correct template"""
        response = self.client.get(reverse('core:badge-detail', kwargs={'pk': self.badge.id}))
        self.assertTemplateUsed(response, 'core/badges/detail.html')
        self.assertTemplateUsed(response, 'base.html')

    def test_badge_detail_page_contains_expected_content(self):
        """Test that the badge detail page contains expected content"""
        response = self.client.get(reverse('core:badge-detail', kwargs={'pk': self.badge.id}))
        content = response.content.decode('utf-8')

        # Check for badge detail specific content
        self.assertIn(self.badge.name, content)
        self.assertIn('QR Code', content)
        self.assertIn('Structures où ce badge est valable', content)
        self.assertIn('Ce badge est rattaché à d\'autres personnes', content)

    def test_badge_name_change_is_reflected(self):
        """Test that changes to the badge name are reflected in the detail page"""
        # Change the badge name
        new_name = "Modified Badge Name"
        self.badge.name = new_name
        self.badge.save()

        # Check that the new name is displayed
        response = self.client.get(reverse('core:badge-detail', kwargs={'pk': self.badge.id}))
        content = response.content.decode('utf-8')
        self.assertIn(new_name, content)


class StructureDetailTest(TestCase):
    """Test the structure detail page view"""

    def setUp(self):
        """Set up test data"""
        from .models import Structure

        # Create a test structure
        self.structure = Structure.objects.create(
            name="Test Structure",
            type="association",
            address="123 Test Street",
            description="Test Description",
            referent_last_name="Test",
            referent_first_name="User",
            referent_position="Tester"
        )

    def test_structure_detail_page_loads_correctly(self):
        """Test that the structure detail page loads correctly with a 200 status code"""
        response = self.client.get(reverse('core:structure-detail', kwargs={'pk': self.structure.id}))
        self.assertEqual(response.status_code, 200)

    def test_structure_detail_page_uses_correct_template(self):
        """Test that the structure detail page uses the correct template"""
        response = self.client.get(reverse('core:structure-detail', kwargs={'pk': self.structure.id}))
        self.assertTemplateUsed(response, 'core/structures/detail.html')
        self.assertTemplateUsed(response, 'base.html')

    def test_structure_detail_page_contains_expected_content(self):
        """Test that the structure detail page contains expected content"""
        response = self.client.get(reverse('core:structure-detail', kwargs={'pk': self.structure.id}))
        content = response.content.decode('utf-8')

        # Check for structure detail specific content
        self.assertIn(self.structure.name, content)
        self.assertIn('Forger un nouveau badge', content)
        self.assertIn('Badges disponibles', content)
        self.assertIn(self.structure.address, content)
        self.assertIn(self.structure.description, content)

    def test_structure_name_change_is_reflected(self):
        """Test that changes to the structure name are reflected in the detail page"""
        # Change the structure name
        new_name = "Modified Structure Name"
        self.structure.name = new_name
        self.structure.save()

        # Check that the new name is displayed
        response = self.client.get(reverse('core:structure-detail', kwargs={'pk': self.structure.id}))
        content = response.content.decode('utf-8')
        self.assertIn(new_name, content)


class CreateBadgeTest(TestCase):
    """Test the badge creation page view"""

    def setUp(self):
        """Set up test data"""
        from .models import Structure
        from django.core.files.uploadedfile import SimpleUploadedFile
        from pathlib import Path

        # Create a test structure
        self.structure = Structure.objects.create(
            name="Test Structure",
            type="association",
            address="123 Test Street",
            description="Test Description",
            referent_last_name="Test",
            referent_first_name="User",
            referent_position="Tester"
        )

        # Prepare test image for badge icon
        base_dir = Path(__file__).resolve().parent.parent
        badge_image_path = base_dir / 'media' / 'badges' / 'exemples' / 'gp1.png'

        with open(badge_image_path, 'rb') as f:
            self.image_content = f.read()

        self.test_image = SimpleUploadedFile(
            name='test_badge_icon.png',
            content=self.image_content,
            content_type='image/png'
        )

    def test_create_badge_page_loads_correctly(self):
        """Test that the badge creation page loads correctly with a 200 status code"""
        response = self.client.get(reverse('core:create_badge'))
        self.assertEqual(response.status_code, 200)

    def test_create_badge_page_uses_correct_template(self):
        """Test that the badge creation page uses the correct template"""
        response = self.client.get(reverse('core:create_badge'))
        self.assertTemplateUsed(response, 'core/badges/create.html')
        self.assertTemplateUsed(response, 'base.html')

    def test_create_badge_page_contains_expected_content(self):
        """Test that the badge creation page contains expected content"""
        response = self.client.get(reverse('core:create_badge'))
        content = response.content.decode('utf-8')

        # Check for badge creation specific content
        self.assertIn('Forger un nouveau Badge', content)
        self.assertIn('Icône', content)
        self.assertIn('Nom', content)
        self.assertIn('Niveau', content)
        self.assertIn('Description', content)

    def test_create_badge_form_submission(self):
        """Test submitting the badge creation form with valid data"""
        # Prepare form data
        form_data = {
            'name': 'Test Badge Created From Form',
            'level': 'intermediate',
            'description': 'This is a test badge created from the form submission test',
            'issuing_structure': self.structure.id,
        }

        # Create a fresh test image for each test
        test_image = SimpleUploadedFile(
            name='test_badge_icon.png',
            content=self.image_content,
            content_type='image/png'
        )

        # Submit the form
        response = self.client.post(
            reverse('core:create_badge'),
            data={**form_data, 'icon': test_image},
            follow=True  # Follow redirects
        )

        # Check that the form submission was successful (should redirect to badge detail)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/badges/detail.html')

        # Verify the badge was created in the database
        from .models import Badge
        badge = Badge.objects.filter(name='Test Badge Created From Form').first()
        self.assertIsNotNone(badge)
        self.assertEqual(badge.level, 'intermediate')
        self.assertEqual(badge.description, 'This is a test badge created from the form submission test')
        self.assertEqual(badge.issuing_structure, self.structure)

        # Check that the badge appears in the list view
        list_response = self.client.get(reverse('core:badge-list'))
        list_content = list_response.content.decode('utf-8')
        self.assertIn('Test Badge Created From Form', list_content)


class CreateStructureTest(TestCase):
    """Test the structure creation page view"""

    def setUp(self):
        """Set up test data"""
        from pathlib import Path

        # Prepare test image for structure logo
        base_dir = Path(__file__).resolve().parent.parent
        structure_image_path = base_dir / 'media' / 'structures' / 'examples' / 'draw_svg20210805-28561-1nfg07n.svg.png'

        with open(structure_image_path, 'rb') as f:
            self.image_content = f.read()

        self.test_image = SimpleUploadedFile(
            name='test_structure_logo.png',
            content=self.image_content,
            content_type='image/png'
        )

    def test_create_structure_page_loads_correctly(self):
        """Test that the structure creation page loads correctly with a 200 status code"""
        response = self.client.get(reverse('core:create_association'))
        self.assertEqual(response.status_code, 200)

    def test_create_structure_page_uses_correct_template(self):
        """Test that the structure creation page uses the correct template"""
        response = self.client.get(reverse('core:create_association'))
        self.assertTemplateUsed(response, 'core/structures/create.html')
        self.assertTemplateUsed(response, 'base.html')

    def test_create_structure_page_contains_expected_content(self):
        """Test that the structure creation page contains expected content"""
        response = self.client.get(reverse('core:create_association'))
        content = response.content.decode('utf-8')

        # Check for structure creation specific content
        self.assertIn('Créer une Structure / Entreprise', content)
        self.assertIn('Informations générales', content)
        self.assertIn('Personne référente', content)
        self.assertIn('Nom', content)
        self.assertIn('SIREN/SIRET', content)

    def test_create_structure_form_submission(self):
        """Test submitting the structure creation form with valid data"""
        # Prepare form data
        form_data = {
            'name': 'Test Structure Created From Form',
            'type': 'association',
            'address': '123 Test Street, Test City',
            'siret': '123 456 789 00012',
            'description': 'This is a test structure created from the form submission test',
            'referent_last_name': 'Test',
            'referent_first_name': 'User',
            'referent_position': 'Tester',
            'latitude': 48.8566,
            'longitude': 2.3522,
        }

        # Create a fresh test image for each test
        test_image = SimpleUploadedFile(
            name='test_structure_logo.png',
            content=self.image_content,
            content_type='image/png'
        )

        # Submit the form
        response = self.client.post(
            reverse('core:create_association'),
            data={**form_data, 'logo': test_image},
            follow=True  # Follow redirects
        )

        # Check that the form submission was successful (should redirect to structure detail)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/structures/detail.html')

        # Verify the structure was created in the database
        from .models import Structure
        structure = Structure.objects.filter(name='Test Structure Created From Form').first()
        self.assertIsNotNone(structure)
        self.assertEqual(structure.type, 'association')
        self.assertEqual(structure.address, '123 Test Street, Test City')
        self.assertEqual(structure.siret, '123 456 789 00012')
        self.assertEqual(structure.description, 'This is a test structure created from the form submission test')
        self.assertEqual(structure.referent_last_name, 'Test')
        self.assertEqual(structure.referent_first_name, 'User')
        self.assertEqual(structure.referent_position, 'Tester')
        self.assertEqual(structure.latitude, 48.8566)
        self.assertEqual(structure.longitude, 2.3522)

        # Check that the structure appears in the list view
        list_response = self.client.get(reverse('core:structure-list'))
        list_content = list_response.content.decode('utf-8')
        self.assertIn('Test Structure Created From Form', list_content)


class ImageDisplayTest(TestCase):
    """Test that images are displayed correctly using django-pictures"""

    def setUp(self):
        """Set up test data with images"""
        from .models import Structure, Badge, UserProfile
        from django.contrib.auth.models import User

        # Get test image paths
        base_dir = Path(__file__).resolve().parent.parent
        structure_image_path = base_dir / 'media' / 'structures' / 'examples' / 'draw_svg20210805-28561-1nfg07n.svg.png'
        badge_image_path = base_dir / 'media' / 'badges' / 'exemples' / 'gp1.png'

        # Create test structure with image
        with open(structure_image_path, 'rb') as f:
            image_content = f.read()

        self.structure = Structure.objects.create(
            name="Test Structure with Image",
            type="association",
            address="123 Test Street",
            description="Test Description",
            referent_last_name="Test",
            referent_first_name="User",
            referent_position="Tester"
        )
        self.structure.logo.save('test_structure_logo.png', SimpleUploadedFile('test_structure_logo.png', image_content))

        # Create test badge with image
        with open(badge_image_path, 'rb') as f:
            image_content = f.read()

        self.badge = Badge.objects.create(
            name="Test Badge with Image",
            level="intermediate",
            description="Test Badge Description",
            issuing_structure=self.structure
        )
        self.badge.icon.save('test_badge_icon.png', SimpleUploadedFile('test_badge_icon.png', image_content))

        # Create test user and profile
        self.user = User.objects.create_user(
            username='testimageuser',
            email='testimageuser@example.com',
            password='testpassword',
            first_name='Test',
            last_name='Image User'
        )

        self.profile = UserProfile.objects.create(
            user=self.user,
            address='123 Test Street'
        )

    def test_structure_detail_page_displays_image(self):
        """Test that the structure detail page displays the structure logo using django-pictures"""
        response = self.client.get(reverse('core:structure-detail', kwargs={'pk': self.structure.id}))
        content = response.content.decode('utf-8')

        # Check that the image is displayed using django-pictures (rendered HTML)
        self.assertIn('<picture>', content)
        self.assertIn('<source type="image/webp"', content)
        self.assertIn('srcset=', content)
        self.assertIn('sizes=', content)
        self.assertIn('/media/structures/logos/', content)

    def test_badge_detail_page_displays_image(self):
        """Test that the badge detail page displays the badge icon using django-pictures"""
        response = self.client.get(reverse('core:badge-detail', kwargs={'pk': self.badge.id}))
        content = response.content.decode('utf-8')

        # Check that the image is displayed using django-pictures (rendered HTML)
        self.assertIn('<picture', content)
        self.assertIn('<source type="image/webp"', content)
        self.assertIn('srcset=', content)
        self.assertIn('sizes=', content)
        self.assertIn('/media/badges/icons/', content)

    def test_structure_list_page_displays_images(self):
        """Test that the structure list page displays structure logos using django-pictures"""
        response = self.client.get(reverse('core:structure-list'))
        content = response.content.decode('utf-8')

        # Check that the image is displayed using django-pictures (rendered HTML)
        self.assertIn('<picture>', content)
        self.assertIn('<source type="image/webp"', content)
        self.assertIn('srcset=', content)
        self.assertIn('sizes=', content)
        self.assertIn('/media/structures/logos/', content)

    def test_badge_list_page_displays_images(self):
        """Test that the badge list page displays badge icons using django-pictures"""
        response = self.client.get(reverse('core:badge-list'))
        content = response.content.decode('utf-8')

        # Check that the image is displayed using django-pictures (rendered HTML)
        self.assertIn('<picture>', content)
        self.assertIn('<source type="image/webp"', content)
        self.assertIn('srcset=', content)
        self.assertIn('sizes=', content)
        self.assertIn('/media/badges/icons/', content)


class BadgeSearchFilterTest(TestCase):
    """Test the badge search and filter functionality"""

    def setUp(self):
        """Set up test data"""
        from .models import Structure, Badge

        # Create test structures
        self.structure1 = Structure.objects.create(
            name="Python Structure",
            type="association",
            address="123 Python Street",
            description="Python Structure Description",
            referent_last_name="Python",
            referent_first_name="Developer",
            referent_position="Lead"
        )

        self.structure2 = Structure.objects.create(
            name="Django Association",
            type="association",
            address="456 Django Avenue",
            description="Django Association Description",
            referent_last_name="Django",
            referent_first_name="Developer",
            referent_position="Lead"
        )

        # Create test badges with different levels and structures
        self.badge1 = Badge.objects.create(
            name="Python Basics",
            level="beginner",
            description="Learn Python basics",
            issuing_structure=self.structure1
        )

        self.badge2 = Badge.objects.create(
            name="Django Framework",
            level="intermediate",
            description="Learn Django web framework",
            issuing_structure=self.structure2
        )

        self.badge3 = Badge.objects.create(
            name="Advanced Python",
            level="expert",
            description="Advanced Python concepts",
            issuing_structure=self.structure1
        )

        self.badge4 = Badge.objects.create(
            name="Django REST Framework",
            level="expert",
            description="Build APIs with Django REST Framework",
            issuing_structure=self.structure2
        )

    def test_badge_search_by_name(self):
        """Test searching badges by name"""
        response = self.client.get(reverse('core:badge-list') + '?search=Python')
        self.assertEqual(response.status_code, 200)

        # Parse the HTML content
        soup = BeautifulSoup(response.content, 'html.parser')
        badge_cards = soup.select('.badge-grid .card')

        # Check that only Python badges are returned
        self.assertEqual(len(badge_cards), 2)
        badge_names = [card.select_one('.card-title').text.strip() for card in badge_cards]
        self.assertIn('Python Basics', badge_names)
        self.assertIn('Advanced Python', badge_names)
        self.assertNotIn('Django Framework', badge_names)
        self.assertNotIn('Django REST Framework', badge_names)

    def test_badge_search_by_description(self):
        """Test searching badges by description"""
        response = self.client.get(reverse('core:badge-list') + '?search=API')
        self.assertEqual(response.status_code, 200)

        # Parse the HTML content
        soup = BeautifulSoup(response.content, 'html.parser')
        badge_cards = soup.select('.badge-grid .card')

        # Check that only badges with 'API' in description are returned
        self.assertEqual(len(badge_cards), 1)
        badge_names = [card.select_one('.card-title').text.strip() for card in badge_cards]
        self.assertIn('Django REST Framework', badge_names)

    def test_badge_search_by_structure(self):
        """Test searching badges by structure name"""
        response = self.client.get(reverse('core:badge-list') + '?search=Django')
        self.assertEqual(response.status_code, 200)

        # Parse the HTML content
        soup = BeautifulSoup(response.content, 'html.parser')
        badge_cards = soup.select('.badge-grid .card')

        # Check that only badges from Django structure are returned
        self.assertEqual(len(badge_cards), 2)
        badge_names = [card.select_one('.card-title').text.strip() for card in badge_cards]
        self.assertIn('Django Framework', badge_names)
        self.assertIn('Django REST Framework', badge_names)
        self.assertNotIn('Python Basics', badge_names)
        self.assertNotIn('Advanced Python', badge_names)

    def test_badge_filter_by_level(self):
        """Test filtering badges by level"""
        # Test filtering by beginner level
        response = self.client.get(reverse('core:badge-list') + '?level=beginner')
        self.assertEqual(response.status_code, 200)

        # Parse the HTML content
        soup = BeautifulSoup(response.content, 'html.parser')
        badge_cards = soup.select('.badge-grid .card')

        # Check that only beginner badges are returned
        self.assertEqual(len(badge_cards), 1)
        badge_names = [card.select_one('.card-title').text.strip() for card in badge_cards]
        self.assertIn('Python Basics', badge_names)

        # Test filtering by expert level
        response = self.client.get(reverse('core:badge-list') + '?level=expert')
        self.assertEqual(response.status_code, 200)

        # Parse the HTML content
        soup = BeautifulSoup(response.content, 'html.parser')
        badge_cards = soup.select('.badge-grid .card')

        # Check that only expert badges are returned
        self.assertEqual(len(badge_cards), 2)
        badge_names = [card.select_one('.card-title').text.strip() for card in badge_cards]
        self.assertIn('Advanced Python', badge_names)
        self.assertIn('Django REST Framework', badge_names)

        # Test filtering by multiple levels
        response = self.client.get(reverse('core:badge-list') + '?level=beginner&level=intermediate')
        self.assertEqual(response.status_code, 200)

        # Parse the HTML content
        soup = BeautifulSoup(response.content, 'html.parser')
        badge_cards = soup.select('.badge-grid .card')

        # Check that beginner and intermediate badges are returned
        self.assertEqual(len(badge_cards), 2)
        badge_names = [card.select_one('.card-title').text.strip() for card in badge_cards]
        self.assertIn('Python Basics', badge_names)
        self.assertIn('Django Framework', badge_names)

    def test_badge_filter_by_structure(self):
        """Test filtering badges by structure"""
        response = self.client.get(reverse('core:badge-list') + f'?structure={self.structure1.id}')
        self.assertEqual(response.status_code, 200)

        # Parse the HTML content
        soup = BeautifulSoup(response.content, 'html.parser')
        badge_cards = soup.select('.badge-grid .card')

        # Check that only badges from structure1 are returned
        self.assertEqual(len(badge_cards), 2)
        badge_names = [card.select_one('.card-title').text.strip() for card in badge_cards]
        self.assertIn('Python Basics', badge_names)
        self.assertIn('Advanced Python', badge_names)
        self.assertNotIn('Django Framework', badge_names)
        self.assertNotIn('Django REST Framework', badge_names)

    def test_badge_combined_search_and_filter(self):
        """Test combining search and filter"""
        response = self.client.get(reverse('core:badge-list') + f'?search=Python&level=expert')
        self.assertEqual(response.status_code, 200)

        # Parse the HTML content
        soup = BeautifulSoup(response.content, 'html.parser')
        badge_cards = soup.select('.badge-grid .card')

        # Check that only expert Python badges are returned
        self.assertEqual(len(badge_cards), 1)
        badge_names = [card.select_one('.card-title').text.strip() for card in badge_cards]
        self.assertIn('Advanced Python', badge_names)
        self.assertNotIn('Python Basics', badge_names)
        self.assertNotIn('Django Framework', badge_names)
        self.assertNotIn('Django REST Framework', badge_names)

    def test_htmx_request_returns_partial_template(self):
        """Test that HTMX requests return the partial template"""
        # Make a regular request
        regular_response = self.client.get(reverse('core:badge-list'))
        self.assertEqual(regular_response.status_code, 200)
        self.assertTemplateUsed(regular_response, 'core/badges/list.html')
        self.assertTemplateUsed(regular_response, 'base.html')

        # Make an HTMX request
        htmx_response = self.client.get(
            reverse('core:badge-list'),
            HTTP_HX_REQUEST='true'
        )
        self.assertEqual(htmx_response.status_code, 200)
        self.assertTemplateUsed(htmx_response, 'core/badges/partials/badge_list.html')
        self.assertNotIn('base.html', [t.name for t in htmx_response.templates])

        # Check that the HTMX response contains only the badge list
        htmx_content = htmx_response.content.decode('utf-8')
        self.assertIn('<div class="badge-grid">', htmx_content)
        self.assertNotIn('<div class="col-md-3 mb-4">', htmx_content)  # Filter sidebar should not be included

    def test_no_duplicate_data_in_response(self):
        """Test that there are no duplicate badges in the response"""
        response = self.client.get(reverse('core:badge-list'))
        self.assertEqual(response.status_code, 200)

        # Parse the HTML content
        soup = BeautifulSoup(response.content, 'html.parser')
        badge_cards = soup.select('.badge-grid .card')

        # Extract badge names
        badge_names = [card.select_one('.card-title').text.strip() for card in badge_cards]

        # Check for duplicates by comparing the length of the list with the length of the set
        self.assertEqual(len(badge_names), len(set(badge_names)), 
                         f"Duplicate badges found: {badge_names}")

        # Check that all badges are present
        self.assertEqual(len(badge_names), 4)
        self.assertIn('Python Basics', badge_names)
        self.assertIn('Django Framework', badge_names)
        self.assertIn('Advanced Python', badge_names)
        self.assertIn('Django REST Framework', badge_names)
