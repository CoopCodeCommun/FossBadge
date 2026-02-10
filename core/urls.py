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

# The API URLs are now determined automatically by the router
urlpatterns = [
    path('', include(router.urls)),

    # Custom action URLs that don't fit the standard pattern
    # Creation routes
    path('badge/create/', views.BadgeViewSet.as_view({'get': 'create_badge', 'post': 'create_badge'}), name='create_badge'),
    path('structure/create/', views.StructureViewSet.as_view({'get': 'create_association', 'post': 'create_association'}), name='create_association'),
    path('user/create/',views.UserViewSet.as_view({'get': 'create_user', 'post': 'create_user'}),name='create_user'),

    # Edition routes
    path('users/<uuid:pk>/edit', views.UserViewSet.as_view({'get': 'edit', 'post': 'edit'}), name='edit-profile')
]
