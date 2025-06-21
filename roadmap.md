# FossBadge - Roadmap d'implémentation

Ce document détaille les étapes nécessaires pour implémenter le système de badges tel que décrit dans le cahier des charges.

## 1. Configuration initiale

- [x] Création du projet Django
- [x] Configuration de l'application 'core'
  - [x] Ajouter 'core' à INSTALLED_APPS dans settings.py
  - [x] Configurer les dossiers statiques et media
  - [x] Configurer les templates
- [x] Installation des dépendances
  - [x] Bootstrap 5
  - [x] HTMX
  - [x] Autres bibliothèques nécessaires

## 2. Maquette graphique

- [ ] Créer des wireframes/maquettes pour les interfaces utilisateur
  - [ ] Page utilisateur
  - [ ] Page badge
  - [ ] Page association/entreprise
  - [ ] Page création de badge
  - [ ] Page création d'association/entreprise
- [ ] Implémenter des templates Django statiques pour visualiser les maquettes
  - [ ] Créer des templates HTML avec Bootstrap 5
  - [ ] Ajouter des données factices pour simuler le contenu
  - [ ] Configurer les routes Django pour accéder aux maquettes
- [ ] Valider les maquettes avec les parties prenantes
  - [ ] Recueillir les retours
  - [ ] Ajuster les maquettes selon les retours

## 3. Modèles de données

- [x] Créer les modèles Django suivants:
  - [x] Utilisateur (extension du modèle User de Django)
    - Champs: avatar, genre, nom, prénom, adresse
  - [x] Badge
    - Champs: icône, nom, niveau (débutant/intermédiaire/expert), description
  - [x] Association/Entreprise
    - Champs: logo, nom, adresse, SIREN/SIRET, description, coordonnées géographiques
  - [x] Personne référente
    - Champs: genre, nom, prénom, poste, association liée
  - [x] Relations entre modèles
    - Utilisateur-Badge (ManyToMany)
    - Utilisateur-Association (ManyToMany)
    - Badge-Association (ForeignKey)
- [x] Créer et exécuter les migrations
- [x] Configurer l'interface d'administration Django

## 4. Développement Backend

- [x] Créer les vues Django pour:
  - [x] Page utilisateur
  - [x] Page badge
  - [x] Page association/entreprise
  - [x] Page création de badge
  - [x] Page création d'association/entreprise
- [x] Implémenter les formulaires Django
  - [x] Formulaire de création de badge
  - [x] Formulaire de création d'association/entreprise
- [x] Configurer les URLs
- [x] Implémenter la logique HTMX pour les interactions dynamiques
- [x] Générer des QR codes pour les badges

## 5. Développement Frontend

- [x] Structure HTML de base
  - [x] Template de base avec Bootstrap 5
  - [x] Navbar et footer communs
- [x] Développer les templates HTML pour chaque page:
  - [x] Page utilisateur
    - [x] Section informations personnelles
    - [x] Grille de badges (4x4 max)
    - [x] Liste des associations
  - [x] Page badge
    - [x] Affichage des détails du badge
    - [x] QR Code
    - [x] Structures où le badge est valable
  - [x] Page association/entreprise
    - [x] Informations de l'association
    - [x] Liste des badges disponibles
    - [x] Carte OpenStreetMap
  - [x] Formulaire de création de badge
  - [x] Formulaire de création d'association/entreprise
- [x] Styles CSS (Bootstrap 5)
  - [x] Styles responsives
  - [x] Éléments larges et contrastés (FALC)
  - [x] Adaptation mobile-first

## 6. Accessibilité et FALC

- [x] Vérifier la conformité FALC
  - [x] Textes courts et simples
  - [x] Contraste élevé
  - [x] Éléments visuels clairs
- [x] Implémenter les attributs d'accessibilité HTML
- [x] Tester avec des outils d'accessibilité
- [x] Optimiser pour les lecteurs d'écran

## 7. Intégration HTMX

- [x] Configurer HTMX pour les interactions sans JavaScript complexe
- [x] Implémenter les endpoints pour les requêtes HTMX
- [x] Tester les interactions dynamiques

## 8. Tests

- [x] Écrire des tests unitaires pour les modèles
- [x] Écrire des tests pour les vues
- [x] Écrire des tests pour les formulaires
- [x] Tests d'intégration
- [ ] Tests d'accessibilité

## 9. Documentation

- [ ] Documenter l'API
- [ ] Créer un guide d'utilisation
- [ ] Documenter l'architecture du projet
- [ ] Mettre à jour le README.md

## 10. Déploiement

- [ ] Configurer les paramètres de production
- [ ] Sécuriser l'application
- [ ] Déployer sur un serveur de test
- [ ] Tests finaux
- [ ] Déploiement en production

## 11. Maintenance et évolution

- [ ] Plan de maintenance
- [ ] Idées d'améliorations futures
- [ ] Gestion des retours utilisateurs
