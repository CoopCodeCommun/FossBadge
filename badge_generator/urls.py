"""
Configuration des URLs du generateur de badges.
Le router fabrique les URLs tout seul a partir du ViewSet.
URL configuration for the badge generator. Router auto-generates URLs.
"""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from badge_generator.views import BadgeGeneratorViewSet


# On cree un router qui va fabriquer toutes les URLs.
# Le basename "badge-generator" est utilise pour nommer les URLs.
# Router creates all URLs. Basename used for URL naming.
router = DefaultRouter()
router.register(r"", BadgeGeneratorViewSet, basename="badge-generator")

app_name = "badge_generator"

urlpatterns = [
    # Toutes les URLs sont gerees par le router.
    # All URLs managed by the router.
    path("", include(router.urls)),
]
