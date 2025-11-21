from django.test import TestCase
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from pathlib import Path
from core.models import Structure


class EditStructureTest(TestCase):
    """Test the structure edition page view"""

    def setUp(self):
        """Set up test data"""

        # Prepare test image for structure logo
        base_dir = Path(__file__).resolve().parent.parent.parent
        structure_image_path = base_dir / 'media' / 'structures' / 'examples' / 'draw_svg20210805-28561-1nfg07n.svg.png'

        with open(structure_image_path, 'rb') as f:
            self.image_content = f.read()

        structure = Structure(
            name='Test Structure Created From Form',
            type='association',
            address='123 Test Street, Test City',
            siret='123 456 789 00012',
            description='This is a test structure created from the form submission test',
            referent_last_name='Test',
            referent_first_name='User',
            referent_position='Tester',
            latitude=48.8566,
            longitude=2.3522,
        )
        structure.save()

        # Attributes to avoid code repetition
        self.template_name = 'core:structure-edit'
        self.redirect_args = {
            "viewname": self.template_name,
            "kwargs": {'pk': structure.pk}
        }

    def test_edit_structure_page_loads_correctly(self):
        """Test that the structure edition page loads correctly with a 200 status code"""
        response = self.client.get(reverse(**self.redirect_args))
        self.assertEqual(response.status_code, 200)

    def test_edit_structure_page_uses_correct_template(self):
        """Test that the structure edition page uses the correct template"""
        response = self.client.get(reverse(**self.redirect_args))
        self.assertTemplateUsed(response, 'core/structures/edit.html')
        self.assertTemplateUsed(response, 'base.html')

    def test_edit_structure_page_contains_expected_content(self):
        """Test that the structure edition page contains expected content"""
        response = self.client.get(reverse(**self.redirect_args))
        content = response.content.decode('utf-8')

        # Check for structure edition specific content
        self.assertIn('Modifier une structure', content)
        self.assertIn('Informations générales', content)
        self.assertIn('Personne référente', content)
        self.assertIn('Nom', content)
        self.assertIn('SIREN/SIRET', content)

    def test_edit_structure_form_submission(self):
        """Test submitting the structure edition form with valid data"""
        # Prepare form data
        form_data = {
            'name': 'Test Structure Edited From Form',
            'type': 'association',
            'address': '123 Test Street, Test City',
            'siret': '123 456 789 00012',
            'description': 'This is a test structure edited from the form submission test',
            'referent_last_name': 'Test 2',
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
            reverse(**self.redirect_args),
            data={**form_data, 'logo': test_image},
            follow=True  # Follow redirects
        )

        # Check that the form submission was successful (should redirect to structure detail)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/structures/detail.html')

        # Verify the structure was edited in the database
        structure = Structure.objects.filter(name='Test Structure Edited From Form').first()
        self.assertIsNotNone(structure)
        self.assertEqual(structure.type, 'association')
        self.assertEqual(structure.address, '123 Test Street, Test City')
        self.assertEqual(structure.siret, '123 456 789 00012')
        self.assertEqual(structure.description, 'This is a test structure edited from the form submission test')
        self.assertEqual(structure.referent_last_name, 'Test 2')
        self.assertEqual(structure.referent_first_name, 'User')
        self.assertEqual(structure.referent_position, 'Tester')
        self.assertEqual(structure.latitude, 48.8566)
        self.assertEqual(structure.longitude, 2.3522)

        # Check that the structure appears in the list view
        list_response = self.client.get(reverse('core:structure-list'))
        list_content = list_response.content.decode('utf-8')
        self.assertIn('Test Structure Edited From Form', list_content)