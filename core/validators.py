from django.shortcuts import get_object_or_404
from rest_framework import serializers

from core.admin import StructureAdmin
from core.models import Badge, User, Structure


class BadgeAssignmentValidator(serializers.Serializer):
    badge = serializers.UUIDField()
    assigned_user = serializers.UUIDField()
    assigned_by_structure = serializers.UUIDField()
    assigned_by_user = serializers.UUIDField()
    notes = serializers.CharField()

    def validate_badge(self, value):
        try:
            badge = Badge.objects.get(pk=value)
        except Exception:
            raise serializers.ValidationError("Le badge n'existe pas")
        return value

    def validate_assigned_user(self, value):
        try:
            user = User.objects.get(pk=value)
        except Exception:
            raise serializers.ValidationError("L'utilisateur n'existe pas")
        return value

    def validate_assigned_by_structure(self, value):
        try:
            structure = Structure.objects.get(pk=value)
        except Exception:
            raise serializers.ValidationError("La structure n'existe pas")
        return value

    def validate_assigned_by_user(self, value):
        try:
            user = User.objects.get(pk=value)
        except Exception:
            raise serializers.ValidationError("L'utilisateur n'existe pas")
        return value

    def validate(self, data):

        return data

class BadgeEndorsementValidator(serializers.Serializer):
    badge = serializers.UUIDField()
    structure = serializers.UUIDField()
    endorsed_by = serializers.UUIDField()
    notes = serializers.CharField()

    def validate_badge(self, value):
        try:
            badge = Badge.objects.get(pk=value)
        except Exception:
            raise serializers.ValidationError("Le badge n'existe pas")
        return value


    def validate_structure(self, value):
        try:
            structure = Structure.objects.get(pk=value)
        except Exception:
            raise serializers.ValidationError("La structure n'existe pas")
        return value

    def validate_endorsed_by(self, value):
        try:
            user = User.objects.get(pk=value)
        except Exception:
            raise serializers.ValidationError("L'utilisateur n'existe pas")
        return value

    def validate(self, data):

        return data
