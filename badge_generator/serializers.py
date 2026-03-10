"""
Validation des donnees avec des Serializers DRF.
On n'utilise jamais les Django Forms. Toujours des Serializers.
Version simplifiee : 2 serializers (preview + generate).
Les couleurs sont derivees de la categorie, pas choisies par l'utilisateur.
La forme est choisie par l'utilisateur parmi les formes disponibles.

DRF Serializers for data validation. Never Django Forms.
Simplified: 2 serializers (preview + generate).
Colors come from the category, not from user input.
Shape is chosen by the user from available shapes.

LOCALISATION : badge_generator/serializers.py
"""

from rest_framework import serializers

from badge_generator.models import BadgeCategory, BadgeLevel
from badge_generator.shapes import ALL_SHAPES, DEFAULT_SHAPE_KEY


# ============================================================================
# Serializer pour la previsualisation du badge.
# On valide les choix de l'utilisateur avant de generer le SVG.
# Preview serializer: validate user choices before generating SVG.
# ============================================================================

class PreviewBadgeSerializer(serializers.Serializer):
    """
    On verifie que la categorie et le niveau existent.
    Le titre et le sous-titre sont optionnels pour la preview.
    Validate category and level exist. Title/subtitle optional for preview.
    """

    category_uuid = serializers.UUIDField(
        required=False,
        error_messages={
            "invalid": "Cette catégorie n'est pas valide. / Invalid category.",
        }
    )

    level_uuid = serializers.UUIDField(
        required=False,
        error_messages={
            "invalid": "Ce niveau n'est pas valide. / Invalid level.",
        }
    )

    title = serializers.CharField(
        max_length=100,
        required=False,
        allow_blank=True,
        default="",
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

    def validate_category_uuid(self, value):
        # Si pas de categorie fournie, c'est ok pour la preview.
        # No category is OK for preview.
        if value is None:
            return value

        category_exists = BadgeCategory.objects.filter(uuid=value).exists()
        if not category_exists:
            raise serializers.ValidationError(
                "Cette catégorie n'existe pas. / This category does not exist."
            )
        return value

    def validate_level_uuid(self, value):
        # Si pas de niveau fourni, c'est ok pour la preview.
        # No level is OK for preview.
        if value is None:
            return value

        level_exists = BadgeLevel.objects.filter(uuid=value).exists()
        if not level_exists:
            raise serializers.ValidationError(
                "Ce niveau n'existe pas. / This level does not exist."
            )
        return value

    def validate_shape(self, value):
        # Si la forme est vide ou inconnue, on prend la forme par defaut.
        # If shape is empty or unknown, use default.
        if not value or value not in ALL_SHAPES:
            return DEFAULT_SHAPE_KEY
        return value


# ============================================================================
# Serializer pour la generation finale du badge.
# La categorie, le niveau et le titre sont obligatoires.
# Generate serializer: category, level and title are required.
# ============================================================================

class GenerateBadgeSerializer(serializers.Serializer):
    """
    On rassemble tous les choix de l'utilisateur pour generer le badge.
    La categorie et le niveau sont obligatoires.
    Le titre est obligatoire. Le sous-titre est optionnel.
    Collect all user choices. Category, level and title are required.
    """

    category_uuid = serializers.UUIDField(
        error_messages={
            "required": "Veuillez choisir une catégorie. / Please choose a category.",
            "invalid": "Cette catégorie n'est pas valide. / Invalid category.",
        }
    )

    level_uuid = serializers.UUIDField(
        error_messages={
            "required": "Veuillez choisir un niveau. / Please choose a level.",
            "invalid": "Ce niveau n'est pas valide. / Invalid level.",
        }
    )

    title = serializers.CharField(
        max_length=100,
        error_messages={
            "required": "Le titre est obligatoire. / Title is required.",
            "max_length": "Le titre est trop long (100 caractères max). / Title too long.",
            "blank": "Le titre ne peut pas être vide. / Title cannot be empty.",
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

    def validate_category_uuid(self, value):
        # On verifie que la categorie existe.
        # Check that the category exists.
        category_exists = BadgeCategory.objects.filter(uuid=value).exists()
        if not category_exists:
            raise serializers.ValidationError(
                "Cette catégorie n'existe pas. / This category does not exist."
            )
        return value

    def validate_level_uuid(self, value):
        # On verifie que le niveau existe.
        # Check that the level exists.
        level_exists = BadgeLevel.objects.filter(uuid=value).exists()
        if not level_exists:
            raise serializers.ValidationError(
                "Ce niveau n'existe pas. / This level does not exist."
            )
        return value

    def validate_shape(self, value):
        # Si la forme est vide ou inconnue, on prend la forme par defaut.
        # If shape is empty or unknown, use default.
        if not value or value not in ALL_SHAPES:
            return DEFAULT_SHAPE_KEY
        return value
