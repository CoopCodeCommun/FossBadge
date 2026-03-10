from django.apps import AppConfig


class BadgeGeneratorConfig(AppConfig):
    """
    Configuration de l'application generateur de badges.
    Badge generator app configuration.
    """
    default_auto_field = "django.db.models.BigAutoField"
    name = "badge_generator"
    verbose_name = "Générateur de Badges"
