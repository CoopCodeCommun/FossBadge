from django.test import TestCase
from django.urls import reverse
from core.models import User, Structure, Badge
from django.utils import timezone
from datetime import timedelta

class UserProfileTest(TestCase):
    """Test the user profile page view"""

    def setUp(self):
        """Set up test data"""
        # Create a test user
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword',
            first_name='Test',
            last_name='User',
            address = '123 Test Street'
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
        assignment = self.badge.add_holder(self.user)
        assignment.assigned_date = self.assignment_date
        assignment.save()

    def test_user_profile_page_loads_correctly(self):
        """Test that the user profile page loads correctly with a 200 status code"""
        response = self.client.get(reverse('core:user-detail', kwargs={'pk': self.user.id}))
        self.assertEqual(response.status_code, 200)

    def test_user_profile_page_uses_correct_template(self):
        """Test that the user profile page uses the correct template"""
        response = self.client.get(reverse('core:user-detail', kwargs={'pk': self.user.id}))
        self.assertTemplateUsed(response, 'core/users/detail.html')
        self.assertTemplateUsed(response, 'base.html')

    def test_user_profile_page_contains_expected_content(self):
        """Test that the user profile page contains expected content"""
        response = self.client.get(reverse('core:user-detail', kwargs={'pk': self.user.id}))
        content = response.content.decode('utf-8')

        # Check for user profile specific content
        self.assertIn('Profil de Test User', content)
        self.assertIn('Informations personnelles', content)
        self.assertIn('Mes badges', content)
        self.assertIn('Mes structures', content)

    def test_user_profile_page_displays_badge_assignment_dates(self):
        """Test that the user profile page displays badge assignment dates correctly"""
        response = self.client.get(reverse('core:user-detail', kwargs={'pk': self.user.id}))
        content = response.content.decode('utf-8')

        # Check that the badge is displayed
        self.assertIn('Test Badge', content)

        # Check that the assignment date is displayed in the exact format
        formatted_date = self.assignment_date.strftime('%d/%m/%Y')
        self.assertIn(f'Assigné le {formatted_date}', content)

        # Check that the humanized date is displayed
        self.assertIn('il y a', content.lower())  # "il y a" is the French equivalent of "ago"
