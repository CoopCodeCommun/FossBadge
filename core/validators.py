from django.shortcuts import get_object_or_404
from rest_framework import serializers

from core.admin import StructureAdmin
from core.models import Badge, User, Structure
from mapview.models import Marker


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
