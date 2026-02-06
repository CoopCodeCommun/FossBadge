import uuid
from itertools import chain
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from pictures.models import PictureField
from django.db.models import Q

# Create your models here.

class User(AbstractUser):

    uuid = models.UUIDField(default=uuid.uuid7, primary_key=True, db_index=True)

    avatar_width = models.PositiveIntegerField(blank=True, null=True, editable=False)
    avatar_height = models.PositiveIntegerField(blank=True, null=True, editable=False)
    avatar = PictureField(upload_to='users/avatars/', blank=True, null=True, verbose_name="Avatar",
                         aspect_ratios=[None, "1/1", "3/2"], width_field='avatar_width', height_field='avatar_height')
    address = models.TextField(blank=True, null=True, verbose_name="Adresse")

    class Meta:
        verbose_name = "Utilisateur"
        verbose_name_plural = "Utilisateurs"

    def __str__(self):
        return f"Profil de {self.username}"

    @property
    def structures(self):
        return Structure.objects.filter(
            Q(admins=self.pk)|
            Q(editors=self.pk)|
            Q(users=self.pk),
        ).distinct()


    def get_badges(self):
        """
        Returns all badges held by this user
        """
        return Badge.objects.filter(assignments__user=self)

    def get_badge_assignments(self):
        """
        Returns all badge assignments for this user
        """
        return self.badge_assignments.all().order_by('-assigned_date')

    def add_badge(self, badge, assigned_by=None, notes=None):
        """
        Adds a badge to this user
        """
        return badge.add_holder(self, assigned_by, notes)

    def remove_badge(self, badge):
        """
        Removes a badge from this user
        """
        badge.remove_holder(self)


class Structure(models.Model):
    """
    Model representing a structure (association, company, school, etc.)
    """

    uuid = models.UUIDField(default=uuid.uuid7, primary_key=True, db_index=True)

    TYPE_CHOICES = [
        ('association', 'Association'),
        ('company', 'Entreprise'),
        ('school', 'École'),
    ]

    ROLES = [
        ('admin',"Administrateur"),
        ('editor', "Éditeur"),
        ('user', "Utilisateur"),
    ]

    name = models.CharField(max_length=100, verbose_name="Nom")
    logo_width = models.PositiveIntegerField(blank=True, null=True, editable=False)
    logo_height = models.PositiveIntegerField(blank=True, null=True, editable=False)
    logo = PictureField(upload_to='structures/logos/', blank=True, null=True, verbose_name="Logo", 
                        aspect_ratios=[None, "1/1", "16/9"], width_field='logo_width', height_field='logo_height')
    type = models.CharField(max_length=20, choices=TYPE_CHOICES, verbose_name="Type")
    address = models.TextField(verbose_name="Adresse")
    siret = models.CharField(max_length=20, blank=True, null=True, verbose_name="SIREN/SIRET")
    description = models.TextField(verbose_name="Description")

    # Referent person information
    # TODO : use a foreign key to user ? and remove those fields
    referent_last_name = models.CharField(max_length=100, verbose_name="Nom du référent")
    referent_first_name = models.CharField(max_length=100, verbose_name="Prénom du référent")
    referent_position = models.CharField(max_length=100, verbose_name="Poste du référent")

    # Location for map display
    latitude = models.FloatField(blank=True, null=True, verbose_name="Latitude")
    longitude = models.FloatField(blank=True, null=True, verbose_name="Longitude")

    # Relationships
    admins = models.ManyToManyField(User, related_name='structures_admins', verbose_name='Administrateurs')
    editors = models.ManyToManyField(User, related_name='structures_editors', verbose_name='Éditeurs')
    users = models.ManyToManyField(User, related_name='structures_users', blank=True, verbose_name="Utilisateurs")

    class Meta:
        verbose_name = "Structure"
        verbose_name_plural = "Structures"
        ordering = ['name']

    def __str__(self):
        return self.name

    # def users(self):
    #     return list(chain(self.admins.all(), self.editors.all(), self.users.all()))

    def badge_count(self):
        """
        Returns the number of badges associated with this structure
        """
        return self.issued_badges.count()

    def is_admin(self, user):
        """
        Return true if the user is admin of the structure or a superuser
        """
        return self.admins.filter(pk=user.pk).exists() or user.is_superuser

    def is_editor(self, user):
        """
        Return true if the user is admin of the structure or a superuser
        """
        return self.editors.filter(pk=user.pk).exists() or user.is_superuser


class Badge(models.Model):
    """
    Model representing a badge
    """

    uuid = models.UUIDField(default=uuid.uuid7, primary_key=True, db_index=True)

    LEVEL_CHOICES = [
        ('beginner', 'Débutant'),
        ('intermediate', 'Intermédiaire'),
        ('expert', 'Expert'),
    ]

    name = models.CharField(max_length=100, verbose_name="Nom")
    icon_width = models.PositiveIntegerField(blank=True, null=True, editable=False)
    icon_height = models.PositiveIntegerField(blank=True, null=True, editable=False)
    icon = PictureField(upload_to='badges/icons/', blank=True, null=True, verbose_name="Icône", 
                       aspect_ratios=[None, "1/1"], width_field='icon_width', height_field='icon_height')
    level = models.CharField(max_length=20, choices=LEVEL_CHOICES, verbose_name="Niveau")
    description = models.TextField(verbose_name="Description")

    # Relationships
    issuing_structure = models.ForeignKey(
        Structure, 
        on_delete=models.CASCADE, 
        related_name='issued_badges',
        verbose_name="Structure émettrice"
    )
    valid_structures = models.ManyToManyField(
        Structure, 
        related_name='valid_badges',
        blank=True,
        verbose_name="Structures où ce badge est valable"
    )
    # The holders relationship is now managed through the BadgeAssignment model
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Date de création")

    class Meta:
        verbose_name = "Badge"
        verbose_name_plural = "Badges"
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.get_level_display()})"

    def get_holders(self):
        """
        Returns all users who hold this badge excluding inactive users
        """
        return User.objects.filter(badge_assignments__badge=self,is_active=True)

    def get_assignments(self):
        """
        Returns all users who hold this badge excluding inactive users
        """
        return BadgeAssignment.objects.filter(badge=self)


    def add_holder(self, user, assigned_by=None, notes=None):
        """
        Adds a user as a holder of this badge
        """
        assignment, created = BadgeAssignment.objects.get_or_create(
            badge=self,
            user=user,
            defaults={
                'assigned_by': assigned_by,
                'notes': notes
            }
        )
        return assignment

    def remove_holder(self, user):
        """
        Removes a user as a holder of this badge
        """
        BadgeAssignment.objects.filter(badge=self, user=user).delete()


class BadgeHistory(models.Model):
    """
    Model to track the history of a badge (creation, modifications)
    """

    uuid = models.UUIDField(default=uuid.uuid7, primary_key=True, db_index=True)

    badge = models.ForeignKey(Badge, on_delete=models.CASCADE, related_name='history', verbose_name="Badge")
    action = models.CharField(max_length=50, verbose_name="Action")
    timestamp = models.DateTimeField(default=timezone.now, verbose_name="Date et heure")
    details = models.TextField(blank=True, null=True, verbose_name="Détails")

    class Meta:
        verbose_name = "Historique de badge"
        verbose_name_plural = "Historiques de badges"
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.action} - {self.badge.name} - {self.timestamp.strftime('%d/%m/%Y %H:%M')}"


class BadgeAssignment(models.Model):
    """
    Model to track when a user receives a badge
    """

    uuid = models.UUIDField(default=uuid.uuid7, primary_key=True)

    badge = models.ForeignKey(Badge, on_delete=models.CASCADE, related_name='assignments', verbose_name="Badge")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='badge_assignments', verbose_name="Utilisateur")
    assigned_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, 
                                   related_name='assigned_badges', verbose_name="Assigné par")
    assigned_structure = models.ForeignKey(Structure, on_delete=models.SET_NULL, null=True, blank=True,
                                           related_name='assigned_badges', verbose_name="Assigné par")
    assigned_date = models.DateTimeField(default=timezone.now, verbose_name="Date d'attribution")
    notes = models.TextField(blank=True, null=True, verbose_name="Notes")

    qr_code_width = models.PositiveIntegerField(blank=True, null=True, editable=False)
    qr_code_height = models.PositiveIntegerField(blank=True, null=True, editable=False)
    qr_code = PictureField(upload_to='badges/qrcodes/', blank=True, null=True, verbose_name="QR Code",
                          aspect_ratios=[None, "1/1"], width_field='qr_code_width', height_field='qr_code_height')


    class Meta:
        verbose_name = "Attribution de badge"
        verbose_name_plural = "Attributions de badges"
        ordering = ['-assigned_date']
        # Ensure a user can't receive the same badge twice
        unique_together = ['badge', 'user']

    def __str__(self):
        return f"{self.badge.name} attribué à {self.user.username} le {self.assigned_date.strftime('%d/%m/%Y')}"


class BadgeEndorsement(models.Model):
    """
    Model to track when a structure endorses a badge
    """

    uuid = models.UUIDField(default=uuid.uuid7, primary_key=True, db_index=True)

    badge = models.ForeignKey(Badge, on_delete=models.CASCADE, related_name='endorsements', verbose_name="Badge")
    structure = models.ForeignKey(Structure, on_delete=models.CASCADE, related_name='endorsed_badges', 
                                 verbose_name="Structure")
    endorsed_date = models.DateTimeField(default=timezone.now, verbose_name="Date d'approbation")
    endorsed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, 
                                   related_name='badge_endorsements', verbose_name="Approuvé par")
    notes = models.TextField(blank=True, null=True, verbose_name="Notes")

    class Meta:
        verbose_name = "Approbation de badge"
        verbose_name_plural = "Approbations de badges"
        ordering = ['-endorsed_date']
        # Ensure a structure can't endorse the same badge twice
        unique_together = ['badge', 'structure']

    def __str__(self):
        return f"{self.badge.name} approuvé par {self.structure.name} le {self.endorsed_date.strftime('%d/%m/%Y')}"
