from django.test import TestCase
from django.urls import reverse
from core.models import Structure, Badge


class EditBadgeTest(TestCase):
    """Test the badge edition page view"""

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
        self.template_name = 'core:badge-edit'
        self.redirect_args = {
            "viewname": self.template_name,
            "kwargs": {'pk': self.badge.pk}
        }

    def test_edit_badge_page_loads_correctly(self):
        """Test that the badge edition page loads correctly with a 200 status code"""
        response = self.client.get(reverse(**self.redirect_args))
        self.assertEqual(response.status_code, 200)

    def test_edit_badge_page_uses_correct_template(self):
        """Test that the badge edition page uses the correct template"""
        response = self.client.get(reverse(**self.redirect_args))
        self.assertTemplateUsed(response, 'core/badges/edit.html')
        self.assertTemplateUsed(response, 'base.html')

    def test_edit_badge_page_contains_expected_content(self):
        """Test that the badge edition page contains expected content"""
        response = self.client.get(reverse(**self.redirect_args))
        content = response.content.decode('utf-8')

        # Check for badge edition specific content
        self.assertIn('Modifier un Badge', content)
        self.assertIn('Informations du badge', content)
        self.assertIn('Structures où ce badge est valable', content)
        self.assertIn('Niveau', content)
        self.assertIn('Structure émettrice', content)

    def test_edit_badge_form_submission(self):
        """Test submitting the badge edition form with valid data"""

        # Prepare form data
        form_data = {
            'name': 'Test Badge Edition',
            'level': 'expert',
            "description" : "This is a test badge edition",
            "issuing_structure" : self.structure.pk,
        }

        # Submit the form
        response = self.client.post(
            reverse(**self.redirect_args),
            data={**form_data},
            follow=True  # Follow redirects
        )

        # Check that the form submission was successful (should redirect to badge detail)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/badges/detail.html')

        # Verify the badge was edited in the database
        badge = Badge.objects.filter(name='Test Badge Edition').first()
        self.assertIsNotNone(badge)
        self.assertEqual(badge.name, 'Test Badge Edition')
        self.assertEqual(badge.level, 'expert')
        self.assertEqual(badge.description, 'This is a test badge edition')
        self.assertEqual(badge.issuing_structure, self.structure)

        # Check that the badge appears in the list view
        list_response = self.client.get(reverse('core:badge-list'))
        list_content = list_response.content.decode('utf-8')
        self.assertIn('Test Badge Edition', list_content)