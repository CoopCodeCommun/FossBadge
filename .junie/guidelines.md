# FossBadge - Guidelines de Développement

## Table des matières

1. [Introduction](#introduction)
2. [Structure du Projet](#structure-du-projet)
3. [Standards de Codage](#standards-de-codage)
4. [Tests](#tests)
5. [Documentation](#documentation)
6. [Accessibilité (FALC)](#accessibilité-falc)
7. [Technologies](#technologies)
8. [Déploiement](#déploiement)
9. Django Gideline

## Introduction

Ce document contient les guidelines pour le développement du projet FossBadge. Il est destiné à tous les contributeurs du projet et vise à maintenir une cohérence dans le code et les pratiques de développement.

FossBadge est une plateforme libre et open source pour créer, gérer et partager des badges numériques. Elle permet aux organisations de reconnaître les compétences et les réalisations à travers une interface simple et accessible.

## Structure du Projet

```
fossbadge/
├── core/                  # Application principale
│   ├── migrations/        # Migrations de base de données
│   ├── templates/         # Templates spécifiques à l'application
│   ├── admin.py           # Configuration de l'admin Django
│   ├── apps.py            # Configuration de l'application
│   ├── models.py          # Modèles de données
│   ├── tests.py           # Tests unitaires
│   ├── urls.py            # Configuration des URLs
│   └── views.py           # Vues de l'application
├── fossbadge/             # Configuration du projet
│   ├── settings.py        # Paramètres du projet
│   ├── urls.py            # URLs du projet
│   ├── asgi.py            # Configuration ASGI
│   └── wsgi.py            # Configuration WSGI
├── static/                # Fichiers statiques
│   ├── bootstrap/         # Fichiers Bootstrap
│   ├── css/               # Fichiers CSS personnalisés
│   └── js/                # Fichiers JavaScript personnalisés
├── templates/             # Templates globaux
│   ├── base.html          # Template de base
│   └── includes/          # Composants réutilisables
├── media/                 # Fichiers téléchargés par les utilisateurs
├── .junie/                # Configuration et documentation spécifiques
├── manage.py              # Script de gestion Django
├── pyproject.toml         # Configuration Poetry
├── README.md              # Documentation principale
└── .gitignore             # Configuration Git
```

## Standards de Codage

### Python

- Suivre la [PEP 8](https://www.python.org/dev/peps/pep-0008/) pour le style de code Python
- Utiliser des docstrings pour documenter les fonctions, classes et méthodes
- Limiter les lignes à 100 caractères maximum
- Utiliser des noms de variables et de fonctions explicites
- Préférer les fonctions et classes courtes et focalisées

Exemple:

```python
def get_user_badges(user_id):
    """
    Récupère tous les badges d'un utilisateur.
    
    Args:
        user_id (int): L'ID de l'utilisateur
        
    Returns:
        QuerySet: Les badges de l'utilisateur
    """
    return Badge.objects.filter(user_id=user_id)
```

### HTML/CSS

- Utiliser des indentations de 4 espaces
- Utiliser des classes Bootstrap 5 autant que possible
- Suivre les principes FALC pour l'accessibilité
- Utiliser des templates Django avec héritage
- Séparer les composants réutilisables dans des fichiers include
- Utiliser HTMX pour la relation avec le serveur

Exemple:

```html
{% extends 'base.html' %}

{% block title %}Titre de la Page{% endblock %}

{% block content %}
<div class="container">
    <h1 class="display-4">Titre Principal</h1>
    <p class="lead">Description claire et concise.</p>
    
    {% include 'includes/component.html' %}
</div>
{% endblock %}
```

## Tests

- Écrire des tests unitaires pour toutes les fonctionnalités
- Viser une couverture de code d'au moins 80%
- Utiliser le framework de test de Django
- Exécuter les tests avant chaque commit

Exemple:

```python
from django.test import TestCase
from django.urls import reverse

class HomePageTest(TestCase):
    def test_home_page_loads_correctly(self):
        response = self.client.get(reverse('core:home'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/index.html')
```

## Documentation

- Documenter toutes les fonctions, classes et méthodes avec des docstrings
- Maintenir à jour le README.md avec les informations essentielles
- Créer des documents spécifiques pour les fonctionnalités complexes
- Documenter les changements importants dans les messages de commit

## Accessibilité (FALC)

Suivre les principes FALC (Facile à Lire et à Comprendre):

- Utiliser un langage simple et direct
- Éviter le jargon technique dans l'interface utilisateur
- Utiliser des contrastes élevés pour le texte
- Créer des éléments d'interface larges et facilement cliquables
- S'assurer que l'interface est navigable au clavier
- Utiliser des attributs ARIA appropriés
- Tester régulièrement l'accessibilité

Exemple CSS:

```css
/* Augmenter la taille des boutons pour faciliter le clic */
.btn {
    padding: 0.75rem 1.5rem;
    font-size: 1.1rem;
}

/* Assurer un contraste suffisant */
.high-contrast {
    color: #000;
    background-color: #fff;
    border: 1px solid #000;
}
```

## Technologies

- **Backend**: Django 5.2+
- **Frontend**: Bootstrap 5, HTMX
- **Base de données**: SQLite (développement), PostgreSQL (production)
- **Gestion des dépendances**: Poetry
- **Tests**: Django Test Framework

## Déploiement

- Utiliser des variables d'environnement pour les configurations sensibles
- Suivre la checklist de déploiement Django
- Configurer correctement les fichiers statiques
- Mettre en place des sauvegardes régulières de la base de données
- Utiliser HTTPS pour toutes les communications

---

# Django Guidelines

You are an expert in Python, Django, and scalable web application development. You write secure, maintainable, and performant code following Django and Python best practices.

## Python Best Practices
- Follow PEP 8 with 120 character line limit
- Use double quotes for Python strings
- Sort imports with `isort`
- Use f-strings for string formatting

## Django Best Practices
- Follow Django's "batteries included" philosophy - use built-in features before third-party packages
- Prioritize security and follow Django's security best practices
- Use Django's ORM effectively and avoid raw SQL unless absolutely necessary
- Use Django signals sparingly and document them well.

## Models
- Add `__str__` methods to all models for a better admin interface
- Use `related_name` for foreign keys when needed
- Define `Meta` class with appropriate options (ordering, verbose_name, etc.)
- Use `blank=True` for optional form fields, `null=True` for optional database fields

## Views
- Always validate and sanitize user input
- Handle exceptions gracefully with try/except blocks
- Use `get_object_or_404` instead of manual exception handling
- Implement proper pagination for list views

## URLs
- Use descriptive URL names for reverse URL lookups
- Always end URL patterns with a trailing slash

## Forms
- Use ModelForms when working with model instances
- Use crispy forms or similar for better form rendering

## Templates
- Use template inheritance with base templates
- Use template tags and filters for common operations
- Avoid complex logic in templates - move it to views or template tags
- Use static files properly with `{% load static %}`
- Implement CSRF protection in all forms

## Settings
- Use environment variables in a single `settings.py` file
- Never commit secrets to version control

## Database
- Use migrations for all database changes
- Optimize queries with `select_related` and `prefetch_related`
- Use database indexes for frequently queried fields
- Avoid N+1 query problems

## Testing
- Always write unit tests and check that they pass for new features
- Test both positive and negative scenarios

Ces guidelines sont évolutives et peuvent être mises à jour selon les besoins du projet. Tous les contributeurs sont encouragés à proposer des améliorations à ce document.