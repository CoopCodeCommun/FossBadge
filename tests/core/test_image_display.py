from django.test import TestCase
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from pathlib import Path
from core.models import Structure, Badge, User

class ImageDisplayTest(TestCase):
    """Test that images are displayed correctly using django-pictures"""

    def setUp(self):
        """Set up test data with images"""
        # Get test image paths
        base_dir = Path(__file__).resolve().parent.parent.parent
        structure_image_path = base_dir / 'media' / 'structures' / 'examples' / 'draw_svg20210805-28561-1nfg07n.svg.png'
        badge_image_path = base_dir / 'media' / 'badges' / 'exemples' / 'gp1.png'

        # Create test structure with image
        with open(structure_image_path, 'rb') as f:
            image_content = f.read()

        self.structure = Structure.objects.create(
            name="Test Structure with Image",
            type="association",
            address="123 Test Street",
            description="Test Description",
            referent_last_name="Test",
            referent_first_name="User",
            referent_position="Tester"
        )
        self.structure.logo.save('test_structure_logo.png', SimpleUploadedFile('test_structure_logo.png', image_content))

        # Create test badge with image
        with open(badge_image_path, 'rb') as f:
            image_content = f.read()

        self.badge = Badge.objects.create(
            name="Test Badge with Image",
            level="intermediate",
            description="Test Badge Description",
            issuing_structure=self.structure
        )
        self.badge.icon.save('test_badge_icon.png', SimpleUploadedFile('test_badge_icon.png', image_content))

        # Create test user
        self.user = User.objects.create_user(
            username='testimageuser',
            email='testimageuser@example.com',
            password='testpassword',
            first_name='Test',
            last_name='Image User',
            address = '123 Test Street'
        )

    def test_structure_detail_page_displays_image(self):
        """Test that the structure detail page displays the structure logo using django-pictures"""
        response = self.client.get(reverse('core:structure-detail', kwargs={'pk': self.structure.pk}))
        content = response.content.decode('utf-8')

        # Check that the image is displayed using django-pictures (rendered HTML)
        self.assertIn('<picture>', content)
        self.assertIn('<source type="image/webp"', content)
        self.assertIn('srcset=', content)
        self.assertIn('sizes=', content)
        self.assertIn('/media/structures/logos/', content)

    def test_badge_detail_page_displays_image(self):
        """Test that the badge detail page displays the badge icon using django-pictures"""
        response = self.client.get(reverse('core:badge-detail', kwargs={'pk': self.badge.pk}))
        content = response.content.decode('utf-8')

        # Check that the image is displayed using django-pictures (rendered HTML)
        self.assertIn('<picture', content)
        self.assertIn('<source type="image/webp"', content)
        self.assertIn('srcset=', content)
        self.assertIn('sizes=', content)
        self.assertIn('/media/badges/icons/', content)

    def test_structure_list_page_displays_images(self):
        """Test that the structure list page displays structure logos using django-pictures"""
        response = self.client.get(reverse('core:structure-list'))
        content = response.content.decode('utf-8')

        # Check that the image is displayed using django-pictures (rendered HTML)
        self.assertIn('<picture>', content)
        self.assertIn('<source type="image/webp"', content)
        self.assertIn('srcset=', content)
        self.assertIn('sizes=', content)
        self.assertIn('/media/structures/logos/', content)

    def test_badge_list_page_displays_images(self):
        """Test that the badge list page displays badge icons using django-pictures"""
        response = self.client.get(reverse('core:badge-list'))
        content = response.content.decode('utf-8')

        # Check that the image is displayed using django-pictures (rendered HTML)
        self.assertIn('<picture>', content)
        self.assertIn('<source type="image/webp"', content)
        self.assertIn('srcset=', content)
        self.assertIn('sizes=', content)
        self.assertIn('/media/badges/icons/', content)