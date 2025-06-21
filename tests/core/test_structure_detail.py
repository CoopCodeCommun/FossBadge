from django.test import TestCase
from django.urls import reverse
from core.models import Structure

class StructureDetailTest(TestCase):
    """Test the structure detail page view"""

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