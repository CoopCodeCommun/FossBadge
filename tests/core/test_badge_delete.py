from django.test import TestCase
from django.urls import reverse
from core.models import Structure, Badge


class DeleteBadgeTest(TestCase):
    """Test the badge deletion page view"""

    def setUp(self):
        """Set up test data"""

        self.structure = Structure.objects.create(
            name="Test Structure",
            type="association",
            address="123 Test Street",
            description="Test Description",
            referent_last_name="Test",
            referent_first_name="User",
            referent_position="Tester"
        )

        self.badge = Badge(
            name="Test Badge",
            level="intermediate",
            description="This is a test badge",
            issuing_structure=self.structure
        )
        self.badge.save()

        # Attributes to avoid code repetition
        self.template_name = 'core:badge-delete'
        self.redirect_args = {
            "viewname": self.template_name,
            "kwargs": {'pk': self.badge.pk}
        }

    def test_delete_badge_page_loads_correctly(self):
        """Test that the badge deletion page loads correctly with a 200 status code"""
        response = self.client.get(reverse(**self.redirect_args))
        self.assertEqual(response.status_code, 200)

    def test_delete_badge_page_uses_correct_template(self):
        """Test that the badge deletion page uses the correct template"""
        response = self.client.get(reverse(**self.redirect_args))
        self.assertTemplateUsed(response, 'core/badges/delete.html')
        self.assertTemplateUsed(response, 'base.html')

    def test_delete_badge_page_contains_expected_content(self):
        """Test that the badge deletion page contains expected content"""
        response = self.client.get(reverse(**self.redirect_args))
        content = response.content.decode('utf-8')

        # Check for badge deletion specific content
        self.assertIn('Supprimer un badge', content)
        self.assertIn(f'Êtes-vous sûr de vouloir supprimer le badge "{self.badge.name}" ?', content)
        self.assertIn('Supprimer le badge', content)
        self.assertIn('Revenir en arrière', content)

    def test_delete_badge_form_submission(self):
        """Test submitting the badge deletion form"""

        # Check if badge is in the database
        badge = Badge.objects.filter(name='Test Badge').first()
        self.assertIsNotNone(badge)

        # Submit the form
        response = self.client.post(
            reverse(**self.redirect_args),
            follow=True  # Follow redirects
        )

        # Check that the form submission was successful (should redirect to badge list)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/badges/list.html')

        # Verify that the badge is not present in the database
        badge = Badge.objects.filter(name='Test Badge').first()
        self.assertIsNone(badge)

        # Check that the badge not appears in the list view
        list_response = self.client.get(reverse('core:badge-list'))
        list_content = list_response.content.decode('utf-8')
        self.assertNotIn('Test Badge', list_content)
