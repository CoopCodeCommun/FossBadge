from django.test import TestCase
from django.urls import reverse
from bs4 import BeautifulSoup
from core.models import Structure, Badge

class BadgeSearchFilterTest(TestCase):
    """Test the badge search and filter functionality"""

    def setUp(self):
        """Set up test data"""
        # Create test structures
        self.structure1 = Structure.objects.create(
            name="Python Structure",
            type="association",
            address="123 Python Street",
            description="Python Structure Description",
            referent_last_name="Python",
            referent_first_name="Developer",
            referent_position="Lead"
        )

        self.structure2 = Structure.objects.create(
            name="Django Association",
            type="association",
            address="456 Django Avenue",
            description="Django Association Description",
            referent_last_name="Django",
            referent_first_name="Developer",
            referent_position="Lead"
        )

        # Create test badges with different levels and structures
        self.badge1 = Badge.objects.create(
            name="Python Basics",
            level="beginner",
            description="Learn Python basics",
            issuing_structure=self.structure1
        )

        self.badge2 = Badge.objects.create(
            name="Django Framework",
            level="intermediate",
            description="Learn Django web framework",
            issuing_structure=self.structure2
        )

        self.badge3 = Badge.objects.create(
            name="Advanced Python",
            level="expert",
            description="Advanced Python concepts",
            issuing_structure=self.structure1
        )

        self.badge4 = Badge.objects.create(
            name="Django REST Framework",
            level="expert",
            description="Build APIs with Django REST Framework",
            issuing_structure=self.structure2
        )

    def test_badge_search_by_name(self):
        """Test searching badges by name"""
        response = self.client.get(reverse('core:badge-list') + '?search=Python')
        self.assertEqual(response.status_code, 200)

        # Parse the HTML content
        soup = BeautifulSoup(response.content, 'html.parser')
        badge_cards = soup.select('.badge-grid .card')

        # Check that only Python badges are returned
        self.assertEqual(len(badge_cards), 2)
        badge_names = [card.select_one('.card-title').text.strip() for card in badge_cards]
        self.assertIn('Python Basics', badge_names)
        self.assertIn('Advanced Python', badge_names)
        self.assertNotIn('Django Framework', badge_names)
        self.assertNotIn('Django REST Framework', badge_names)

    def test_badge_search_by_description(self):
        """Test searching badges by description"""
        response = self.client.get(reverse('core:badge-list') + '?search=API')
        self.assertEqual(response.status_code, 200)

        # Parse the HTML content
        soup = BeautifulSoup(response.content, 'html.parser')
        badge_cards = soup.select('.badge-grid .card')

        # Check that only badges with 'API' in description are returned
        self.assertEqual(len(badge_cards), 1)
        badge_names = [card.select_one('.card-title').text.strip() for card in badge_cards]
        self.assertIn('Django REST Framework', badge_names)

    def test_badge_search_by_structure(self):
        """Test searching badges by structure name"""
        response = self.client.get(reverse('core:badge-list') + '?search=Django')
        self.assertEqual(response.status_code, 200)

        # Parse the HTML content
        soup = BeautifulSoup(response.content, 'html.parser')
        badge_cards = soup.select('.badge-grid .card')

        # Check that only badges from Django structure are returned
        self.assertEqual(len(badge_cards), 2)
        badge_names = [card.select_one('.card-title').text.strip() for card in badge_cards]
        self.assertIn('Django Framework', badge_names)
        self.assertIn('Django REST Framework', badge_names)
        self.assertNotIn('Python Basics', badge_names)
        self.assertNotIn('Advanced Python', badge_names)

    def test_badge_filter_by_level(self):
        """Test filtering badges by level"""
        # Test filtering by beginner level
        response = self.client.get(reverse('core:badge-list') + '?level=beginner')
        self.assertEqual(response.status_code, 200)

        # Parse the HTML content
        soup = BeautifulSoup(response.content, 'html.parser')
        badge_cards = soup.select('.badge-grid .card')

        # Check that only beginner badges are returned
        self.assertEqual(len(badge_cards), 1)
        badge_names = [card.select_one('.card-title').text.strip() for card in badge_cards]
        self.assertIn('Python Basics', badge_names)

        # Test filtering by expert level
        response = self.client.get(reverse('core:badge-list') + '?level=expert')
        self.assertEqual(response.status_code, 200)

        # Parse the HTML content
        soup = BeautifulSoup(response.content, 'html.parser')
        badge_cards = soup.select('.badge-grid .card')

        # Check that only expert badges are returned
        self.assertEqual(len(badge_cards), 2)
        badge_names = [card.select_one('.card-title').text.strip() for card in badge_cards]
        self.assertIn('Advanced Python', badge_names)
        self.assertIn('Django REST Framework', badge_names)

        # Test filtering by multiple levels
        response = self.client.get(reverse('core:badge-list') + '?level=beginner&level=intermediate')
        self.assertEqual(response.status_code, 200)

        # Parse the HTML content
        soup = BeautifulSoup(response.content, 'html.parser')
        badge_cards = soup.select('.badge-grid .card')

        # Check that beginner and intermediate badges are returned
        self.assertEqual(len(badge_cards), 2)
        badge_names = [card.select_one('.card-title').text.strip() for card in badge_cards]
        self.assertIn('Python Basics', badge_names)
        self.assertIn('Django Framework', badge_names)

    def test_badge_filter_by_structure(self):
        """Test filtering badges by structure"""
        response = self.client.get(reverse('core:badge-list') + f'?structure={self.structure1.id}')
        self.assertEqual(response.status_code, 200)

        # Parse the HTML content
        soup = BeautifulSoup(response.content, 'html.parser')
        badge_cards = soup.select('.badge-grid .card')

        # Check that only badges from structure1 are returned
        self.assertEqual(len(badge_cards), 2)
        badge_names = [card.select_one('.card-title').text.strip() for card in badge_cards]
        self.assertIn('Python Basics', badge_names)
        self.assertIn('Advanced Python', badge_names)
        self.assertNotIn('Django Framework', badge_names)
        self.assertNotIn('Django REST Framework', badge_names)

    def test_badge_combined_search_and_filter(self):
        """Test combining search and filter"""
        response = self.client.get(reverse('core:badge-list') + f'?search=Python&level=expert')
        self.assertEqual(response.status_code, 200)

        # Parse the HTML content
        soup = BeautifulSoup(response.content, 'html.parser')
        badge_cards = soup.select('.badge-grid .card')

        # Check that only expert Python badges are returned
        self.assertEqual(len(badge_cards), 1)
        badge_names = [card.select_one('.card-title').text.strip() for card in badge_cards]
        self.assertIn('Advanced Python', badge_names)
        self.assertNotIn('Python Basics', badge_names)
        self.assertNotIn('Django Framework', badge_names)
        self.assertNotIn('Django REST Framework', badge_names)

    def test_htmx_request_returns_partial_template(self):
        """Test that HTMX requests return the partial template"""
        # Make a regular request
        regular_response = self.client.get(reverse('core:badge-list'))
        self.assertEqual(regular_response.status_code, 200)
        self.assertTemplateUsed(regular_response, 'core/badges/list.html')
        self.assertTemplateUsed(regular_response, 'base.html')

        # Make an HTMX request
        htmx_response = self.client.get(
            reverse('core:badge-list'),
            HTTP_HX_REQUEST='true'
        )
        self.assertEqual(htmx_response.status_code, 200)
        self.assertTemplateUsed(htmx_response, 'core/badges/partials/badge_list.html')
        self.assertNotIn('base.html', [t.name for t in htmx_response.templates])

        # Check that the HTMX response contains only the badge list
        htmx_content = htmx_response.content.decode('utf-8')
        self.assertIn('<div class="badge-grid">', htmx_content)
        self.assertNotIn('<div class="col-md-3 mb-4">', htmx_content)  # Filter sidebar should not be included

    def test_no_duplicate_data_in_response(self):
        """Test that there are no duplicate badges in the response"""
        response = self.client.get(reverse('core:badge-list'))
        self.assertEqual(response.status_code, 200)

        # Parse the HTML content
        soup = BeautifulSoup(response.content, 'html.parser')
        badge_cards = soup.select('.badge-grid .card')

        # Extract badge names
        badge_names = [card.select_one('.card-title').text.strip() for card in badge_cards]

        # Check for duplicates by comparing the length of the list with the length of the set
        self.assertEqual(len(badge_names), len(set(badge_names)), 
                         f"Duplicate badges found: {badge_names}")

        # Check that all badges are present
        self.assertEqual(len(badge_names), 4)
        self.assertIn('Python Basics', badge_names)
        self.assertIn('Django Framework', badge_names)
        self.assertIn('Advanced Python', badge_names)
        self.assertIn('Django REST Framework', badge_names)