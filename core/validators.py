from django.shortcuts import get_object_or_404
from rest_framework import serializers

from badge_generator.models import BadgeLevel, BadgeCategory
from badge_generator.shapes import DEFAULT_SHAPE_KEY, ALL_SHAPES
from core.admin import StructureAdmin
from core.models import Badge, User, Structure
from mapview.models import Marker
from django.utils.translation import gettext_lazy as _


class BadgeAssignmentValidator(serializers.Serializer):
    """
    Valide les donnees pour assigner un badge a un utilisateur.
    L'email est utilise pour identifier ou creer l'utilisateur.
    / Validates data for assigning a badge to a user.
    Email is used to identify or create the user.
    """
    badge = serializers.UUIDField()
    assigned_email = serializers.EmailField(
        error_messages={
            'required': 'L\'email est obligatoire',
            'invalid': 'Veuillez entrer un email valide',
        }
    )
    assigned_by_structure = serializers.UUIDField()
    assigned_by_user = serializers.UUIDField()
    notes = serializers.CharField()

    def validate_badge(self, value):
        try:
            Badge.objects.get(pk=value)
        except Exception:
            raise serializers.ValidationError("Le badge n'existe pas")
        return value

    def validate_assigned_by_structure(self, value):
        try:
            Structure.objects.get(pk=value)
        except Exception:
            raise serializers.ValidationError("La structure n'existe pas")
        return value

    def validate_assigned_by_user(self, value):
        try:
            User.objects.get(pk=value)
        except Exception:
            raise serializers.ValidationError("L'utilisateur n'existe pas")
        return value

    def validate(self, data):
        # Verifie que l'utilisateur est admin de la structure
        # / Check that the user is admin of the structure
        try:
            structure = Structure.objects.get(pk=data['assigned_by_structure'])
            user = User.objects.get(pk=data['assigned_by_user'])
        except Exception:
            return data

        if not structure.is_admin(user):
            raise serializers.ValidationError(
                "Vous devez être admin de cette structure pour attribuer un badge"
            )
        return data


class BadgeSelfAssignmentValidator(serializers.Serializer):
    notes = serializers.CharField(required=True)


class BadgeEndorsementValidator(serializers.Serializer):
    """
    Valide les donnees pour endosser un badge.
    Verifie que l'utilisateur est bien admin de la structure choisie.
    / Validates data for endorsing a badge.
    Checks that the user is admin of the chosen structure.
    """
    badge = serializers.UUIDField()
    structure = serializers.UUIDField()
    endorsed_by = serializers.UUIDField()
    notes = serializers.CharField()

    def validate_badge(self, value):
        try:
            Badge.objects.get(pk=value)
        except Exception:
            raise serializers.ValidationError("Le badge n'existe pas")
        return value

    def validate_structure(self, value):
        try:
            Structure.objects.get(pk=value)
        except Exception:
            raise serializers.ValidationError("La structure n'existe pas")
        return value

    def validate_endorsed_by(self, value):
        try:
            User.objects.get(pk=value)
        except Exception:
            raise serializers.ValidationError("L'utilisateur n'existe pas")
        return value

    def validate(self, data):
        # Verifie que l'utilisateur est admin de la structure
        # / Check that the user is admin of the structure
        try:
            structure = Structure.objects.get(pk=data['structure'])
            user = User.objects.get(pk=data['endorsed_by'])
        except Exception:
            return data

        if not structure.is_admin(user):
            raise serializers.ValidationError(
                "Vous devez être admin de cette structure pour endosser un badge"
            )
        return data


class DreamBadgeValidator(serializers.Serializer):
    name = serializers.CharField(required=True)
    icon = serializers.ImageField(required=False)
    description = serializers.CharField()


class InviteUserValidator(serializers.Serializer):
    """
    Validator for user invite from a structure
    """
    email = serializers.EmailField()
    role = serializers.ChoiceField(choices=Structure.ROLES)


class CreateCourseValidator(serializers.Serializer):
    """
    Validator for creating a course
    """
    structure = serializers.UUIDField()
    badge = serializers.UUIDField()

class CreateStructureValidator(serializers.Serializer):
    """
    Validator for creating a structure
    """

    def create(self, validated_data):
        data = validated_data
        longitude = data.pop("longitude", None)
        latitude = data.pop("latitude", None)

        structure = Structure.objects.create(**data)

        if longitude and latitude:
            marker = Marker.objects.create(latitude=latitude, longitude=longitude)
            structure.marker = marker
            structure.save()

        return structure

    def update(self, instance, validated_data):
        longitude = validated_data.get("longitude", None)
        latitude = validated_data.get("latitude", None)

        instance.name = validated_data.get('name', instance.name)
        instance.description = validated_data.get('description', instance.description)
        instance.type = validated_data.get('type', instance.type)
        instance.siret = validated_data.get('siret', instance.siret)
        instance.referent_last_name = validated_data.get('referent_last_name', instance.referent_last_name)
        instance.referent_first_name = validated_data.get('referent_first_name', instance.referent_first_name)
        instance.referent_position = validated_data.get('referent_position', instance.referent_position)
        instance.address = validated_data.get('address', instance.address)

        # LOGO ?
        instance.logo = validated_data.get('logo', instance.logo)

        if longitude and latitude:
            if instance.marker:
                instance.marker.longitude = longitude
                instance.marker.latitude = latitude
                instance.marker.save()
            else:
                marker = Marker.objects.create(latitude=latitude, longitude=longitude)
                instance.marker = marker

        instance.save()
        return instance

    name = serializers.CharField(required=True)
    description = serializers.CharField(required=True)

    logo = serializers.ImageField(required=False)
    type = serializers.ChoiceField(choices=Structure.TYPE_CHOICES)

    siret = serializers.CharField(required=False)

    # Referent info
    referent_last_name = serializers.CharField(required=True, max_length=100)
    referent_first_name = serializers.CharField(required=True, max_length=100)
    referent_position = serializers.CharField(required=True, max_length=100)

    # Location info
    address = serializers.CharField(required=True)

    # Marker info
    latitude = serializers.FloatField(required=False)
    longitude = serializers.FloatField(required=False)

class CreateBadgeValidator(serializers.Serializer):
    """
    Validator for creating a badge and an associated icon
    The request context MUST be populated.
    """

    category_uuid = serializers.UUIDField(
        error_messages={
            "required": _("Veuillez choisir une catégorie."),
            "invalid": _("Cette catégorie n'est pas valide."),
        }
    )

    level_uuid = serializers.UUIDField(
        error_messages={
            "required": _("Veuillez choisir un niveau."),
            "invalid": _("Ce niveau n'est pas valide."),
        }
    )

    title = serializers.CharField(
        max_length=100,
        error_messages={
            "required": _("Le titre est obligatoire."),
            "max_length": _("Le titre est trop long (100 caractères max)."),
            "blank": _("Le titre ne peut pas être vide."),
        }
    )

    subtitle = serializers.CharField(
        max_length=100,
        required=False,
        allow_blank=True,
        default="",
    )

    # La forme choisie par l'utilisateur. Par defaut "starburst".
    # Shape chosen by the user. Default is "starburst".
    shape = serializers.CharField(
        max_length=30,
        required=False,
        allow_blank=True,
        default=DEFAULT_SHAPE_KEY,
    )

    description = serializers.CharField()

    criteria = serializers.CharField()

    creator_type = serializers.CharField(
        error_messages={
            "blank" : _("Veuillez choisir une option"),
            "invalid": _("Cette option n'est pas valide."),
        }
    )

    structure_uuid = serializers.CharField(
        error_messages={
            "required": _("Veuillez choisir une structure."),
            "invalid": _("Cette structure n'est pas valide."),
        },
        required=False,
    )

    def validate_category_uuid(self, value):
        # On verifie que la categorie existe.
        # Check that the category exists.
        category_exists = BadgeCategory.objects.filter(uuid=value).exists()
        if not category_exists:
            raise serializers.ValidationError(
                _("Cette catégorie n'existe pas.")
            )
        return value

    def validate_level_uuid(self, value):
        # On verifie que le niveau existe.
        # Check that the level exists.
        level_exists = BadgeLevel.objects.filter(uuid=value).exists()
        if not level_exists:
            raise serializers.ValidationError(
                _("Ce niveau n'existe pas.")
            )
        return value

    def validate_creator_type(self,value):
        if value == "structure" or value == "user":
            return value

        raise serializers.ValidationError(_("Vous devez choisir qui émet ce badge."))

    def validate_structure_uuid(self, value):
        # Check if we create the badge as a structure. If so, check if the structure is valid.
        # print(self.initial_data["user"])
        if self.initial_data['creator_type'] == "structure":
            structure = Structure.objects.filter(uuid=value)
            structure_exist = structure.exists()
            if not structure_exist:
                raise serializers.ValidationError("Veuillez choisir une structure valide.")


            user = self.context["request"].user
            print(user)
            print(structure[0])
            print(structure[0].is_editor(user))
            if not structure[0].is_editor(user):
                raise serializers.ValidationError(_("Vous n'êtes pas éditeur de cette structure."))

        return value

    def validate_shape(self, value):
        # Si la forme est vide ou inconnue, on prend la forme par defaut.
        # If shape is empty or unknown, use default.
        if not value or value not in ALL_SHAPES:
            return DEFAULT_SHAPE_KEY
        return value
