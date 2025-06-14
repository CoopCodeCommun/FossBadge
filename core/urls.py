from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    # Home page
    path('', views.home, name='home'),

    # User list page
    path('users/', views.user_list, name='user_list'),

    # User profile page
    path('user/', views.user_profile, name='user_profile'),

    # Badge list page
    path('badges/', views.badge_list, name='badge_list'),

    # Badge detail page
    path('badge/', views.badge_detail, name='badge_detail'),

    # Structure list page
    path('structures/', views.structure_list, name='structure_list'),

    # Structure/company detail page
    path('structure/', views.association_detail, name='association_detail'),

    # Badge creation page
    path('badge/create/', views.create_badge, name='create_badge'),

    # Structure/company creation page
    path('structure/create/', views.create_association, name='create_association'),
]
