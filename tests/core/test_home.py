from django.test import TestCase
from django.urls import reverse

# Create your tests here.
class HomePageTest(TestCase):
    """Test the home page view"""

    def test_home_page_loads_correctly(self):
        """Test that the home page loads correctly with a 200 status code"""
        response = self.client.get(reverse('core:home-list'))
        self.assertEqual(response.status_code, 200)

    def test_home_page_uses_correct_template(self):
        """Test that the home page uses the correct template"""
        response = self.client.get(reverse('core:home-list'))
        self.assertTemplateUsed(response, 'core/home/index.html')
        self.assertTemplateUsed(response, 'base.html')

    def test_home_page_contains_static_files(self):
        """Test that the home page contains references to all required static files"""
        response = self.client.get(reverse('core:home-list'))
        content = response.content.decode('utf-8')

        # Check for Bootstrap CSS
        self.assertIn('bootstrap.min.css', content)

        # Check for Bootstrap JS
        self.assertIn('bootstrap.bundle.min.js', content)

        # Check for HTMX
        self.assertIn('htmx.min.js', content)

        # Check for custom CSS
        self.assertIn('custom.css', content)