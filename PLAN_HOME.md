# Plan — Page d'accueil / Home Page

## Ce qui a été fait (session mars 2026)

### 1. Page d'accueil avec recherche unifiée

**URL** : `/` (racine, via `HomeViewSet.list`)

Page style Google : titre centré, sous-titre, barre de recherche plein écran.
Quand l'utilisateur tape ≥ 4 caractères, les résultats apparaissent en 3 colonnes.

**Fichiers** :
- `core/views.py` → `HomeViewSet` (list, search, badge_focus, structure_focus, person_focus)
- `core/urls.py` → routeur DRF, basename `home`
- `templates/core/home/index.html` → page principale
- `templates/core/home/base_home.html` → base minimale sans navbar/footer
- `static/css/custom.css` → tous les styles home

### 2. Recherche HTMX en 3 colonnes

**Action** : `HomeViewSet.search` (`GET /search/`)
**Template partiel** : `templates/core/home/partial/search_results.html`

Comportement :
- `hx-get` déclenché au `keyup` avec délai 300ms
- Minimum 4 caractères (bloqué côté JS + côté serveur)
- Recherche dans : nom, description, structure émettrice, notes d'endorsement, badges assignés
- Résultats en 3 colonnes : **Badges** | **Structures** | **Personnes**
- Limite : 5 résultats par catégorie
- Animation d'apparition progressive (fadeIn 0.2s, stagger 0.02s par item)

### 3. Filtres toggle (Badges / Structures / Personnes)

3 checkboxes stylisées en pastilles colorées (orange / bleu / vert).
Activées par défaut. Décocher une catégorie la masque dans les résultats.

Subtilité technique : les checkboxes non cochées ne sont pas envoyées en GET.
Le helper `read_category_filters(request)` détecte si au moins un filtre est présent ;
si oui, les absents sont considérés comme désactivés.

Les filtres sont propagés à toutes les vues focus via `hx-include="#home-search-filters"`.

### 4. Mécanisme de focus

Cliquer sur un item l'agrandit **dans sa propre colonne** :
- Badge → se déplie dans la colonne Badges (gauche)
- Structure → se déplie dans la colonne Structures (centre)
- Personne → se déplie dans la colonne Personnes (droite)

Les autres colonnes affichent les objets **liés** (pas les résultats de recherche).

**Actions serveur** :
- `badge_focus` → `GET /badge-focus/<uuid>/` → `partial/badge_focus.html`
- `structure_focus` → `GET /structure-focus/<uuid>/` → `partial/structure_focus.html`
- `person_focus` → `GET /person-focus/<uuid>/` → `partial/person_focus.html`

**Relations affichées** :
| Focus      | Col 1 (Badges)         | Col 2 (Structures)           | Col 3 (Personnes)         |
|------------|------------------------|------------------------------|---------------------------|
| Badge      | **Détail badge**       | Émettrice + endorseuses      | Possesseurs du badge      |
| Structure  | Badges émis/endossés   | **Détail structure**         | Membres                   |
| Personne   | Badges possédés        | Structures d'appartenance    | **Détail personne**       |

**Tags visuels** dans les colonnes liées :
- Badges : "Émis" (orange) / "Endossé" (bleu)
- Structures : "Émetteur" (orange) / "Endosse" (bleu)
- Personnes : "Possède ce badge" / "Membre"

### 5. Cross-navigation

Depuis un focus, on peut cliquer sur un objet lié pour passer à son propre focus.
Exemple : Badge focus → clic sur une structure → Structure focus → clic sur un membre → Person focus.

Tous les liens dans les templates focus pointent vers les URLs de focus (pas les pages détail classiques).
Le paramètre `q` et les filtres sont conservés via les query params.

### 6. Push URL + fallback no-JS

- Chaque focus ajoute `hx-push-url="true"` → l'URL du navigateur reflète l'état.
- Le bouton "← Retour aux résultats" utilise `hx-push-url="/"` pour revenir à la racine.
- Fallback sans JS : chaque vue focus vérifie `request.htmx`.
  - Si HTMX → retourne le partiel seul.
  - Sinon → retourne `index.html` avec `focus_partial` pré-rempli.

### 7. Spinner de chargement

- Petit spinner dans l'input (via `hx-indicator`) pour les recherches.
- Grand spinner centré (`#results-spinner`) pour les transitions focus.
  Géré en JS via `htmx:beforeRequest` / `htmx:afterSwap`.

### 8. Styles et couleurs

Variables CSS :
- `--home-color-badges: #e8a735` (orange)
- `--home-color-structures: #5b8def` (bleu)
- `--home-color-personnes: #6ec477` (vert)

La page utilise `base_home.html` (sans navbar ni footer) pour un rendu épuré.

---

## Idées futures / TODO

### A. Focus multiple (sélection combinée)

Objectif : pouvoir sélectionner **plusieurs objets** de colonnes différentes et voir l'intersection.

**Cas d'usage concrets :**
- Sélectionner un badge + un lieu → voir les personnes qui possèdent ce badge ET appartiennent à ce lieu.
- Sélectionner une personne + un lieu → voir les badges donnés ou endossés par ce lieu que cette personne possède.
- Sélectionner un badge + une personne → voir les structures où cette personne a reçu ce badge.

**Étapes techniques :**

1. **Nouveau concept : `multi-focus`**
   - L'URL encode les sélections : `/multi-focus/?badge=<uuid>&structure=<uuid>`
   - Nouveau partiel : `partial/multi_focus.html`
   - Nouvelle action `HomeViewSet.multi_focus()` qui calcule les intersections

2. **UX de sélection**
   - En mode focus simple, un bouton "Ajouter au filtre" (icône +) sur chaque item des colonnes liées.
   - Cliquer "ajoute" l'item sans remplacer le focus actuel → on passe en multi-focus.
   - La colonne sélectionnée affiche l'item en mode "focus compact" (icône + nom, pas le détail complet).
   - La troisième colonne (non sélectionnée) affiche l'**intersection**.

3. **Requêtes d'intersection côté serveur**
   - Badge + Structure → `User.objects.filter(badge_assignments__badge=badge, badge_assignments__assigned_structure=structure)`
   - Personne + Structure → `Badge.objects.filter(assignments__user=person, Q(issuing_structure=structure) | Q(endorsements__structure=structure))`
   - Badge + Personne → `Structure.objects.filter(Q(issued_badges=badge) | Q(endorsements__badge=badge)).filter(Q(admins=person) | Q(editors=person) | Q(users=person))`

4. **Bouton "Réinitialiser"** pour revenir au focus simple ou à la recherche.

---

### B. Carte des lieux sous la recherche

Objectif : afficher une **carte MapLibre** sous le champ de recherche, montrant les structures (lieux) qui correspondent à la recherche. Cliquer sur un marqueur ouvre un **tooltip** listant les badges recherchés que ce lieu possède.

**Pas de Deck.gl, pas de 3D, pas de hexagones.** Juste MapLibre GL JS + des marqueurs + des popups.

**L'ancien code `mapview/` est une expérimentation à nettoyer** (voir B.6).

#### B.0 — Ce qui existe et qu'on réutilise

- Modèle `Marker` (`mapview/models.py`) : `name`, `lat`, `lng`, `icon`. Lié à `Structure` via FK nullable.
- `Structure.marker` : si non-null, la structure est affichable sur la carte.
- `Structure.latitude` / `Structure.longitude` : champs directs, inutilisés pour l'instant. Alternative possible au `Marker`.
- `MapViewConfig` (django-solo) : centre par défaut de la carte (Lyon : 45.77, 4.88).
- MapLibre GL JS déjà dans les dépendances front.
- Fond de carte CARTO (voyager, positron, dark-matter) — pas de clé API.

#### B.1 — Layout : toggle Liste / Carte

Un bouton toggle (icône liste / icône carte) est placé **à côté des filtres** Badges / Structures / Personnes.
Il bascule entre la vue liste (3 colonnes, comportement actuel) et la vue carte.

```
┌──────────────────────────────────────────────────┐
│              🔍 Barre de recherche               │
│  [Badges] [Structures] [Personnes]   [≡] [🗺️]  │  ← filtres + toggle vue
├──────────────────────────────────────────────────┤
│  Mode liste :                                    │
│  Badges  │  Structures  │  Personnes             │  ← #search-results
├──────────────────────────────────────────────────┤
│  Mode carte :                                    │
│  ┌──────────────────────────────────────────┐    │
│  │            🗺️ Carte MapLibre            │    │  ← #search-results
│  │          📍 📍    📍                     │    │
│  │                📍                        │    │
│  └──────────────────────────────────────────┘    │
└──────────────────────────────────────────────────┘
```

**Implémentation du toggle :**
- 2 boutons radio stylisés en pill (comme les filtres), groupés à droite des filtres catégorie.
- Le bouton "Liste" est actif par défaut.
- Cliquer "Carte" → `hx-get` vers `/search-map/?q=...` qui retourne le partiel carte.
- Cliquer "Liste" → `hx-get` vers `/search/?q=...` qui retourne les colonnes habituelles.
- En mode carte, la carte occupe ~500px de haut dans `#search-results`.
- Sans recherche (< 4 chars) : la carte affiche toutes les structures avec marker.
- Le toggle conserve les filtres via `hx-include="#home-search-filters"`.

#### B.2 — Nouvelle action : `HomeViewSet.map_data()`

Endpoint JSON léger qui retourne les structures filtrées par la recherche.

```python
@action(detail=False, methods=["GET"], url_path="map-data")
def map_data(self, request):
    """
    Retourne les structures avec marker au format GeoJSON,
    filtrées par la recherche en cours.
    Returns structures with markers as GeoJSON, filtered by current search.
    """
    search_query = request.GET.get('q', '')
    structures_with_markers = Structure.objects.filter(
        marker__isnull=False
    ).select_related('marker')

    if len(search_query) >= 4:
        structures_with_markers = structures_with_markers.filter(
            Q(name__icontains=search_query)
            | Q(description__icontains=search_query)
            | Q(issued_badges__name__icontains=search_query)
            | Q(issued_badges__description__icontains=search_query)
        ).distinct()

    # Pour chaque structure, inclure les badges qui matchent la recherche
    features = []
    for structure in structures_with_markers:
        matching_badges = Badge.objects.filter(
            Q(issuing_structure=structure) | Q(endorsements__structure=structure)
        ).distinct()
        if len(search_query) >= 4:
            matching_badges = matching_badges.filter(
                Q(name__icontains=search_query)
                | Q(description__icontains=search_query)
            )

        features.append({
            'type': 'Feature',
            'geometry': {
                'type': 'Point',
                'coordinates': [structure.marker.lng, structure.marker.lat],
            },
            'properties': {
                'pk': str(structure.pk),
                'name': structure.name,
                'badges': [
                    {'pk': str(b.pk), 'name': b.name}
                    for b in matching_badges[:10]
                ],
                'badge_count': matching_badges.count(),
            },
        })

    return JsonResponse({'type': 'FeatureCollection', 'features': features})
```

**Exception à la règle "pas de JSON pour l'UI"** : ici le JSON est une donnée géographique consommée par MapLibre, pas du pilotage d'UI. Le tooltip est rendu côté client par MapLibre (API native `Popup`).

#### B.3 — Template : bloc carte dans `index.html`

Ajouter un `<div id="home-map">` sous `#search-results` dans `index.html`.

```html
{# Carte des lieux / Map of places #}
<div id="home-map" style="height: 400px; border-radius: 12px; overflow: hidden; margin-top: 1rem;"></div>
```

Le JS de la carte est dans un nouveau fichier : `static/js/home_map.js` (~80 lignes).
Chargement lazy : le `<script>` est dans `index.html`, MapLibre GL CSS/JS via CDN.

#### B.4 — JS : `home_map.js`

Script simple, pas de classe complexe. Fonctionnalités :

1. **Init** : créer la carte MapLibre centrée sur `MapViewConfig` (ou Lyon par défaut).
2. **Chargement des marqueurs** : `fetch('/map-data/?q=...')` → ajouter les features comme source GeoJSON.
3. **Marqueurs** : layer `circle` ou `symbol` MapLibre (pastilles bleues `--home-color-structures`).
4. **Clic sur marqueur** → `Popup` MapLibre avec :
   - Nom de la structure (lien vers `structure-focus/`)
   - Liste des badges matchés (liens vers `badge-focus/`)
   - Si > 10 badges : "et X autres..."
5. **Mise à jour** : écouter `htmx:afterSwap` sur `#search-results` pour re-fetch `/map-data/` avec le `q` courant.
6. **Pas de filtrage par viewport** (contrairement à l'ancien code). Toutes les structures matchées sont affichées.

```javascript
// Pseudo-code simplifié / Simplified pseudo-code
document.addEventListener('DOMContentLoaded', function() {
    const map = new maplibregl.Map({
        container: 'home-map',
        style: 'https://basemaps.cartocdn.com/gl/voyager-gl-style/style.json',
        center: [4.88, 45.77],  // Lyon par défaut / Lyon default
        zoom: 5,
    });

    function updateMarkers() {
        const searchInput = document.getElementById('home-search-input');
        const query = searchInput ? searchInput.value : '';
        fetch(`/map-data/?q=${encodeURIComponent(query)}`)
            .then(r => r.json())
            .then(geojson => {
                // Mettre à jour la source GeoJSON / Update GeoJSON source
                if (map.getSource('structures')) {
                    map.getSource('structures').setData(geojson);
                } else {
                    map.addSource('structures', { type: 'geojson', data: geojson });
                    map.addLayer({ /* circle layer */ });
                }
            });
    }

    map.on('load', updateMarkers);

    // Re-fetch quand la recherche change / Re-fetch when search changes
    document.body.addEventListener('htmx:afterSwap', function(event) {
        if (event.detail.target.id === 'search-results') {
            updateMarkers();
        }
    });

    // Popup au clic / Popup on click
    map.on('click', 'structures-layer', function(e) {
        const props = e.features[0].properties;
        const badges = JSON.parse(props.badges);
        // Construire le HTML du popup / Build popup HTML
        new maplibregl.Popup()
            .setLngLat(e.lngLat)
            .setHTML(popupHtml)
            .addTo(map);
    });
});
```

#### B.5 — CSS carte

Styles minimaux dans `custom.css` :

```css
#home-map {
    height: 400px;
    border-radius: 12px;
    overflow: hidden;
    margin-top: 1rem;
    border: 1px solid #e8eaed;
}

/* Popup MapLibre — style cohérent avec le reste de la home */
.maplibregl-popup-content {
    border-radius: 12px;
    padding: 0.75rem 1rem;
    font-family: inherit;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.12);
    max-width: 280px;
}
```

#### B.6 — Nettoyage de l'ancien code `mapview/`

L'app `mapview/` est une expérimentation. À nettoyer :

**À supprimer :**
- `mapview/views.py` → `IndexViewSet` (toutes les vues)
- `mapview/urls.py` → routes `/map/`
- `mapview/templates/mapview/` → tous les templates (index, partials, exploration)
- `static/mapview/js/map_3d.js` → classe `ApplicationMap3D` (576 lignes)
- `static/mapview/css/map_3d.css` → styles du panneau flottant
- Référence dans le routeur principal (`urls.py` racine)

**À conserver :**
- `mapview/models.py` → modèle `Marker` + `MapViewConfig` (utilisés par la nouvelle carte)
- `mapview/migrations/` → nécessaires pour la BDD
- `mapview/fixtures/` → fichier KML d'exemple (utile pour le populate_db)
- `mapview/admin.py` → à enrichir pour gérer les Markers dans Unfold

**À vérifier :**
- L'URL `/map/` dans la navbar ou ailleurs → la retirer
- Les imports de `mapview.views` dans le `urls.py` racine → les retirer

#### B.7 — Fichiers à créer / modifier

| Fichier | Action |
|---------|--------|
| `core/views.py` | Ajouter `map_data()` dans `HomeViewSet` |
| `core/urls.py` | L'action est auto-routée par DRF (`map-data/`) |
| `templates/core/home/index.html` | Ajouter `<div id="home-map">` + `<script>` MapLibre + `home_map.js` |
| `static/js/home_map.js` | **Nouveau** — ~80 lignes, init carte + marqueurs + popup |
| `static/css/custom.css` | Ajouter styles `#home-map` + popup |
| `mapview/views.py` | Vider (supprimer les vues) |
| `mapview/urls.py` | Vider (supprimer les routes) |
| `mapview/templates/` | Supprimer tout le dossier |
| `static/mapview/` | Supprimer `js/map_3d.js` + `css/map_3d.css` |
| URL racine (`urls.py`) | Retirer l'include de `mapview.urls` |

#### B.8 — Filtres : retirer "Personnes" de la carte ?

La carte ne montre que des **structures** (lieux) et des **badges**. Les personnes n'ont pas de coordonnées géographiques.

Cependant, la recherche textuelle en colonnes continue à fonctionner avec les 3 filtres (Badges, Structures, Personnes). La carte ignore simplement le filtre "Personnes" et ne réagit qu'aux badges et structures.

Pas besoin de retirer le filtre "Personnes" de l'UI — il reste utile pour les colonnes.

---

### C. Intégration des features existantes dans la nouvelle UX

Tout ce qui existe dans les templates Bootstrap classiques, à intégrer progressivement dans la page d'accueil ou dans des modales/panneaux HTMX.

#### C.1 Features Badge (existant dans `core/badges/`)

| Feature | Templates actuels | Intégration prévue |
|---------|------------------|--------------------|
| **Liste badges** | `badges/list.html` + `partials/badge_list.html` | Déjà remplacé par la colonne Badges de `/` |
| **Détail badge** | `badges/detail.html` | Enrichir `badge_focus.html` avec les infos manquantes (holders, endorsements, boutons action) |
| **Créer badge** | `badges/create.html` | Modale HTMX depuis le focus ou bouton "+" dans la colonne Badges |
| **Éditer badge** | `badges/edit.html` | Modale HTMX depuis le badge_focus (si permission IsBadgeEditor) |
| **Supprimer badge** | `badges/delete.html` | Modale confirmation HTMX depuis badge_focus |
| **Assigner badge** | `partials/badge_assignment.html` | Modale HTMX depuis badge_focus, bouton "Assigner" (si CanAssignBadge) |
| **Endorser badge** | `partials/badge_endorsement.html` | Modale HTMX depuis badge_focus, bouton "Endorser" (si CanEndorseBadge) |

#### C.2 Features Structure (existant dans `core/structures/`)

| Feature | Templates actuels | Intégration prévue |
|---------|------------------|--------------------|
| **Liste structures** | `structures/list.html` + `partials/structure_list.html` | Déjà remplacé par la colonne Structures de `/` |
| **Détail structure** | `structures/detail.html` | Enrichir `structure_focus.html` (badges émis, membres par rôle, formulaire invitation) |
| **Créer structure** | `structures/create.html` | Modale HTMX ou page dédiée accessible depuis le "+" |
| **Éditer structure** | `structures/edit.html` | Modale HTMX depuis structure_focus (si IsStructureAdmin) |
| **Supprimer structure** | `structures/delete.html` | Modale confirmation HTMX |
| **Inviter membre** | Formulaire dans `detail.html` | Modale HTMX depuis structure_focus, bouton "Inviter" (si IsStructureAdmin) |

#### C.3 Features Utilisateur (existant dans `core/users/`)

| Feature | Templates actuels | Intégration prévue |
|---------|------------------|--------------------|
| **Liste utilisateurs** | `users/list.html` + `partials/user_list.html` | Déjà remplacé par la colonne Personnes de `/` |
| **Profil utilisateur** | `users/detail.html` | Enrichir `person_focus.html` (badges groupés, structures avec rôles) |
| **Éditer profil** | `partials/user_profile_edit.html` | Modale HTMX depuis person_focus (si self ou admin) |
| **CV** | `users/cv.html` + variantes (bootstrap, material, liquid_glass) | Bouton "Voir le CV" dans person_focus → ouvre dans un nouvel onglet ou modale pleine page |
| **Login** | `authentication/login.html` | Conserver tel quel (page séparée) ou modale HTMX accessible depuis la home |
| **Logout** | redirect | Conserver tel quel |

#### C.4 Features Assignment (existant dans `core/assignments/`)

| Feature | Templates actuels | Intégration prévue |
|---------|------------------|--------------------|
| **Détail assignment** | `assignments/detail.html` | Modale HTMX depuis person_focus ou badge_focus (clic sur un badge possédé) |
| **Liste assignments par badge** | `assignments/list_user_assignment.html` | Intégrer dans person_focus quand on clique sur un badge |

#### C.5 Ordre de priorité d'intégration

**Phase 1 — Enrichir les focus existants (pas de nouvelle page)**
1. Ajouter les boutons d'action conditionnels dans badge_focus (Assigner, Endorser, Éditer, Supprimer) — visibles uniquement si l'utilisateur a les permissions.
2. Ajouter les boutons d'action dans structure_focus (Inviter, Éditer, Supprimer).
3. Ajouter les boutons d'action dans person_focus (Éditer profil, Voir CV).
4. Charger les modales existantes (`badge_assignment.html`, `badge_endorsement.html`) via HTMX depuis les focus.

**Phase 2 — Création d'objets depuis la home**
5. Bouton "Créer un badge" (visible si IsAuthenticated) → modale ou side-panel HTMX.
6. Bouton "Créer une structure" → idem.
7. Formulaire d'invitation membre depuis structure_focus.

**Phase 3 — Multi-focus**
8. Implémenter la sélection combinée (section A ci-dessus).

**Phase 4 — Vue carte**
9. Intégrer la bascule liste/carte (section B ci-dessus).

**Phase 5 — Nettoyage**
10. Rediriger les anciennes URLs (`/badges/`, `/structures/`, `/users/`) vers la home avec les bons query params.
11. Supprimer les templates de liste devenus inutiles.
12. Conserver les pages de détail classiques comme fallback SEO / partage de lien.

---

### D. UX générale

- [ ] **Pagination / "Voir plus"** : actuellement limité à 5 résultats par catégorie. Ajouter un bouton "Voir tous les badges (12)" qui charge la suite.
- [ ] **Recherche par tags/catégories** : filtres avancés (niveau, domaine, territoire).
- [ ] **Historique de recherche** : suggestions basées sur les recherches récentes.
- [ ] **Résultats "vides" améliorés** : message contextuel quand une colonne est vide ("Aucun badge trouvé pour 'social'").
- [ ] **Raccourcis clavier** : Escape pour revenir aux résultats, flèches pour naviguer.
- [ ] **Animation de transition** entre focus : slide horizontal au lieu de fade.

### E. Contenu du focus

- [ ] **Badges** : ajouter les critères d'obtention, la date de création, le nombre de possesseurs.
- [ ] **Structures** : ajouter la mini-carte (si lat/lng disponibles via `Structure.marker`), les liens web/réseaux sociaux.
- [ ] **Personnes** : ajouter la bio, les compétences, la date d'inscription.
- [ ] **Bouton "Voir la fiche complète"** : lien vers la page détail existante depuis le focus.

### F. Technique

- [ ] **Cache** : mettre en cache les résultats de recherche fréquents (Redis/Memcached).
- [ ] **Recherche full-text** : migrer vers `SearchVector` / `SearchRank` de PostgreSQL pour des résultats plus pertinents.
- [ ] **Debounce serveur** : rate limiting sur `/search/` pour éviter les abus.
- [ ] **Tests** : écrire des tests pour chaque action du HomeViewSet (search, badge_focus, structure_focus, person_focus) + tests HTMX vs no-JS.
- [ ] **SEO** : meta tags dynamiques pour les pages focus (Open Graph, titre, description).
- [ ] **Accessibilité** : audit complet WCAG, navigation clavier dans les résultats, annonces aria-live.

### G. Design

- [ ] **Mode sombre** : vérifier que toutes les classes Bootstrap respectent le thème.
- [ ] **Responsive mobile** : les 3 colonnes deviennent un accordéon vertical sur petit écran.
- [ ] **Illustrations vides** : SVG illustratifs quand il n'y a pas encore de résultats.