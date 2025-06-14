# Explication des Tests

Ce document explique en français ce que font tous les tests présents dans le projet FossBadge.

## Tests de la Page d'Accueil (`core/tests.py`)

La classe `HomePageTest` contient trois méthodes de test qui vérifient différents aspects de la page d'accueil :

### 1. `test_home_page_loads_correctly`

**Objectif** : Vérifier que la page d'accueil se charge correctement.

**Description** : Ce test envoie une requête GET à l'URL de la page d'accueil et vérifie que le code de statut de la réponse est 200 (OK). Un code 200 indique que la page a été chargée avec succès sans erreur.

**Fonctionnement** :
- Utilise le client de test Django pour simuler une requête GET à l'URL 'core:home'
- Vérifie que le code de statut de la réponse est 200

### 2. `test_home_page_uses_correct_template`

**Objectif** : Vérifier que la page d'accueil utilise les bons templates.

**Description** : Ce test vérifie que la vue de la page d'accueil utilise les templates corrects pour le rendu de la page. Il s'assure que les templates 'core/index.html' et 'base.html' sont utilisés.

**Fonctionnement** :
- Envoie une requête GET à l'URL de la page d'accueil
- Vérifie que le template 'core/index.html' est utilisé pour le rendu
- Vérifie que le template 'base.html' est également utilisé (car 'index.html' étend 'base.html')

### 3. `test_home_page_contains_static_files`

**Objectif** : Vérifier que la page d'accueil contient des références à tous les fichiers statiques requis.

**Description** : Ce test s'assure que le HTML généré pour la page d'accueil contient des références à tous les fichiers statiques nécessaires au bon fonctionnement de l'application.

**Fonctionnement** :
- Envoie une requête GET à l'URL de la page d'accueil
- Décode le contenu de la réponse en UTF-8
- Vérifie que le contenu contient une référence à 'bootstrap.min.css' (CSS de Bootstrap)
- Vérifie que le contenu contient une référence à 'bootstrap.bundle.min.js' (JavaScript de Bootstrap)
- Vérifie que le contenu contient une référence à 'htmx.min.js' (HTMX)
- Vérifie que le contenu contient une référence à 'custom.css' (CSS personnalisé)

Ces tests garantissent que la page d'accueil fonctionne correctement, utilise les bons templates et inclut tous les fichiers statiques nécessaires.

## Tests de la Page Profil Utilisateur (`core/tests.py`)

La classe `UserProfileTest` contient trois méthodes de test qui vérifient différents aspects de la page profil utilisateur :

### 1. `test_user_profile_page_loads_correctly`

**Objectif** : Vérifier que la page profil utilisateur se charge correctement.

**Description** : Ce test envoie une requête GET à l'URL de la page profil utilisateur et vérifie que le code de statut de la réponse est 200 (OK).

**Fonctionnement** :
- Utilise le client de test Django pour simuler une requête GET à l'URL 'core:user_profile'
- Vérifie que le code de statut de la réponse est 200

### 2. `test_user_profile_page_uses_correct_template`

**Objectif** : Vérifier que la page profil utilisateur utilise les bons templates.

**Description** : Ce test vérifie que la vue de la page profil utilisateur utilise les templates corrects pour le rendu de la page.

**Fonctionnement** :
- Envoie une requête GET à l'URL de la page profil utilisateur
- Vérifie que le template 'core/user.html' est utilisé pour le rendu
- Vérifie que le template 'base.html' est également utilisé

### 3. `test_user_profile_page_contains_expected_content`

**Objectif** : Vérifier que la page profil utilisateur contient le contenu attendu.

**Description** : Ce test s'assure que le HTML généré pour la page profil utilisateur contient les éléments spécifiques attendus pour cette page.

**Fonctionnement** :
- Envoie une requête GET à l'URL de la page profil utilisateur
- Décode le contenu de la réponse en UTF-8
- Vérifie que le contenu contient les éléments spécifiques au profil utilisateur comme 'Profil Utilisateur', 'Informations personnelles', 'Mes badges', et 'Mes associations'

## Tests de la Page Détail de Badge (`core/tests.py`)

La classe `BadgeDetailTest` contient trois méthodes de test qui vérifient différents aspects de la page détail de badge :

### 1. `test_badge_detail_page_loads_correctly`

**Objectif** : Vérifier que la page détail de badge se charge correctement.

**Description** : Ce test envoie une requête GET à l'URL de la page détail de badge et vérifie que le code de statut de la réponse est 200 (OK).

**Fonctionnement** :
- Utilise le client de test Django pour simuler une requête GET à l'URL 'core:badge_detail'
- Vérifie que le code de statut de la réponse est 200

### 2. `test_badge_detail_page_uses_correct_template`

**Objectif** : Vérifier que la page détail de badge utilise les bons templates.

**Description** : Ce test vérifie que la vue de la page détail de badge utilise les templates corrects pour le rendu de la page.

**Fonctionnement** :
- Envoie une requête GET à l'URL de la page détail de badge
- Vérifie que le template 'core/badge.html' est utilisé pour le rendu
- Vérifie que le template 'base.html' est également utilisé

### 3. `test_badge_detail_page_contains_expected_content`

**Objectif** : Vérifier que la page détail de badge contient le contenu attendu.

**Description** : Ce test s'assure que le HTML généré pour la page détail de badge contient les éléments spécifiques attendus pour cette page.

**Fonctionnement** :
- Envoie une requête GET à l'URL de la page détail de badge
- Décode le contenu de la réponse en UTF-8
- Vérifie que le contenu contient les éléments spécifiques au détail de badge comme 'Détails du Badge', 'QR Code', 'Structures où ce badge est valable', et 'Ce badge est rattaché à d\'autres personnes'

## Tests de la Page Détail d'Association (`core/tests.py`)

La classe `AssociationDetailTest` contient trois méthodes de test qui vérifient différents aspects de la page détail d'association :

### 1. `test_association_detail_page_loads_correctly`

**Objectif** : Vérifier que la page détail d'association se charge correctement.

**Description** : Ce test envoie une requête GET à l'URL de la page détail d'association et vérifie que le code de statut de la réponse est 200 (OK).

**Fonctionnement** :
- Utilise le client de test Django pour simuler une requête GET à l'URL 'core:association_detail'
- Vérifie que le code de statut de la réponse est 200

### 2. `test_association_detail_page_uses_correct_template`

**Objectif** : Vérifier que la page détail d'association utilise les bons templates.

**Description** : Ce test vérifie que la vue de la page détail d'association utilise les templates corrects pour le rendu de la page.

**Fonctionnement** :
- Envoie une requête GET à l'URL de la page détail d'association
- Vérifie que le template 'core/association.html' est utilisé pour le rendu
- Vérifie que le template 'base.html' est également utilisé

### 3. `test_association_detail_page_contains_expected_content`

**Objectif** : Vérifier que la page détail d'association contient le contenu attendu.

**Description** : Ce test s'assure que le HTML généré pour la page détail d'association contient les éléments spécifiques attendus pour cette page.

**Fonctionnement** :
- Envoie une requête GET à l'URL de la page détail d'association
- Décode le contenu de la réponse en UTF-8
- Vérifie que le contenu contient les éléments spécifiques au détail d'association comme 'Association / Entreprise', 'Forger un nouveau badge', 'Localisation', et 'Badges disponibles'

## Tests de la Page Création de Badge (`core/tests.py`)

La classe `CreateBadgeTest` contient trois méthodes de test qui vérifient différents aspects de la page création de badge :

### 1. `test_create_badge_page_loads_correctly`

**Objectif** : Vérifier que la page création de badge se charge correctement.

**Description** : Ce test envoie une requête GET à l'URL de la page création de badge et vérifie que le code de statut de la réponse est 200 (OK).

**Fonctionnement** :
- Utilise le client de test Django pour simuler une requête GET à l'URL 'core:create_badge'
- Vérifie que le code de statut de la réponse est 200

### 2. `test_create_badge_page_uses_correct_template`

**Objectif** : Vérifier que la page création de badge utilise les bons templates.

**Description** : Ce test vérifie que la vue de la page création de badge utilise les templates corrects pour le rendu de la page.

**Fonctionnement** :
- Envoie une requête GET à l'URL de la page création de badge
- Vérifie que le template 'core/create_badge.html' est utilisé pour le rendu
- Vérifie que le template 'base.html' est également utilisé

### 3. `test_create_badge_page_contains_expected_content`

**Objectif** : Vérifier que la page création de badge contient le contenu attendu.

**Description** : Ce test s'assure que le HTML généré pour la page création de badge contient les éléments spécifiques attendus pour cette page.

**Fonctionnement** :
- Envoie une requête GET à l'URL de la page création de badge
- Décode le contenu de la réponse en UTF-8
- Vérifie que le contenu contient les éléments spécifiques à la création de badge comme 'Forger un nouveau Badge', 'Icône du badge', 'Nom du badge', 'Niveau', et 'Description courte'

## Tests de la Page Création d'Association (`core/tests.py`)

La classe `CreateAssociationTest` contient trois méthodes de test qui vérifient différents aspects de la page création d'association :

### 1. `test_create_association_page_loads_correctly`

**Objectif** : Vérifier que la page création d'association se charge correctement.

**Description** : Ce test envoie une requête GET à l'URL de la page création d'association et vérifie que le code de statut de la réponse est 200 (OK).

**Fonctionnement** :
- Utilise le client de test Django pour simuler une requête GET à l'URL 'core:create_association'
- Vérifie que le code de statut de la réponse est 200

### 2. `test_create_association_page_uses_correct_template`

**Objectif** : Vérifier que la page création d'association utilise les bons templates.

**Description** : Ce test vérifie que la vue de la page création d'association utilise les templates corrects pour le rendu de la page.

**Fonctionnement** :
- Envoie une requête GET à l'URL de la page création d'association
- Vérifie que le template 'core/create_association.html' est utilisé pour le rendu
- Vérifie que le template 'base.html' est également utilisé

### 3. `test_create_association_page_contains_expected_content`

**Objectif** : Vérifier que la page création d'association contient le contenu attendu.

**Description** : Ce test s'assure que le HTML généré pour la page création d'association contient les éléments spécifiques attendus pour cette page.

**Fonctionnement** :
- Envoie une requête GET à l'URL de la page création d'association
- Décode le contenu de la réponse en UTF-8
- Vérifie que le contenu contient les éléments spécifiques à la création d'association comme 'Créer une Association / Entreprise', 'Informations générales', 'Personne référente', 'Nom de l\'association/entreprise', et 'Numéro SIREN/SIRET'
