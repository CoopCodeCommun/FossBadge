from django.test import TestCase
from django.urls import reverse
from django.test import Client

# Create your tests here.
class HomePageTest(TestCase):
    """Test the home page view"""

    def test_home_page_loads_correctly(self):
        """Test that the home page loads correctly with a 200 status code"""
        response = self.client.get(reverse('core:home'))
        self.assertEqual(response.status_code, 200)

    def test_home_page_uses_correct_template(self):
        """Test that the home page uses the correct template"""
        response = self.client.get(reverse('core:home'))
        self.assertTemplateUsed(response, 'core/index.html')
        self.assertTemplateUsed(response, 'base.html')

    def test_home_page_contains_static_files(self):
        """Test that the home page contains references to all required static files"""
        response = self.client.get(reverse('core:home'))
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

    def test_user_profile_page_loads_correctly(self):
        """Test that the user profile page loads correctly with a 200 status code"""
        response = self.client.get(reverse('core:user_profile'))
        self.assertEqual(response.status_code, 200)

    def test_user_profile_page_uses_correct_template(self):
        """Test that the user profile page uses the correct template"""
        response = self.client.get(reverse('core:user_profile'))
        self.assertTemplateUsed(response, 'core/user.html')
        self.assertTemplateUsed(response, 'base.html')

    def test_user_profile_page_contains_expected_content(self):
        """Test that the user profile page contains expected content"""
        response = self.client.get(reverse('core:user_profile'))
        content = response.content.decode('utf-8')

        # Check for user profile specific content
        self.assertIn('Profil Utilisateur', content)
        self.assertIn('Informations personnelles', content)
        self.assertIn('Mes badges', content)
        self.assertIn('Mes structures', content)


class BadgeDetailTest(TestCase):
    """Test the badge detail page view"""

    def test_badge_detail_page_loads_correctly(self):
        """Test that the badge detail page loads correctly with a 200 status code"""
        response = self.client.get(reverse('core:badge_detail'))
        self.assertEqual(response.status_code, 200)

    def test_badge_detail_page_uses_correct_template(self):
        """Test that the badge detail page uses the correct template"""
        response = self.client.get(reverse('core:badge_detail'))
        self.assertTemplateUsed(response, 'core/badge.html')
        self.assertTemplateUsed(response, 'base.html')

    def test_badge_detail_page_contains_expected_content(self):
        """Test that the badge detail page contains expected content"""
        response = self.client.get(reverse('core:badge_detail'))
        content = response.content.decode('utf-8')

        # Check for badge detail specific content
        self.assertIn('Détails du Badge', content)
        self.assertIn('QR Code', content)
        self.assertIn('Structures où ce badge est valable', content)
        self.assertIn('Ce badge est rattaché à d\'autres personnes', content)


class StructureDetailTest(TestCase):
    """Test the structure detail page view"""

    def test_structure_detail_page_loads_correctly(self):
        """Test that the structure detail page loads correctly with a 200 status code"""
        response = self.client.get(reverse('core:association_detail'))
        self.assertEqual(response.status_code, 200)

    def test_structure_detail_page_uses_correct_template(self):
        """Test that the structure detail page uses the correct template"""
        response = self.client.get(reverse('core:association_detail'))
        self.assertTemplateUsed(response, 'core/association.html')
        self.assertTemplateUsed(response, 'base.html')

    def test_structure_detail_page_contains_expected_content(self):
        """Test that the structure detail page contains expected content"""
        response = self.client.get(reverse('core:association_detail'))
        content = response.content.decode('utf-8')

        # Check for structure detail specific content
        self.assertIn('Structure / Entreprise', content)
        self.assertIn('Forger un nouveau badge', content)
        self.assertIn('Localisation', content)
        self.assertIn('Badges disponibles', content)


class CreateBadgeTest(TestCase):
    """Test the badge creation page view"""

    def test_create_badge_page_loads_correctly(self):
        """Test that the badge creation page loads correctly with a 200 status code"""
        response = self.client.get(reverse('core:create_badge'))
        self.assertEqual(response.status_code, 200)

    def test_create_badge_page_uses_correct_template(self):
        """Test that the badge creation page uses the correct template"""
        response = self.client.get(reverse('core:create_badge'))
        self.assertTemplateUsed(response, 'core/create_badge.html')
        self.assertTemplateUsed(response, 'base.html')

    def test_create_badge_page_contains_expected_content(self):
        """Test that the badge creation page contains expected content"""
        response = self.client.get(reverse('core:create_badge'))
        content = response.content.decode('utf-8')

        # Check for badge creation specific content
        self.assertIn('Forger un nouveau Badge', content)
        self.assertIn('Icône du badge', content)
        self.assertIn('Nom du badge', content)
        self.assertIn('Niveau', content)
        self.assertIn('Description courte', content)


class CreateStructureTest(TestCase):
    """Test the structure creation page view"""

    def test_create_structure_page_loads_correctly(self):
        """Test that the structure creation page loads correctly with a 200 status code"""
        response = self.client.get(reverse('core:create_association'))
        self.assertEqual(response.status_code, 200)

    def test_create_structure_page_uses_correct_template(self):
        """Test that the structure creation page uses the correct template"""
        response = self.client.get(reverse('core:create_association'))
        self.assertTemplateUsed(response, 'core/create_association.html')
        self.assertTemplateUsed(response, 'base.html')

    def test_create_structure_page_contains_expected_content(self):
        """Test that the structure creation page contains expected content"""
        response = self.client.get(reverse('core:create_association'))
        content = response.content.decode('utf-8')

        # Check for structure creation specific content
        self.assertIn('Créer une Structure / Entreprise', content)
        self.assertIn('Informations générales', content)
        self.assertIn('Personne référente', content)
        self.assertIn('Nom de la structure/entreprise', content)
        self.assertIn('Numéro SIREN/SIRET', content)
