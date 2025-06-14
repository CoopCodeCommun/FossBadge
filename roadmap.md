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

- [ ] Créer les modèles Django suivants:
  - [ ] Utilisateur (extension du modèle User de Django)
    - Champs: avatar, genre, nom, prénom, adresse
  - [ ] Badge
    - Champs: icône, nom, niveau (débutant/intermédiaire/expert), description
  - [ ] Association/Entreprise
    - Champs: logo, nom, adresse, SIREN/SIRET, description, coordonnées géographiques
  - [ ] Personne référente
    - Champs: genre, nom, prénom, poste, association liée
  - [ ] Relations entre modèles
    - Utilisateur-Badge (ManyToMany)
    - Utilisateur-Association (ManyToMany)
    - Badge-Association (ForeignKey)
- [ ] Créer et exécuter les migrations
- [ ] Configurer l'interface d'administration Django

## 4. Développement Backend

- [ ] Créer les vues Django pour:
  - [ ] Page utilisateur
  - [ ] Page badge
  - [ ] Page association/entreprise
  - [ ] Page création de badge
  - [ ] Page création d'association/entreprise
- [ ] Implémenter les formulaires Django
  - [ ] Formulaire de création de badge
  - [ ] Formulaire de création d'association/entreprise
- [ ] Configurer les URLs
- [ ] Implémenter la logique HTMX pour les interactions dynamiques
- [ ] Générer des QR codes pour les badges

## 5. Développement Frontend

- [ ] Structure HTML de base
  - [ ] Template de base avec Bootstrap 5
  - [ ] Navbar et footer communs
- [ ] Développer les templates HTML pour chaque page:
  - [ ] Page utilisateur
    - [ ] Section informations personnelles
    - [ ] Grille de badges (4x4 max)
    - [ ] Liste des associations
  - [ ] Page badge
    - [ ] Affichage des détails du badge
    - [ ] QR Code
    - [ ] Structures où le badge est valable
  - [ ] Page association/entreprise
    - [ ] Informations de l'association
    - [ ] Liste des badges disponibles
    - [ ] Carte OpenStreetMap
  - [ ] Formulaire de création de badge
  - [ ] Formulaire de création d'association/entreprise
- [ ] Styles CSS (Bootstrap 5)
  - [ ] Styles responsives
  - [ ] Éléments larges et contrastés (FALC)
  - [ ] Adaptation mobile-first

## 6. Accessibilité et FALC

- [ ] Vérifier la conformité FALC
  - [ ] Textes courts et simples
  - [ ] Contraste élevé
  - [ ] Éléments visuels clairs
- [ ] Implémenter les attributs d'accessibilité HTML
- [ ] Tester avec des outils d'accessibilité
- [ ] Optimiser pour les lecteurs d'écran

## 7. Intégration HTMX

- [ ] Configurer HTMX pour les interactions sans JavaScript complexe
- [ ] Implémenter les endpoints pour les requêtes HTMX
- [ ] Tester les interactions dynamiques

## 8. Tests

- [ ] Écrire des tests unitaires pour les modèles
- [ ] Écrire des tests pour les vues
- [ ] Écrire des tests pour les formulaires
- [ ] Tests d'intégration
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
