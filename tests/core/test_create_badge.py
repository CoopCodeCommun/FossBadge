from django.test import TestCase
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from pathlib import Path
from core.models import Structure, Badge

class CreateBadgeTest(TestCase):
    """Test the badge creation page view"""

    def setUp(self):
        """Set up test data"""
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
        base_dir = Path(__file__).resolve().parent.parent.parent
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
        badge = Badge.objects.filter(name='Test Badge Created From Form').first()
        self.assertIsNotNone(badge)
        self.assertEqual(badge.level, 'intermediate')
        self.assertEqual(badge.description, 'This is a test badge created from the form submission test')
        self.assertEqual(badge.issuing_structure, self.structure)

        # Check that the badge appears in the list view
        list_response = self.client.get(reverse('core:badge-list'))
        list_content = list_response.content.decode('utf-8')
        self.assertIn('Test Badge Created From Form', list_content)