from django.test import TestCase
from django.urls import reverse
from core.models import Structure, Badge

class BadgeDetailTest(TestCase):
    """Test the badge detail page view"""

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