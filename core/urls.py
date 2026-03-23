from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'core'

# Create a router and register our viewsets with it
router = DefaultRouter()
router.register(r'', views.HomeViewSet, basename='home')
router.register(r'badges', views.BadgeViewSet, basename='badge')
router.register(r'structures', views.StructureViewSet, basename='structure')
router.register(r'users', views.UserViewSet, basename='user')
router.register(r'assignments', views.AssignmentViewSet, basename='assignment')
router.register(r'courses', views.CourseViewSet, basename='course')

# Les routes custom doivent être AVANT le router.
# Le router HomeViewSet a un pattern "badge/<pk>/" qui capturerait "badge/create/".
# / Custom routes must come BEFORE the router to avoid being caught by "badge/<pk>/".
urlpatterns = [
    # Creation routes
    path('badge/create/', views.BadgeViewSet.as_view({'get': 'create_badge', 'post': 'create_badge'}), name='create_badge'),
    path('structure/create/', views.StructureViewSet.as_view({'get': 'create_association', 'post': 'create_association'}), name='create_association'),

    # Edition routes
    path('users/<uuid:pk>/edit', views.UserViewSet.as_view({'get': 'edit', 'post': 'edit'}), name='edit-profile'),

    # Router URLs (après les routes custom)
    # / Router URLs (after custom routes)
    path('', include(router.urls)),

    # Test path for the errors pages
    path('404', views.raise404),
    path('403', views.raise403),

]
