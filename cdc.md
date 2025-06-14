# 🧾 Cahier des charges UI — Pages HTML/CSS FALC pour système de badges

## 🎯 Objectif

Créer un ensemble de pages web **ultra simples**, accessibles, et compatibles avec le principe **FALC (Facile à Lire et à Comprendre)**.

L'interface doit :
- être conçue en **HTML5 + Bootstrap 5**,
- éviter tout JavaScript sauf ce qui est **nécessaire pour HTMX**,
- être facilement intégrable côté back-end Python (Django ou équivalent, avec templates),
- être **responsive**, avec des éléments larges, lisibles et contrastés.

---

## 🖼️ Pages à concevoir

### 1. Page utilisateur

Affiche les informations d’un·e utilisateur·rice ainsi que ses badges et associations.

**Contenu :**
- Icône / avatar de l'utilisateur
- Genre / Nom / Prénom / Adresse
- Bloc “Mes badges” (grille 4x4 maximum)
- Bloc “Mes associations” (logos d’assos/entreprises liés)

---

### 2. Page badge

Affiche les détails d’un badge individuel.

**Contenu :**
- Icône du badge
- Nom du badge
- Association émettrice ou endorsée par une autre
- Niveau : **débutant / intermédiaire / expert**
- QR Code à télécharger (géré par le back)
- Logos des structures où le badge est **valable**
- Mention : “Ce badge est rattaché à d'autres personnes...” (liste ou noms simples)

---

### 3. Page entreprise / association

Page dédiée à une structure.

**Contenu :**
- Logo
- Nom de l'association/entreprise
- Adresse
- Description du lieu ou de la mission
- Liste des badges disponibles (blocs/icônes)
- Bouton : “Forger un nouveau badge”
- Carte OpenStreetMap (sera gérée par le back ; prévoir un `<div id="map">`)

---

### 4. Page forger un badge

Formulaire de création de badge par une structure.

**Champs :**
- Icône du badge (upload ou sélection simple)
- Nom du badge
- Niveau : sélection parmi 3 options (débutant / intermédiaire / expert)
- Description courte

---

### 5. Page création d’association / entreprise

Formulaire d’ajout d’une structure.

**Champs :**
- Nom de l'association/entreprise
- Adresse
- Numéro SIREN/SIRET (texte libre, validation côté back)
- Description de la mission / lieu
- Personne référente :
  - Genre
  - Nom
  - Prénom
  - Poste

---

## 🎨 Style et accessibilité

- **Bootstrap 5 uniquement** (pas d'autres frameworks)
- Responsive, **mobile first**
- Polices lisibles, **gros boutons**, **textes courts**, **contraste élevé**
- Utilisation possible de [Bootstrap Icons](https://icons.getbootstrap.com/)
- Éléments visuels simples (icônes, badges carrés avec textes)
- Aucun effet visuel ou animation non essentiel

---

## ⚙️ Contraintes techniques

- Zéro JS complexe : **HTMX uniquement**, géré côté back
- Utilisation de `div`, `section`, `form`, `article`, etc. HTML5 sémantique
- Prévoir des `class` claires et réutilisables (ex. `.badge-card`, `.asso-list`, `.user-info`)
- Les formulaires doivent être compatibles avec HTMX : pur HTML5
- SEO facile by design : utilise au maximum la sémentique shema.org

---

## 📁 Organisation attendue

