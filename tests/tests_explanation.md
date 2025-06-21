# Explication des Tests

Ce document explique en français ce que font tous les tests présents dans le projet FossBadge.

## Organisation des Tests

Les tests sont organisés dans un dossier `tests` à la racine du projet, avec des sous-dossiers correspondant aux applications Django. Actuellement, tous les tests concernent l'application `core` et sont donc dans le dossier `tests/core/`.

Chaque fichier de test correspond à une fonctionnalité ou à un aspect spécifique de l'application :

- `test_home.py` : Tests de la page d'accueil
- `test_user_profile.py` : Tests de la page profil utilisateur
- `test_badge_detail.py` : Tests de la page détail de badge
- `test_structure_detail.py` : Tests de la page détail de structure
- `test_create_badge.py` : Tests de la page création de badge
- `test_create_structure.py` : Tests de la page création de structure
- `test_image_display.py` : Tests de l'affichage des images
- `test_badge_search_filter.py` : Tests de la recherche et du filtrage des badges

## Tests de la Page d'Accueil (`tests/core/test_home.py`)

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

## Tests de la Page Profil Utilisateur (`tests/core/test_user_profile.py`)

La classe `UserProfileTest` contient plusieurs méthodes de test qui vérifient différents aspects de la page profil utilisateur :

### 1. `test_user_profile_page_loads_correctly`

**Objectif** : Vérifier que la page profil utilisateur se charge correctement.

**Description** : Ce test envoie une requête GET à l'URL de la page profil utilisateur et vérifie que le code de statut de la réponse est 200 (OK).

**Fonctionnement** :
- Utilise le client de test Django pour simuler une requête GET à l'URL 'core:user-detail'
- Vérifie que le code de statut de la réponse est 200

### 2. `test_user_profile_page_uses_correct_template`

**Objectif** : Vérifier que la page profil utilisateur utilise les bons templates.

**Description** : Ce test vérifie que la vue de la page profil utilisateur utilise les templates corrects pour le rendu de la page.

**Fonctionnement** :
- Envoie une requête GET à l'URL de la page profil utilisateur
- Vérifie que le template 'core/users/detail.html' est utilisé pour le rendu
- Vérifie que le template 'base.html' est également utilisé

### 3. `test_user_profile_page_contains_expected_content`

**Objectif** : Vérifier que la page profil utilisateur contient le contenu attendu.

**Description** : Ce test s'assure que le HTML généré pour la page profil utilisateur contient les éléments spécifiques attendus pour cette page.

**Fonctionnement** :
- Envoie une requête GET à l'URL de la page profil utilisateur
- Décode le contenu de la réponse en UTF-8
- Vérifie que le contenu contient les éléments spécifiques au profil utilisateur comme 'Profil de Test User', 'Informations personnelles', 'Mes badges', et 'Mes structures'

### 4. `test_user_profile_page_displays_badge_assignment_dates`

**Objectif** : Vérifier que la page profil utilisateur affiche correctement les dates d'attribution des badges.

**Description** : Ce test vérifie que les dates d'attribution des badges sont correctement affichées sur la page profil utilisateur, à la fois au format exact et au format humanisé.

**Fonctionnement** :
- Envoie une requête GET à l'URL de la page profil utilisateur
- Vérifie que le badge est affiché
- Vérifie que la date d'attribution est affichée au format exact (JJ/MM/AAAA)
- Vérifie que la date humanisée est affichée (contient "il y a")

### 5. `test_user_without_profile_page_loads_correctly`

**Objectif** : Vérifier que la page profil utilisateur se charge correctement pour un utilisateur sans profil.

**Description** : Ce test vérifie que la page profil utilisateur fonctionne correctement même pour un utilisateur qui n'a pas de profil UserProfile associé.

**Fonctionnement** :
- Envoie une requête GET à l'URL de la page profil utilisateur pour un utilisateur sans profil
- Vérifie que le code de statut de la réponse est 200
- Vérifie que le contenu contient les éléments spécifiques attendus
- Vérifie que l'image placeholder est utilisée
- Vérifie que le champ adresse est vide
- Vérifie que le message "aucun badge" est affiché

## Tests de la Page Détail de Badge (`tests/core/test_badge_detail.py`)

La classe `BadgeDetailTest` contient quatre méthodes de test qui vérifient différents aspects de la page détail de badge :

### 1. `test_badge_detail_page_loads_correctly`

**Objectif** : Vérifier que la page détail de badge se charge correctement.

**Description** : Ce test envoie une requête GET à l'URL de la page détail de badge et vérifie que le code de statut de la réponse est 200 (OK).

**Fonctionnement** :
- Utilise le client de test Django pour simuler une requête GET à l'URL 'core:badge-detail'
- Vérifie que le code de statut de la réponse est 200

### 2. `test_badge_detail_page_uses_correct_template`

**Objectif** : Vérifier que la page détail de badge utilise les bons templates.

**Description** : Ce test vérifie que la vue de la page détail de badge utilise les templates corrects pour le rendu de la page.

**Fonctionnement** :
- Envoie une requête GET à l'URL de la page détail de badge
- Vérifie que le template 'core/badges/detail.html' est utilisé pour le rendu
- Vérifie que le template 'base.html' est également utilisé

### 3. `test_badge_detail_page_contains_expected_content`

**Objectif** : Vérifier que la page détail de badge contient le contenu attendu.

**Description** : Ce test s'assure que le HTML généré pour la page détail de badge contient les éléments spécifiques attendus pour cette page.

**Fonctionnement** :
- Envoie une requête GET à l'URL de la page détail de badge
- Décode le contenu de la réponse en UTF-8
- Vérifie que le contenu contient les éléments spécifiques au détail de badge comme le nom du badge, 'QR Code', 'Structures où ce badge est valable', et 'Ce badge est rattaché à d\'autres personnes'

### 4. `test_badge_name_change_is_reflected`

**Objectif** : Vérifier que les modifications du nom du badge sont reflétées dans la page de détail.

**Description** : Ce test vérifie que lorsque le nom d'un badge est modifié dans la base de données, cette modification est correctement reflétée dans la page de détail du badge.

**Fonctionnement** :
- Modifie le nom du badge dans la base de données
- Envoie une requête GET à l'URL de la page détail de badge
- Vérifie que le nouveau nom est affiché dans la réponse

## Tests de la Page Détail de Structure (`tests/core/test_structure_detail.py`)

La classe `StructureDetailTest` contient quatre méthodes de test qui vérifient différents aspects de la page détail de structure :

### 1. `test_structure_detail_page_loads_correctly`

**Objectif** : Vérifier que la page détail de structure se charge correctement.

**Description** : Ce test envoie une requête GET à l'URL de la page détail de structure et vérifie que le code de statut de la réponse est 200 (OK).

**Fonctionnement** :
- Utilise le client de test Django pour simuler une requête GET à l'URL 'core:structure-detail'
- Vérifie que le code de statut de la réponse est 200

### 2. `test_structure_detail_page_uses_correct_template`

**Objectif** : Vérifier que la page détail de structure utilise les bons templates.

**Description** : Ce test vérifie que la vue de la page détail de structure utilise les templates corrects pour le rendu de la page.

**Fonctionnement** :
- Envoie une requête GET à l'URL de la page détail de structure
- Vérifie que le template 'core/structures/detail.html' est utilisé pour le rendu
- Vérifie que le template 'base.html' est également utilisé

### 3. `test_structure_detail_page_contains_expected_content`

**Objectif** : Vérifier que la page détail de structure contient le contenu attendu.

**Description** : Ce test s'assure que le HTML généré pour la page détail de structure contient les éléments spécifiques attendus pour cette page.

**Fonctionnement** :
- Envoie une requête GET à l'URL de la page détail de structure
- Décode le contenu de la réponse en UTF-8
- Vérifie que le contenu contient les éléments spécifiques au détail de structure comme le nom de la structure, 'Forger un nouveau badge', 'Badges disponibles', l'adresse et la description

### 4. `test_structure_name_change_is_reflected`

**Objectif** : Vérifier que les modifications du nom de la structure sont reflétées dans la page de détail.

**Description** : Ce test vérifie que lorsque le nom d'une structure est modifié dans la base de données, cette modification est correctement reflétée dans la page de détail de la structure.

**Fonctionnement** :
- Modifie le nom de la structure dans la base de données
- Envoie une requête GET à l'URL de la page détail de structure
- Vérifie que le nouveau nom est affiché dans la réponse

## Tests de la Page Création de Badge (`tests/core/test_create_badge.py`)

La classe `CreateBadgeTest` contient quatre méthodes de test qui vérifient différents aspects de la page création de badge :

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
- Vérifie que le template 'core/badges/create.html' est utilisé pour le rendu
- Vérifie que le template 'base.html' est également utilisé

### 3. `test_create_badge_page_contains_expected_content`

**Objectif** : Vérifier que la page création de badge contient le contenu attendu.

**Description** : Ce test s'assure que le HTML généré pour la page création de badge contient les éléments spécifiques attendus pour cette page.

**Fonctionnement** :
- Envoie une requête GET à l'URL de la page création de badge
- Décode le contenu de la réponse en UTF-8
- Vérifie que le contenu contient les éléments spécifiques à la création de badge comme 'Forger un nouveau Badge', 'Icône', 'Nom', 'Niveau', et 'Description'

### 4. `test_create_badge_form_submission`

**Objectif** : Vérifier que le formulaire de création de badge fonctionne correctement.

**Description** : Ce test vérifie que le formulaire de création de badge peut être soumis avec succès et que le badge est correctement créé dans la base de données.

**Fonctionnement** :
- Prépare les données du formulaire
- Crée une image de test pour l'icône du badge
- Soumet le formulaire avec les données et l'image
- Vérifie que la soumission est réussie (code 200 et redirection vers la page de détail du badge)
- Vérifie que le badge a été créé dans la base de données avec les bonnes valeurs
- Vérifie que le badge apparaît dans la liste des badges

## Tests de la Page Création de Structure (`tests/core/test_create_structure.py`)

La classe `CreateStructureTest` contient quatre méthodes de test qui vérifient différents aspects de la page création de structure :

### 1. `test_create_structure_page_loads_correctly`

**Objectif** : Vérifier que la page création de structure se charge correctement.

**Description** : Ce test envoie une requête GET à l'URL de la page création de structure et vérifie que le code de statut de la réponse est 200 (OK).

**Fonctionnement** :
- Utilise le client de test Django pour simuler une requête GET à l'URL 'core:create_association'
- Vérifie que le code de statut de la réponse est 200

### 2. `test_create_structure_page_uses_correct_template`

**Objectif** : Vérifier que la page création de structure utilise les bons templates.

**Description** : Ce test vérifie que la vue de la page création de structure utilise les templates corrects pour le rendu de la page.

**Fonctionnement** :
- Envoie une requête GET à l'URL de la page création de structure
- Vérifie que le template 'core/structures/create.html' est utilisé pour le rendu
- Vérifie que le template 'base.html' est également utilisé

### 3. `test_create_structure_page_contains_expected_content`

**Objectif** : Vérifier que la page création de structure contient le contenu attendu.

**Description** : Ce test s'assure que le HTML généré pour la page création de structure contient les éléments spécifiques attendus pour cette page.

**Fonctionnement** :
- Envoie une requête GET à l'URL de la page création de structure
- Décode le contenu de la réponse en UTF-8
- Vérifie que le contenu contient les éléments spécifiques à la création de structure comme 'Créer une Structure / Entreprise', 'Informations générales', 'Personne référente', 'Nom', et 'SIREN/SIRET'

### 4. `test_create_structure_form_submission`

**Objectif** : Vérifier que le formulaire de création de structure fonctionne correctement.

**Description** : Ce test vérifie que le formulaire de création de structure peut être soumis avec succès et que la structure est correctement créée dans la base de données.

**Fonctionnement** :
- Prépare les données du formulaire
- Crée une image de test pour le logo de la structure
- Soumet le formulaire avec les données et l'image
- Vérifie que la soumission est réussie (code 200 et redirection vers la page de détail de la structure)
- Vérifie que la structure a été créée dans la base de données avec les bonnes valeurs
- Vérifie que la structure apparaît dans la liste des structures

## Tests d'Affichage des Images (`tests/core/test_image_display.py`)

La classe `ImageDisplayTest` contient quatre méthodes de test qui vérifient l'affichage correct des images dans différentes pages :

### 1. `test_structure_detail_page_displays_image`

**Objectif** : Vérifier que la page détail de structure affiche correctement le logo de la structure.

**Description** : Ce test vérifie que le logo de la structure est correctement affiché sur la page de détail de la structure en utilisant django-pictures.

**Fonctionnement** :
- Envoie une requête GET à l'URL de la page détail de structure
- Vérifie que le HTML contient les éléments spécifiques à django-pictures comme `<picture>`, `<source type="image/webp"`, etc.
- Vérifie que le chemin vers l'image du logo est correct

### 2. `test_badge_detail_page_displays_image`

**Objectif** : Vérifier que la page détail de badge affiche correctement l'icône du badge.

**Description** : Ce test vérifie que l'icône du badge est correctement affichée sur la page de détail du badge en utilisant django-pictures.

**Fonctionnement** :
- Envoie une requête GET à l'URL de la page détail de badge
- Vérifie que le HTML contient les éléments spécifiques à django-pictures
- Vérifie que le chemin vers l'image de l'icône est correct

### 3. `test_structure_list_page_displays_images`

**Objectif** : Vérifier que la page liste des structures affiche correctement les logos des structures.

**Description** : Ce test vérifie que les logos des structures sont correctement affichés sur la page liste des structures en utilisant django-pictures.

**Fonctionnement** :
- Envoie une requête GET à l'URL de la page liste des structures
- Vérifie que le HTML contient les éléments spécifiques à django-pictures
- Vérifie que le chemin vers les images des logos est correct

### 4. `test_badge_list_page_displays_images`

**Objectif** : Vérifier que la page liste des badges affiche correctement les icônes des badges.

**Description** : Ce test vérifie que les icônes des badges sont correctement affichées sur la page liste des badges en utilisant django-pictures.

**Fonctionnement** :
- Envoie une requête GET à l'URL de la page liste des badges
- Vérifie que le HTML contient les éléments spécifiques à django-pictures
- Vérifie que le chemin vers les images des icônes est correct

## Tests de Recherche et Filtrage des Badges (`tests/core/test_badge_search_filter.py`)

La classe `BadgeSearchFilterTest` contient plusieurs méthodes de test qui vérifient la fonctionnalité de recherche et de filtrage des badges :

### 1. `test_badge_search_by_name`

**Objectif** : Vérifier que la recherche de badges par nom fonctionne correctement.

**Description** : Ce test vérifie que la recherche de badges par nom retourne les badges dont le nom contient le terme de recherche.

**Fonctionnement** :
- Envoie une requête GET à l'URL de la page liste des badges avec un paramètre de recherche
- Vérifie que seuls les badges dont le nom contient le terme de recherche sont retournés

### 2. `test_badge_search_by_description`

**Objectif** : Vérifier que la recherche de badges par description fonctionne correctement.

**Description** : Ce test vérifie que la recherche de badges par description retourne les badges dont la description contient le terme de recherche.

**Fonctionnement** :
- Envoie une requête GET à l'URL de la page liste des badges avec un paramètre de recherche
- Vérifie que seuls les badges dont la description contient le terme de recherche sont retournés

### 3. `test_badge_search_by_structure`

**Objectif** : Vérifier que la recherche de badges par structure fonctionne correctement.

**Description** : Ce test vérifie que la recherche de badges par structure retourne les badges dont la structure émettrice contient le terme de recherche dans son nom.

**Fonctionnement** :
- Envoie une requête GET à l'URL de la page liste des badges avec un paramètre de recherche
- Vérifie que seuls les badges dont la structure émettrice contient le terme de recherche dans son nom sont retournés

### 4. `test_badge_filter_by_level`

**Objectif** : Vérifier que le filtrage des badges par niveau fonctionne correctement.

**Description** : Ce test vérifie que le filtrage des badges par niveau retourne les badges du niveau spécifié.

**Fonctionnement** :
- Envoie une requête GET à l'URL de la page liste des badges avec un paramètre de filtrage par niveau
- Vérifie que seuls les badges du niveau spécifié sont retournés
- Teste également le filtrage par plusieurs niveaux

### 5. `test_badge_filter_by_structure`

**Objectif** : Vérifier que le filtrage des badges par structure fonctionne correctement.

**Description** : Ce test vérifie que le filtrage des badges par structure retourne les badges émis par la structure spécifiée.

**Fonctionnement** :
- Envoie une requête GET à l'URL de la page liste des badges avec un paramètre de filtrage par structure
- Vérifie que seuls les badges émis par la structure spécifiée sont retournés

### 6. `test_badge_combined_search_and_filter`

**Objectif** : Vérifier que la combinaison de la recherche et du filtrage fonctionne correctement.

**Description** : Ce test vérifie que la combinaison de la recherche et du filtrage retourne les badges qui correspondent à la fois au terme de recherche et au filtre.

**Fonctionnement** :
- Envoie une requête GET à l'URL de la page liste des badges avec des paramètres de recherche et de filtrage
- Vérifie que seuls les badges qui correspondent à la fois au terme de recherche et au filtre sont retournés

### 7. `test_htmx_request_returns_partial_template`

**Objectif** : Vérifier que les requêtes HTMX retournent le template partiel.

**Description** : Ce test vérifie que les requêtes HTMX retournent uniquement le contenu partiel sans le template de base.

**Fonctionnement** :
- Envoie une requête GET normale à l'URL de la page liste des badges
- Vérifie que le template complet est utilisé
- Envoie une requête GET avec l'en-tête HTMX à l'URL de la page liste des badges
- Vérifie que seul le template partiel est utilisé
- Vérifie que le contenu de la réponse HTMX contient uniquement la liste des badges sans la barre latérale de filtrage

### 8. `test_no_duplicate_data_in_response`

**Objectif** : Vérifier qu'il n'y a pas de données en double dans la réponse.

**Description** : Ce test vérifie qu'il n'y a pas de badges en double dans la réponse de la page liste des badges.

**Fonctionnement** :
- Envoie une requête GET à l'URL de la page liste des badges
- Extrait les noms des badges de la réponse
- Vérifie qu'il n'y a pas de noms en double en comparant la longueur de la liste avec la longueur de l'ensemble
- Vérifie que tous les badges sont présents dans la réponse
