from django.test import TestCase
from django.urls import reverse
from core.models import Structure


class DeleteStructureTest(TestCase):
    """Test the structure deletion page view"""

    def setUp(self):
        """Set up test data"""

        structure = Structure(
            name='Test Structure For Deletion',
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
        self.template_name = 'core:structure-delete'
        self.redirect_args = {
            "viewname": self.template_name,
            "kwargs": {'pk': structure.pk}
        }

    def test_delete_structure_page_loads_correctly(self):
        """Test that the structure deletion page loads correctly with a 200 status code"""
        response = self.client.get(reverse(**self.redirect_args))
        self.assertEqual(response.status_code, 200)

    def test_delete_structure_page_uses_correct_template(self):
        """Test that the structure deletion page uses the correct template"""
        response = self.client.get(reverse(**self.redirect_args))
        self.assertTemplateUsed(response, 'core/structures/delete.html')
        self.assertTemplateUsed(response, 'base.html')

    def test_delete_structure_page_contains_expected_content(self):
        """Test that the structure deletion page contains expected content"""
        response = self.client.get(reverse(**self.redirect_args))
        content = response.content.decode('utf-8')

        # Check for structure deletion specific content
        self.assertIn('Supprimer une structure', content)
        self.assertIn('Êtes-vous sûr de vouloir supprimer la structure ', content)
        self.assertIn('Supprimer la structure', content)
        self.assertIn('Revenir en arrière', content)

    def test_delete_structure_form_submission(self):
        """Test submitting the structure deletion form"""

        # Check if structure is in the database
        structure = Structure.objects.filter(name='Test Structure For Deletion').first()
        self.assertIsNotNone(structure)

        # Submit the form
        response = self.client.post(
            reverse(**self.redirect_args),
            follow=True  # Follow redirects
        )

        # Check that the form submission was successful (should redirect to structure list)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/structures/list.html')

        # Verify that the structure is not present in the database
        structure = Structure.objects.filter(name='Test Structure For Deletion').first()
        self.assertIsNone(structure)

        # Check that the structure not appears in the list view
        list_response = self.client.get(reverse('core:structure-list'))
        list_content = list_response.content.decode('utf-8')
        self.assertNotIn('Test Structure For Deletion', list_content)
