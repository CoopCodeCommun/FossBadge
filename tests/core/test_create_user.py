from django.test import TestCase
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from pathlib import Path
from core.models import User

class CreateUserTest(TestCase):
    """Test the user creation page view"""

    def setUp(self):
        """Set up test data"""

        # Prepare test image for user icon
        base_dir = Path(__file__).resolve().parent.parent.parent
        user_image_path = base_dir / 'media' / 'users' / 'examples' / 'adoni.png'

        with open(user_image_path, 'rb') as f:
            self.image_content = f.read()

        self.test_image = SimpleUploadedFile(
            name='test_user_icon.png',
            content=self.image_content,
            content_type='image/png'
        )

    def test_create_user_page_loads_correctly(self):
        """Test that the user creation page loads correctly with a 200 status code"""
        response = self.client.get(reverse('core:create_user'))
        self.assertEqual(response.status_code, 200)

    def test_create_user_page_uses_correct_template(self):
        """Test that the user creation page uses the correct template"""
        response = self.client.get(reverse('core:create_user'))
        self.assertTemplateUsed(response, 'core/users/create.html')
        self.assertTemplateUsed(response, 'base.html')

    def test_create_user_page_contains_expected_content(self):
        """Test that the user creation page contains expected content"""
        response = self.client.get(reverse('core:create_user'))
        content = response.content.decode('utf-8')

        # Check for user creation specific content
        self.assertIn('Créer un utilisateur', content)
        self.assertIn('Avatar', content)
        self.assertIn('Prénom', content)
        self.assertIn('Nom', content)
        self.assertIn('Adresse électronique', content)
        self.assertIn('Mot de passe', content)
        self.assertIn('Confirmation du mot de passe', content)
        self.assertIn('Adresse', content)

    def test_create_user_form_submission(self):
        """Test submitting the user creation form with valid data"""
        # Prepare form data
        form_data = {
            'first_name': 'Jean',
            'last_name': 'Test',
            'email': 'test@user.fr',
            'password': 'random_password',
            'password_confirm': 'random_password',
            'address': '50 rue du test',
        }

        # Create a fresh test image for each test
        test_image = SimpleUploadedFile(
            name='test_user_avatar.png',
            content=self.image_content,
            content_type='image/png'
        )

        # Submit the form
        response = self.client.post(
            reverse('core:create_user'),
            data={**form_data, 'avatar': test_image},
            follow=True  # Follow redirects
        )

        # Check that the form submission was successful (should redirect to user detail)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/users/detail.html')

        # Verify the user was created in the database
        user = User.objects.get(email='test@user.fr')

        self.assertIsNotNone(user)
        self.assertEqual(user.first_name, 'Jean')
        self.assertEqual(user.last_name, 'Test')
        self.assertEqual(user.profile.address, '50 rue du test')

        # Check that the user appears in the list view
        list_response = self.client.get(reverse('core:user-list'))
        list_content = list_response.content.decode('utf-8')
        self.assertIn('Jean Test', list_content)