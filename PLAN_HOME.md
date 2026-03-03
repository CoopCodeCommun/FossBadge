# Plan — Page d'accueil / Home Page

## Ce qui a été fait (session mars 2026)

### 1. Page d'accueil avec recherche unifiée

**URL** : `/` (racine, via `HomeViewSet.list`)

Page style Google : titre centré, sous-titre, barre de recherche plein écran.
Quand l'utilisateur tape >= 4 caractères, les résultats apparaissent en 3 colonnes.

**Fichiers** :
- `core/views.py` -> `HomeViewSet` (list, search, badge_focus, structure_focus, person_focus, multi_focus, map_data)
- `core/urls.py` -> routeur DRF, basename `home`
- `templates/core/home/index.html` -> page principale
- `templates/core/home/base_home.html` -> base minimale sans navbar/footer
- `static/css/custom.css` -> tous les styles home
- `static/js/home_map.js` -> carte MapLibre

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
- Badge -> se déplie dans la colonne Badges (gauche)
- Structure -> se déplie dans la colonne Structures (centre)
- Personne -> se déplie dans la colonne Personnes (droite)

Les autres colonnes affichent les objets **liés** (pas les résultats de recherche).

**Actions serveur** :
- `badge_focus` -> `GET /badge-focus/<uuid>/` -> `partial/badge_focus.html`
- `structure_focus` -> `GET /structure-focus/<uuid>/` -> `partial/structure_focus.html`
- `person_focus` -> `GET /person-focus/<uuid>/` -> `partial/person_focus.html`

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
Exemple : Badge focus -> clic sur une structure -> Structure focus -> clic sur un membre -> Person focus.

Tous les liens dans les templates focus pointent vers les URLs de focus (pas les pages détail classiques).
Le paramètre `q` et les filtres sont conservés via les query params.

### 6. Push URL + fallback no-JS

- Chaque focus ajoute `hx-push-url="true"` -> l'URL du navigateur reflète l'état.
- Le bouton "<- Retour aux résultats" utilise `hx-push-url="/"` pour revenir à la racine.
- Fallback sans JS : chaque vue focus vérifie `request.htmx`.
  - Si HTMX -> retourne le partiel seul.
  - Sinon -> retourne `index.html` avec `focus_partial` pré-rempli.

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

### 9. Multi-focus (sélection combinée)

**Action** : `HomeViewSet.multi_focus` (`GET /multi-focus/?badge=<uuid>&structure=<uuid>`)
**Template partiel** : `templates/core/home/partial/multi_focus.html`

Sélectionner 2 ou 3 objets de colonnes différentes.
- Avec 2 items : les 2 en détail + l'intersection dans la 3e colonne.
- Avec 3 items : les 3 en détail, pas d'intersection.

**Intersections serveur** :
- Badge + Structure -> Personnes qui possèdent ce badge ET appartiennent à cette structure.
- Badge + Personne -> Structures qui émettent/endossent ce badge ET où la personne est membre.
- Structure + Personne -> Badges émis/endossés par la structure ET possédés par la personne.

**Bouton x** sur chaque carte focus pour retirer un item (revient au focus simple ou au multi-focus à 2).

### 10. Carte MapLibre (toggle liste / carte)

**Toggle** : 2 boutons radio (icône liste / icône pin) à droite des filtres catégorie, séparés par un trait vertical.

**Mécanisme** : bascule la visibilité de `#search-results` et `#home-map-container`. La carte est un `<div>` fixe dans `index.html`, initialisé paresseusement au premier clic.

**Fichiers** :
- `static/js/home_map.js` -> expose `initHomeMap(onReady)` et `updateHomeMap(pks, query)`
- MapLibre GL JS + CSS chargés via CDN dans `{% block extra_js %}`

**Données carte** :
- `map_data()` (`GET /map-data/`) retourne du GeoJSON.
- Accepte `?pks=1,2,3` pour filtrer par PKs de structures (mode focus/multi-focus).
- Accepte `?q=...` pour filtrer par recherche textuelle (mode recherche).
- Sans paramètre : retourne toutes les structures avec marker.

**Contexte carte dans les partials** :
Chaque partial injecte un `<div id="map-context" hidden data-structures="pk1,pk2">`.
Les PKs sont calculés côté serveur (`structures_pks_csv`, `related_structures_pks`, `multi_structures_pks`).
Quand on bascule en mode carte, le JS lit ces PKs et appelle `updateHomeMap(pks)`.

**Push URL** : `?view=map` est ajouté à l'URL via `history.pushState`. Au rechargement, si `?view=map` est présent, la carte s'affiche directement.

**Points techniques** :
- `map.resize()` à chaque `updateHomeMap` (le conteneur était peut-être `display: none`).
- `initHomeMap(onReady)` attend l'événement `load` de MapLibre avant d'appeler le callback.
- `width: 100%` sur `#home-map-container` (sinon le flex parent le réduit à 0).
- Panneau liste coulissant dans la carte (bouton flottant en bas à gauche).
- `fitBounds` à chaque mise à jour pour recentrer sur les structures du contexte.

**Supprimé** : action `search_map()`, template `partial/search_map.html`. La carte n'est plus un partial HTMX mais un élément DOM permanent piloté par JS.

---

## Idées futures / TODO

### A. Vue Lieu — Page dédiée d'une structure

**Objectif** : une page autonome pour chaque structure. Ce n'est plus de la recherche, c'est de l'**exploration**. L'URL est partageable, indexable, et sert de vitrine du lieu.

**URL** : `/lieu/<uuid>/` (ex: `/lieu/a1b2c3d4/`)

**Remplace** : `structures/detail.html` (ancien détail avec onglets Bootstrap pills).

#### A.1 — Design : "Fiche de lieu"

Direction esthétique : sobre, éditoriale, aérée. Même famille visuelle que la home (mêmes variables CSS, mêmes classes `.home-*`). Pas de gradient flashy, pas de carte surélevée. Juste une page propre qui donne l'info.

```
┌──────────────────────────────────────────────────────┐
│  <- FossBadge                                        │
│                                                      │
│  [Logo 80px]  Nom de la Structure                    │
│               Association · Lyon 4e                  │
│               Description (2-3 lignes max)           │
│                                                      │
│  ┌────────────────────────────────────────────────┐  │
│  │         Mini carte MapLibre (si marker)        │  │
│  │                   180px                         │  │
│  └────────────────────────────────────────────────┘  │
│                                                      │
│  ── Badges ici ──────────────────────────────── (6)  │
│                                                      │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐              │
│  │ [icon]  │  │ [icon]  │  │ [icon]  │              │
│  │ Nom     │  │ Nom     │  │ Nom     │              │
│  │ Expert  │  │ Inter.  │  │ Début.  │              │
│  └─────────┘  └─────────┘  └─────────┘              │
│                                                      │
│  [⚒ Forger un badge]  (si admin/éditeur du lieu)     │
│                                                      │
│  ── Personnes ────────────────────────────────── (8) │
│                                                      │
│  [avatar] Prénom Nom · 3 badges  -> /passeport/      │
│  [avatar] Prénom Nom · 1 badge   -> /passeport/      │
│                                                      │
│  ── Référent ────────────────────────────────────    │
│  Nom Prénom · Poste (si renseigné)                   │
│                                                      │
└──────────────────────────────────────────────────────┘
```

**Principes de design** :
- En-tête horizontal : logo (80px) à gauche, nom + type + adresse + description à droite. Pas d'en-tête géant centré — sobre comme la home.
- Mini carte MapLibre sous l'en-tête si marker (180px, non interactive, `scrollZoom: false`).
- Badges en grille de cartes réutilisant les classes `.home-result-item`. Clic -> déplie le détail en HTMX sur place (pas de redirection).
- "Forger un badge" en bas de la grille badges, visible si `is_admin or is_editor`. Lien vers `create_badge` avec `?structure=<pk>` (existant dans `structures/detail.html` ligne 58).
- Personnes en liste simple réutilisant `.home-result-item`. Clic -> `/passeport/<uuid>/`.
- Référent (nom, prénom, poste) en pied de page si renseigné (existant dans `structures/detail.html` lignes 88-104).
- Pas d'onglets (l'ancien détail avait 3 onglets — Détail/Badges/Users). Tout est sur une seule page, scrollable.
- Bouton retour vers FossBadge en haut à gauche.

#### A.2 — Contenu récupéré de l'ancien `structures/detail.html`

| Contenu existant | Ligne | Récupérer dans Vue Lieu ? |
|---|---|---|
| Logo + nom | 48-55 | Oui — en-tête horizontal |
| Boutons Éditer/Supprimer (si admin) | 12-16 | Oui — discrets en haut à droite |
| Bouton "Forger un nouveau badge" (si admin/éditeur) | 58-60 | Oui — en bas de la grille badges |
| Adresse | 71 | Oui — sous le nom |
| SIRET | 73-78 | Oui — petit texte discret |
| Description | 82-84 | Oui — en-tête |
| Référent (nom, prénom, poste) | 88-104 | Oui — section pied de page |
| Carte Leaflet (commentée) | 113-136 | Remplacé par mini MapLibre |
| Onglet Badges (émis + endossés) | 139-166 | Oui — liste unique fusionnée avec tags "Émis"/"Endossé" |
| Onglet Utilisateurs (users/editors/admins) | 168-193 | Oui — liste unique fusionnée, rôle en petit tag |
| Popup invite SweetAlert | 197-237 | Plus tard (phase 2) — modale HTMX |

#### A.3 — Implémentation

```python
@action(detail=False, methods=["GET"], url_path="lieu/(?P<structure_pk>[^/.]+)")
def lieu(self, request, structure_pk=None):
    structure = get_object_or_404(
        Structure.objects.select_related('marker'), uuid=structure_pk
    )

    # Badges émis et endossés, avec tag pour distinguer
    # Issued and endorsed badges, with tag to distinguish
    issued_badges = Badge.objects.filter(
        issuing_structure=structure
    ).select_related('issuing_structure')

    endorsed_badges = Badge.objects.filter(
        endorsements__structure=structure
    ).select_related('issuing_structure')

    # Membres avec annotation du rôle (pour afficher un tag admin/éditeur/membre)
    # Members with role annotation (to display admin/editor/member tag)
    members_list = User.objects.filter(
        Q(structures_admins=structure)
        | Q(structures_editors=structure)
        | Q(structures_users=structure)
    ).annotate(
        is_structure_admin=Exists(
            structure.admins.filter(pk=OuterRef('pk'))
        ),
        is_structure_editor=Exists(
            structure.editors.filter(pk=OuterRef('pk'))
        ),
    ).distinct()
    # Dans le template : {% if member.is_structure_admin %}Admin{% elif member.is_structure_editor %}Éditeur{% else %}Membre{% endif %}

    # Permissions
    is_admin = structure.is_admin(request.user) if request.user.is_authenticated else False
    is_editor = structure.is_editor(request.user) if request.user.is_authenticated else False

    return render(request, 'core/lieu/index.html', {
        'structure': structure,
        'issued_badges': issued_badges,
        'endorsed_badges': endorsed_badges,
        'members_list': members_list,
        'is_admin': is_admin,
        'is_editor': is_editor,
    })
```

**Fichiers** :
| Fichier | Action |
|---------|--------|
| `templates/core/lieu/index.html` | **Nouveau** — page complète (hérite de `base_home.html`) |
| `static/css/custom.css` | Styles `.lieu-*` (peu de nouveau, on réutilise `.home-*`) |
| `core/views.py` | Action `lieu()` |

---

### B. Vue Passeport — Page dédiée d'un utilisateur

**Objectif** : le "CV open badge" d'une personne. Page autonome, partageable, qui raconte le **parcours** de l'utilisateur à travers les lieux et les compétences acquises.

**URL** : `/passeport/<uuid>/` (ex: `/passeport/d4e5f6g7/`)

**Remplace** : `users/detail.html` (ancien profil) + `users/cv*.html` (anciens CV) + `assignments/list_user_assignment.html`.

Ce n'est pas juste une liste de badges. C'est un **récit de parcours** : les badges sont regroupés par lieu, chaque lieu est une étape du voyage.

#### B.1 — Design : "Carnet de route"

Direction esthétique : sobre, éditorial, personnel. Même famille visuelle que la home et la vue lieu. Pas de gradient, pas de carte fancy. Juste une page propre qui raconte un parcours.

```
┌──────────────────────────────────────────────────────────┐
│  <- FossBadge                          [Se déconnecter]  │
│                                                          │
│  [Avatar 80px]  Prénom Nom                               │
│                 Lyon · 12 badges · 3 lieux               │
│                                                          │
│  ── Parcours ─────────────────────────────────────────── │
│                                                          │
│  ┌─ Maison des Canuts ────────────────────────────────┐  │
│  │  [logo 40px] Maison des Canuts · Lyon 4e           │  │
│  │                                                    │  │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐         │  │
│  │  │ [icon]   │  │ [icon]   │  │ [icon]   │         │  │
│  │  │ Tissage  │  │ Teinture │  │ Design   │         │  │
│  │  │ Expert   │  │ Inter.   │  │ Débutant │         │  │
│  │  │ mars 24  │  │ jan 24   │  │ nov 23   │         │  │
│  │  └──────────┘  └──────────┘  └──────────┘         │  │
│  │                                                    │  │
│  │  [v] Détail "Tissage" (clic pour déplier)          │  │
│  │  ┌──────────────────────────────────────────────┐  │  │
│  │  │ Attribué le 15 mars 2024                     │  │  │
│  │  │ par Jean Martin (Maison des Canuts)          │  │  │
│  │  │                                              │  │  │
│  │  │ Notes : "Marie a réalisé un projet           │  │  │
│  │  │ remarquable de tissage Jacquard."            │  │  │
│  │  └──────────────────────────────────────────────┘  │  │
│  └────────────────────────────────────────────────────┘  │
│                                                          │
│  ┌─ FabLab de Villeurbanne ───────────────────────────┐  │
│  │  [logo 40px] FabLab · Villeurbanne                 │  │
│  │                                                    │  │
│  │  ┌──────────┐  ┌──────────┐                        │  │
│  │  │ [icon]   │  │ [icon]   │                        │  │
│  │  │ Impres.  │  │ Arduino  │                        │  │
│  │  │ Expert   │  │ Inter.   │                        │  │
│  │  │ fev 25   │  │ dec 24   │                        │  │
│  │  └──────────┘  └──────────┘                        │  │
│  └────────────────────────────────────────────────────┘  │
│                                                          │
│  ── Carte du parcours ────────────────────────────────── │
│                                                          │
│  ┌──────────────────────────────────────────────────┐    │
│  │          MapLibre avec les lieux du parcours      │    │
│  └──────────────────────────────────────────────────┘    │
│                                                          │
│  [Éditer mon profil]  (si c'est son propre passeport)    │
│                                                          │
└──────────────────────────────────────────────────────────┘
```

**Principes de design** :
- En-tête horizontal : avatar (80px) à gauche, nom + adresse + compteurs à droite. Sobre, comme la vue lieu.
- **Parcours groupé par lieu** : chaque structure est un bloc/carte. Le nom du lieu est un lien vers `/lieu/<uuid>/`.
- Chaque badge dans le parcours montre : icône, nom, niveau (pastille), date d'obtention.
- **Clic sur un badge → déplie le détail de l'assignment** (HTMX, `<details>` ou panneau), avec : date, assigné par qui, notes. Pas de redirection, tout sur place.
- Les lieux sont triés par date du badge le plus récent (le lieu le plus actif en premier).
- **Carte du parcours** en bas : MapLibre montrant les lieux du parcours.
- Boutons conditionnels en pied :
  - "Éditer mon profil" (si `request.user == person`) → modale HTMX réutilisant `user_profile_edit.html`.
  - "Se déconnecter" (si self) en haut à droite.

#### B.2 — Contenu récupéré de l'ancien `users/detail.html`

| Contenu existant | Ligne | Récupérer dans Passeport ? |
|---|---|---|
| Avatar + nom | 28-36 | Oui — en-tête horizontal |
| Bouton "Se déconnecter" (si self) | 17-21 | Oui — haut à droite |
| Badge "Inactif" | 13-15 | Oui — tag discret si inactif |
| Infos personnelles (nom, prénom, adresse) | 70-82 | Oui — en sous-titre de l'en-tête |
| Bouton "Éditer" profil (HTMX) | 60-67 | Oui — en bas de page si self |
| Dropdown CV (4 templates) | 39-49 | **Non** — le passeport remplace les CV |
| Badges (groupés par badge) | 88-97 | **Remplacé** — groupés par lieu |
| Structures | 99-131 | **Remplacé** — intégré dans le parcours |
| Désactiver compte | 133-151 | Oui — tout en bas si self, discret |

#### B.3 — Contenu récupéré de `assignments/detail.html`

Le détail d'un assignment (badge assigné à une personne) s'affiche **en dépliable dans le passeport**, pas dans une page séparée.

| Contenu existant | Récupérer ? |
|---|---|
| "Assigné par X à Y" + date | Oui — en-tête du dépliable |
| "Assigné par la structure Z" | Oui — sous-titre |
| Notes | Oui — corps du dépliable |
| QR code téléchargeable | Plus tard — quand l'audio/vidéo sera implémenté |

#### B.4 — Implémentation

```python
@action(detail=False, methods=["GET"], url_path="passeport/(?P<person_pk>[^/.]+)")
def passeport(self, request, person_pk=None):
    person = get_object_or_404(User, uuid=person_pk)

    # Tous les assignments avec badge et structure
    # All assignments with badge and structure
    assignments = BadgeAssignment.objects.filter(
        user=person
    ).select_related(
        'badge', 'badge__issuing_structure', 'badge__issuing_structure__marker',
        'assigned_by', 'assigned_structure', 'assigned_structure__marker',
    ).order_by('-assigned_date')

    # Grouper par le lieu qui a attribué le badge (assigned_structure).
    # Si assigned_structure est null, on tombe sur issuing_structure (fallback).
    # Group by the place that assigned the badge (assigned_structure).
    # If assigned_structure is null, fall back to issuing_structure.
    places_dict = {}
    orphan_assignments = []  # Assignments sans lieu associé / Without associated place

    for assignment in assignments:
        # Le lieu d'attribution prime sur la structure émettrice
        # The assigning place takes priority over the issuing structure
        structure = assignment.assigned_structure or assignment.badge.issuing_structure

        if structure is None:
            # Cas rare : ni assigned_structure ni issuing_structure
            # Rare case: no assigned_structure nor issuing_structure
            orphan_assignments.append(assignment)
            continue

        if structure.pk not in places_dict:
            places_dict[structure.pk] = {
                'structure': structure,
                'assignments': [],
                'latest_date': assignment.assigned_date,
            }
        places_dict[structure.pk]['assignments'].append(assignment)

    # Trier par date du badge le plus récent
    # Sort by most recent badge date
    places_list = sorted(
        places_dict.values(),
        key=lambda p: p['latest_date'],
        reverse=True,
    )

    # Ajouter les orphelins à la fin sous "Parcours libre"
    # Append orphans at the end under "Free path"
    if orphan_assignments:
        places_list.append({
            'structure': None,  # Sera affiché comme "Parcours libre" dans le template
            'assignments': orphan_assignments,
            'latest_date': orphan_assignments[0].assigned_date,
        })

    # Structures avec marker pour la carte (exclure les orphelins sans structure)
    # Structures with marker for the map (exclude orphans without structure)
    structures_pks_csv = ','.join(
        str(p['structure'].pk) for p in places_list
        if p['structure'] and p['structure'].marker_id
    )

    is_self = request.user.is_authenticated and request.user.pk == person.pk

    return render(request, 'core/passeport/index.html', {
        'person': person,
        'places_list': places_list,
        'total_badges': assignments.count(),
        'total_places': len(places_list),
        'structures_pks_csv': structures_pks_csv,
        'is_self': is_self,
    })
```

**Fichiers** :
| Fichier | Action |
|---------|--------|
| `templates/core/passeport/index.html` | **Nouveau** — page complète (hérite de `base_home.html`) |
| `static/css/custom.css` | Styles `.passeport-*` (peu de nouveau, on réutilise `.home-*`) |
| `core/views.py` | Action `passeport()` |

#### B.5 — Liens entre les vues

**Règle fondamentale : le multi-focus ne change pas.**

Le mécanisme de focus et multi-focus dans la home (sections 4 et 9) est un élément central de l'architecture. Il reste **exactement comme il est** : clic sur un badge → badge_focus dans la colonne de gauche. Clic sur un second objet → multi-focus. Les 3 colonnes, les intersections, les boutons ×, tout ça reste intact.

Les pages dédiées (`/lieu/`, `/passeport/`, `/badge/`) sont un **complément**, pas un remplacement. On y accède via un bouton explicite "Ouvrir le détail" dans chaque focus. Ce bouton **sort** de la home vers une page autonome.

**Bouton "Ouvrir le détail" dans chaque focus :**
- **Structure focus** → bouton "Voir le lieu" → `/lieu/<uuid>/`
- **Person focus** → bouton "Voir le passeport" → `/passeport/<uuid>/`
- **Badge focus** → bouton "Voir le badge" → `/badge/<uuid>/`

```
Home (recherche + focus + multi-focus)
  │
  ├── clic item            -> focus dans la colonne (comportement existant, inchangé)
  ├── clic 2e item         -> multi-focus (comportement existant, inchangé)
  │
  ├── dans structure_focus : bouton "Voir le lieu"      -> /lieu/<uuid>/
  ├── dans person_focus    : bouton "Voir le passeport" -> /passeport/<uuid>/
  ├── dans badge_focus     : bouton "Voir le badge"     -> /badge/<uuid>/
  │
Badge (page dédiée /badge/<uuid>/)
  │
  ├── clic structure       -> /lieu/<uuid>/
  ├── clic personne        -> /passeport/<uuid>/
  ├── boutons action       -> assigner, endosser (modales HTMX)
  │
Lieu (page dédiée /lieu/<uuid>/)
  │
  ├── clic badge           -> déplie sur place (<details>) avec lien "Voir le badge" -> /badge/<uuid>/
  ├── clic personne        -> /passeport/<uuid>/
  ├── clic "Forger badge"  -> /badge/create/?structure=<pk>
  │
Passeport (page dédiée /passeport/<uuid>/)
  │
  ├── clic badge           -> déplie le détail assignment (<details>) avec lien "Voir le badge" -> /badge/<uuid>/
  ├── clic lieu            -> /lieu/<uuid>/
  ├── clic "Éditer profil" -> modale HTMX (réutilise user_profile_edit.html)
```

**Comportement du clic badge selon le contexte** :
- **Dans la home** : clic → **focus** dans la colonne (existant, inchangé). Bouton "Voir le badge" dans le focus pour aller vers `/badge/<uuid>/`.
- **Dans vue lieu et passeport** : clic → **déplie sur place** (`<details>`) pour montrer le contexte local (notes, qui a assigné, boutons action). Lien discret "Voir le badge" vers `/badge/<uuid>/`.
- **Raison** : dans chaque contexte, on reste dans le flux. On ne quitte la page que par un bouton explicite.

---

### B.6 — Vue Badge — Page dédiée d'un badge

**Objectif** : une page autonome pour chaque badge. C'est la version "agrandie" du badge_focus. Page partageable, indexable, avec toutes les infos et les actions.

**URL** : `/badge/<uuid>/` (ex: `/badge/e1f2g3h4/`)

**Remplace** : `badges/detail.html` (ancien détail Bootstrap). Le `badge_focus.html` dans la home reste intact — c'est la version compacte. `/badge/<uuid>/` est la version complète, accessible via le bouton "Voir le badge" dans le focus.

#### Design : "Fiche de badge"

Même famille visuelle que lieu et passeport. Sobre, éditorial.

```
┌──────────────────────────────────────────────────────────┐
│  <- FossBadge                                            │
│                                                          │
│  [Icon 80px]  Nom du Badge                               │
│               Expert · Émis par Maison des Canuts        │
│               Description (2-3 lignes)                   │
│               Critères : "..." (si renseigné)            │
│                                                          │
│  ── Structures qui reconnaissent ce badge ────── (4)     │
│                                                          │
│  [logo] Maison des Canuts (émetteur)                     │
│  [logo] FabLab Villeurbanne (endosse)                    │
│  [logo] Asso Textile Lyon (endosse)                      │
│                                                          │
│  ── Détenteurs ──────────────────────────────── (12)     │
│                                                          │
│  [avatar] Marie Dupont · via Maison des Canuts           │
│  [avatar] Jean Martin · via FabLab Villeurbanne          │
│                                                          │
│  [Attribuer]  [Endosser]  [Éditer]  [Supprimer]         │
│  (selon permissions)                                     │
│                                                          │
│  ── Carte ───────────────────────────────────────        │
│  ┌──────────────────────────────────────────────┐        │
│  │   MapLibre : structures qui émettent/endossent│        │
│  └──────────────────────────────────────────────┘        │
│                                                          │
└──────────────────────────────────────────────────────────┘
```

**Principes** :
- En-tête horizontal : icône (80px) à gauche, nom + niveau + émetteur + description + critères à droite.
- Structures en liste avec tag "Émetteur" / "Endosse". Clic → `/lieu/<uuid>/`.
- Détenteurs en liste avec avatar + nom + structure d'attribution. Clic → `/passeport/<uuid>/`.
- Boutons d'action en bas : Attribuer, Endosser, Éditer, Supprimer (selon permissions).
- Carte en bas si au moins une structure a un marker.

#### Implémentation

```python
@action(detail=False, methods=["GET"], url_path="badge/(?P<badge_pk>[^/.]+)")
def badge_detail(self, request, badge_pk=None):
    badge = get_object_or_404(
        Badge.objects.select_related('issuing_structure', 'issuing_structure__marker'),
        uuid=badge_pk
    )

    # Structures qui endossent ce badge
    # Structures that endorse this badge
    endorsing_structures = Structure.objects.filter(
        endorsements__badge=badge
    ).select_related('marker')

    # Toutes les structures (émettrice + endosseuses) pour la carte
    # All structures (issuer + endorsers) for the map
    all_structures = [badge.issuing_structure] + list(endorsing_structures)

    # Détenteurs avec leur structure d'attribution
    # Holders with their assigning structure
    holders = BadgeAssignment.objects.filter(
        badge=badge
    ).select_related('user', 'assigned_structure').order_by('-assigned_date')

    # Permissions
    is_badge_editor = False
    can_assign = False
    can_endorse = False
    if request.user.is_authenticated:
        is_badge_editor = badge.issuing_structure.is_editor(request.user) or badge.issuing_structure.is_admin(request.user)
        # L'utilisateur peut assigner s'il est admin/éditeur d'une structure qui endosse
        # User can assign if admin/editor of an endorsing structure
        can_assign = any(
            s.is_admin(request.user) or s.is_editor(request.user)
            for s in all_structures
        )
        # L'utilisateur peut endosser s'il a au moins une structure
        can_endorse = Structure.objects.filter(
            Q(admins=request.user) | Q(editors=request.user)
        ).exists()

    structures_pks_csv = ','.join(
        str(s.pk) for s in all_structures if s.marker_id
    )

    return render(request, 'core/badge_page/index.html', {
        'badge': badge,
        'endorsing_structures': endorsing_structures,
        'holders': holders,
        'is_badge_editor': is_badge_editor,
        'can_assign': can_assign,
        'can_endorse': can_endorse,
        'structures_pks_csv': structures_pks_csv,
    })
```

**Fichiers** :
| Fichier | Action |
|---------|--------|
| `templates/core/badge_page/index.html` | **Nouveau** — page complète (hérite de `base_home.html`) |
| `static/css/custom.css` | Styles `.badge-page-*` (peu de nouveau, on réutilise `.home-*`) |
| `core/views.py` | Action `badge_detail()` |

---

### C. Intégration des features existantes dans la nouvelle UX

Tout ce qui existe dans les templates Bootstrap classiques, à intégrer progressivement dans la page d'accueil ou dans des modales/panneaux HTMX.

#### C.1 Features Badge (existant dans `core/badges/`)

| Feature | Templates actuels | Intégration prévue |
|---------|------------------|--------------------|
| **Liste badges** | `badges/list.html` + `partials/badge_list.html` | Déjà remplacé par la colonne Badges de `/` |
| **Détail badge** | `badges/detail.html` | Remplacé par `/badge/<uuid>/` (section B.6) |
| **Créer badge** | `badges/create.html` | Lié depuis "Forger un badge" (recherche + vue lieu) |
| **Éditer badge** | `badges/edit.html` | Modale HTMX depuis `/badge/<uuid>/` (si IsBadgeEditor) |
| **Supprimer badge** | `badges/delete.html` | Modale confirmation HTMX depuis `/badge/<uuid>/` (si IsBadgeEditor) |
| **Assigner badge** | `partials/badge_assignment.html` | Modale HTMX depuis vue lieu + `/badge/<uuid>/` (si CanAssignBadge) |
| **Endorser badge** | `partials/badge_endorsement.html` | Modale HTMX depuis vue lieu + `/badge/<uuid>/` (si CanEndorseBadge) |

#### C.2 Features Structure (existant dans `core/structures/`)

| Feature | Templates actuels | Intégration prévue |
|---------|------------------|--------------------|
| **Liste structures** | `structures/list.html` + `partials/structure_list.html` | Déjà remplacé par la colonne Structures de `/` |
| **Détail structure** | `structures/detail.html` | Remplacé par `/lieu/<uuid>/` |
| **Créer structure** | `structures/create.html` | Modale HTMX ou page dédiée accessible depuis le "+" |
| **Éditer structure** | `structures/edit.html` | Modale HTMX depuis la vue lieu (si IsStructureAdmin) |
| **Supprimer structure** | `structures/delete.html` | Modale confirmation HTMX |
| **Inviter membre** | Formulaire dans `detail.html` | Modale HTMX depuis la vue lieu, bouton "Inviter" (si IsStructureAdmin) |

#### C.3 Features Utilisateur (existant dans `core/users/`)

| Feature | Templates actuels | Intégration prévue |
|---------|------------------|--------------------|
| **Liste utilisateurs** | `users/list.html` + `partials/user_list.html` | Déjà remplacé par la colonne Personnes de `/` |
| **Profil utilisateur** | `users/detail.html` | Remplacé par `/passeport/<uuid>/` |
| **Éditer profil** | `partials/user_profile_edit.html` | Modale HTMX depuis le passeport (si self ou admin) |
| **CV** | `users/cv.html` + variantes | Le passeport EST le nouveau CV |
| **Login** | `authentication/login.html` | Conserver tel quel (page séparée) |
| **Logout** | redirect | Conserver tel quel |

#### C.4 Features Assignment (existant dans `core/assignments/`)

| Feature | Templates actuels | Intégration prévue |
|---------|------------------|--------------------|
| **Détail assignment** | `assignments/detail.html` | Modale HTMX depuis le passeport (clic sur un badge) |
| **Liste assignments par badge** | `assignments/list_user_assignment.html` | Intégré dans le passeport (badges groupés par lieu) |

#### C.5 Ordre de priorité d'intégration

**Phase 1 — Pages d'exploration**
1. Vue Lieu (`/lieu/<uuid>/`) — affiche badges, personnes, carte. Réutilise le contenu de `structures/detail.html`.
2. Vue Passeport (`/passeport/<uuid>/`) — parcours groupé par lieu, dépliable assignment. Réutilise `users/detail.html` + `assignments/detail.html`.
3. Vue Badge (`/badge/<uuid>/`) — détail badge, structures, détenteurs, carte, boutons action. Remplace `badges/detail.html`.
4. Ajouter bouton "Ouvrir le détail" dans chaque focus : structure_focus → `/lieu/`, person_focus → `/passeport/`, badge_focus → `/badge/`. Les focus eux-mêmes restent inchangés.
5. Bouton "Forger un badge" dans la recherche et dans la vue lieu.
6. Bloc récit dans le multi-focus : description/critères (badge+structure) + histoire (badge+structure+personne). Utilise les champs existants (`notes`, `assigned_by`).

**Phase 1.5 — Migration `criteria`** (dès que les pages de base fonctionnent)
7. Ajouter `criteria` (TextField, blank=True) sur `Badge`. Migration simple. Le champ décrit ce qu'il faut faire pour obtenir le badge (distinct de `description` qui décrit le badge). Afficher `badge.criteria` (si renseigné) à la place de `badge.description` dans les blocs récit du multi-focus et les dépliables.

**Phase 2 — Boutons d'action**
8. Vue Lieu : boutons Éditer/Supprimer (si admin), Inviter (modale HTMX).
9. Passeport : bouton "Éditer profil" (si self) → réutilise `user_profile_edit.html`.
10. Vue Badge : boutons Attribuer/Endosser/Éditer/Supprimer (selon permissions).
11. Attribuer un badge : vue lieu + vue badge + multi-focus badge+structure (section D.2).
12. Endosser un badge : vue lieu + vue badge + badge focus (section D.3).

**Phase 3 — Enrichir les récits**
13. Séparer `structure_comment` / `recipient_comment` sur BadgeAssignment (migration).
14. Modèle `EndorsementMedia` + lecteurs audio/vidéo.

**Phase 4 — Nettoyage**
15. Rediriger `/structures/<pk>/` → `/lieu/<uuid>/`, `/users/<pk>/` → `/passeport/<uuid>/`, `/badges/<pk>/` → `/badge/<uuid>/`.
16. Supprimer les templates devenus inutiles (`structures/detail.html`, `users/detail.html`, `users/cv*.html`, `assignments/list_user_assignment.html`, `badges/detail.html`).

---

### D. Actions sur les badges — Forger, Attribuer, Endosser

**Principe de design** : les actions apparaissent **là où le contexte est le plus riche**, c'est-à-dire là où le plus de champs sont déjà connus. Moins l'utilisateur a de champs à remplir, meilleure est l'UX.

Les formulaires existants (`badge_assignment.html`, `badge_endorsement.html`) sont réutilisés tels quels dans des modales HTMX. Pas de nouveau formulaire à créer.

#### D.1 — Forger un badge (créer)

Le bouton apparaît dans **2 emplacements** :

1. **Recherche** : sous "Aucun badge trouvé" dans `search_results.html` (si authentifié). Lien avec `?name=<query>`.
2. **Vue Lieu** : en bas de la grille badges (si admin ou éditeur du lieu). Lien avec `?structure=<pk>`. C'est déjà le cas dans l'ancien `structures/detail.html` ligne 58.

```
┌─────────────────────────┐     ┌─────────────────────────────────┐
│  Badges                 │     │  ── Badges ici ──────── (3)     │
│                         │     │                                 │
│  Aucun badge trouvé     │     │  [badge] [badge] [badge]        │
│                         │     │                                 │
│  [⚒ Forger un badge]    │     │  [⚒ Forger un badge]            │
│                         │     │  (si admin/éditeur du lieu)     │
│  (Recherche)            │     │  (Vue Lieu)                     │
└─────────────────────────┘     └─────────────────────────────────┘
```

**Lien** vers `{% url 'core:create_badge' %}` (route et template existants).
**Style** : bouton discret, outline, couleur `--home-color-badges`. Au hover, fond plein orange.

#### D.2 — Attribuer un badge (assigner à une personne)

**Raisonnement** : le formulaire d'attribution demande badge + structure + user + notes. Le meilleur endroit est celui où badge et structure sont déjà connus — il ne reste qu'à choisir la personne.

| Emplacement | Badge | Structure | User | Verdict |
|---|---|---|---|---|
| **Vue Lieu** (dépliable badge) | connu | connu (le lieu) | à choisir | **Idéal — 1 seul champ** |
| **Multi-focus** badge+structure | connu | connu | à choisir | **Bon — 1 seul champ** |
| **Multi-focus** badge+structure+personne | connu | connu | connu | **Parfait — 0 champ (juste notes)** |
| Badge focus/detail (existant) | connu | à choisir | à choisir | Correct mais 2 champs |

**Emplacement principal : Vue Lieu**

Quand je suis admin/éditeur d'une structure, je déplie un badge et je vois un bouton "Attribuer". Le formulaire n'affiche que le sélecteur de personne + notes. Badge et structure sont pré-remplis en hidden.

```
┌─ Vue Lieu : Maison des Canuts ─────────────────────┐
│                                                    │
│  ┌──────────┐  ┌──────────┐                        │
│  │ Tissage  │  │ Teinture │                        │
│  │ Expert   │  │ Inter.   │                        │
│  └─────┬────┘  └──────────┘                        │
│        │                                           │
│  ┌─────▼───────────────────────────────────────┐   │
│  │  Tissage artisanal — Expert                 │   │
│  │  3 détenteurs · Émis par ce lieu            │   │
│  │                                             │   │
│  │  [Attribuer]  [Endosser]                    │   │
│  │  (si admin/éditeur)                         │   │
│  └─────────────────────────────────────────────┘   │
│                                                    │
└────────────────────────────────────────────────────┘
```

Clic "Attribuer" → modale HTMX qui charge `badge_assignment.html` avec `badge_pk` pré-rempli et `assigned_structure` pré-rempli sur le **lieu courant** (pas la structure émettrice du badge). C'est le lieu courant qui attribue, même si le badge a été créé par une autre structure. Le champ structure dans le formulaire est un hidden ou un select pré-sélectionné non modifiable.

**Important** : un badge endossé par le lieu courant peut être attribué par ce lieu. Le `assigned_structure` dans le `BadgeAssignment` sera le lieu courant (pas l'`issuing_structure` du badge). C'est cohérent avec la logique du passeport qui groupe par `assigned_structure`.

**Emplacement secondaire : Multi-focus badge+structure**

Dans le bloc récit sous les colonnes, si l'utilisateur a la permission `CanAssignBadge`, un bouton "Attribuer ce badge" apparaît. Badge et structure sont connus. Même modale.

**Emplacement tertiaire : Multi-focus badge+structure+personne**

Les 3 sont connus. Le bouton "Attribuer à [personne]" apparaît dans le bloc histoire. Le formulaire ne demande que les notes. C'est le cas le plus fluide — un clic et c'est fait.

**Le badge detail existant** (`badges/detail.html`) conserve aussi ses boutons actuels. Pas de changement.

#### D.3 — Endosser un badge (une structure reconnaît un badge)

**Raisonnement** : l'endossement part du **badge** — "ma structure veut reconnaître ce badge". Le formulaire demande badge + structure + notes.

| Emplacement | Badge | Structure | Verdict |
|---|---|---|---|
| **Badge focus** (home) | connu | à choisir parmi mes structures | **Bon — 1 champ** |
| **Vue Lieu** (dépliable badge) | connu | connu (le lieu) | **Idéal — 0 champ** |
| Badge detail (existant) | connu | à choisir | Correct — 1 champ |

**Emplacement principal : Vue Lieu**

Quand je suis admin/éditeur d'une structure et que je déplie un badge **d'une autre structure** (pas émis par le lieu courant, mais visible parce qu'il est déjà endossé ou lié), le bouton "Endosser" apparaît. Structure pré-remplie (le lieu courant), badge pré-rempli.

Mais aussi : dans la vue lieu, il y a les badges **émis** par le lieu. Pour ceux-là, pas besoin d'endosser (c'est déjà le lieu émetteur). Le bouton "Endosser" n'apparaît que pour les badges d'autres structures.

**Emplacement secondaire : Badge focus (home)**

Quand je consulte un badge dans le focus et que j'ai au moins une structure qui ne l'endosse pas encore, le bouton "Endosser" apparaît. Le formulaire me laisse choisir laquelle de mes structures endosse.

**Le badge detail existant** (`badges/detail.html`) conserve aussi ses boutons actuels.

**Note sur les permissions** :
- Attribuer : l'utilisateur est admin/éditeur d'une structure qui endosse le badge (`CanAssignBadge`).
- Endosser : l'utilisateur est admin/éditeur d'une structure (`CanEndorseBadge`).
- Ces permissions existent déjà dans `core/permissions.py`.

#### D.4 — Résumé des emplacements

```
Forger (créer)
  ├── Recherche : "Aucun badge trouvé" (si authentifié)
  └── Vue Lieu : bas de la grille badges (si admin/éditeur)

Attribuer (assigner à une personne)
  ├── Vue Lieu : dépliable badge (si admin/éditeur) ← principal
  ├── Vue Badge /badge/<uuid>/ : bouton (si CanAssignBadge)
  ├── Multi-focus badge+structure : bloc récit (si CanAssignBadge)
  └── Multi-focus badge+structure+personne : bloc histoire (si CanAssignBadge)

Endosser (structure reconnaît un badge)
  ├── Vue Lieu : dépliable badge d'une autre structure (si admin/éditeur) ← principal
  └── Vue Badge /badge/<uuid>/ : bouton (si CanEndorseBadge)
```

---

### E. Histoire de l'endossement

**Objectif** : afficher le récit de l'endossement — comment un badge a été attribué, par qui, avec les critères et les commentaires. Ce récit apparaît à **3 endroits** :

1. **Passeport** : clic sur un badge → dépliable avec les détails de l'assignment.
2. **Vue Lieu** : clic sur un badge → dépliable avec les détails (qui l'a obtenu, notes).
3. **Multi-focus (home)** : quand badge + structure + personne sont sélectionnés → bloc récit sous les 3 colonnes. Quand badge + structure sont sélectionnés → critères d'attribution du badge par cette structure.

#### E.1 — Dépliable dans le passeport et la vue lieu

Pas de carte surélevée ni de fond spécial. Un simple `<details>` HTML natif, stylisé pour s'intégrer au flux.

```
┌─ Maison des Canuts ────────────────────────────────┐
│  [logo] Maison des Canuts · Lyon 4e                │
│                                                    │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐         │
│  │ Tissage  │  │ Teinture │  │ Design   │         │
│  │ Expert   │  │ Inter.   │  │ Débutant │         │
│  │ mars 24  │  │ jan 24   │  │ nov 23   │         │
│  └─────┬────┘  └──────────┘  └──────────┘         │
│        │                                           │
│  ┌─────▼───────────────────────────────────────┐   │
│  │  Tissage artisanal — Expert                 │   │
│  │  Attribué le 15 mars 2024                   │   │
│  │  par Jean Martin (Maison des Canuts)        │   │
│  │                                             │   │
│  │  Notes : "Marie a réalisé un projet         │   │
│  │  remarquable de tissage Jacquard."          │   │
│  │                                             │   │
│  │  [▶ Audio 0:45]  [▶ Vidéo 2:12]  (futur)   │   │
│  └─────────────────────────────────────────────┘   │
│                                                    │
└────────────────────────────────────────────────────┘
```

**Principes** :
- `<details>` HTML natif, pas de JS pour ouvrir/fermer.
- `<summary>` = la carte badge (icône + nom + niveau + date).
- Contenu déplié : date, assigné par qui, structure, notes.
- Si pas de notes → le bloc notes n'apparaît pas.
- Données déjà chargées via `select_related` (pas d'appel HTMX supplémentaire).

#### E.2 — Bloc récit dans le multi-focus (home)

Deux cas dans le multi-focus :

**Cas 1 : Badge + Structure sélectionnés (2 items)**
→ La 3e colonne (Personnes) montre l'intersection (qui possède ce badge dans cette structure).
→ En plus, un bloc "À propos de ce badge ici" apparaît sous les colonnes.

**Données affichées (phase 1)** : `badge.description` + `endorsement.notes` (si l'endorsement existe). Ces deux champs existent déjà, pas de migration.
**Données affichées (après migration `criteria`)** : `badge.criteria` remplace `badge.description` dans ce bloc. Le champ `criteria` décrit spécifiquement ce qu'il faut faire pour obtenir le badge, alors que `description` décrit le badge lui-même.

```
┌──────────────────┬──────────────────┬──────────────────┐
│  [Badge focus]   │ [Structure focus]│  Personnes (3)   │
│  ×               │  ×               │  Marie Dupont    │
│  Tissage Expert  │  Maison Canuts   │  Jean Martin     │
│                  │                  │  ...             │
├──────────────────┴──────────────────┴──────────────────┤
│                                                        │
│  ── À propos de ce badge ici ────────────────────────  │
│                                                        │
│  Description : "Maîtrise des techniques de tissage…"   │
│  (badge.description, puis badge.criteria quand dispo)  │
│                                                        │
│  Notes d'endossement : "La Maison des Canuts reconnaît │
│  ce badge et l'attribue aux artisans…"                 │
│  (endorsement.notes, si l'endorsement existe)          │
│                                                        │
└────────────────────────────────────────────────────────┘
```

**Cas 2 : Badge + Structure + Personne sélectionnés (3 items)**
→ Les 3 colonnes montrent les détails.
→ Le bloc sous les colonnes montre l'**histoire complète** : description/critères + détail de l'assignment (date, assigné par, notes) + médias (futur).

```
┌──────────────────┬──────────────────┬──────────────────┐
│  [Badge focus]   │ [Structure focus]│  [Personne focus] │
│  ×               │  ×               │  ×               │
│  Tissage Expert  │  Maison Canuts   │  Marie Dupont    │
├──────────────────┴──────────────────┴──────────────────┤
│                                                        │
│  ── Histoire de cet endossement ───────────────────    │
│                                                        │
│  Description : "Maîtrise des techniques de tissage…"   │
│  (badge.criteria si dispo, sinon badge.description)    │
│                                                        │
│  Attribué le 15 mars 2024                              │
│  par Jean Martin (Maison des Canuts)                   │
│                                                        │
│  Notes : "Marie a réalisé un projet remarquable..."    │
│                                                        │
│  [▶ Audio 0:45]  [▶ Vidéo 2:12]  (futur)              │
│                                                        │
└────────────────────────────────────────────────────────┘
```

**Principes** :
- Le bloc apparaît en pleine largeur sous les 3 colonnes, fond `bg-body-secondary`.
- Pas de carte imbriquée, juste du texte structuré avec des séparateurs légers.
- Si aucun critère ni assignment trouvé → le bloc n'apparaît pas.

#### E.3 — Implémentation multi-focus

Dans `multi_focus()` du `HomeViewSet` :

```python
# Si badge + structure sélectionnés, chercher les critères et l'endorsement
# If badge + structure selected, look for criteria and endorsement
if selected_badge and selected_structure:
    endorsement_info = BadgeEndorsement.objects.filter(
        badge=selected_badge,
        structure=selected_structure,
    ).first()
    context['endorsement_info'] = endorsement_info
    # criteria sera sur selected_badge.criteria (après migration)

# Si les 3 sont sélectionnés, chercher aussi l'assignment
# If all 3 are selected, also look for the assignment
if selected_badge and selected_structure and selected_person:
    endorsement_assignment = BadgeAssignment.objects.filter(
        badge=selected_badge,
        assigned_structure=selected_structure,
        user=selected_person,
    ).select_related('assigned_by').first()
    context['endorsement_assignment'] = endorsement_assignment
```

**Template** : partial `templates/core/home/partial/endorsement_story.html`, inclus en bas de `multi_focus.html`.

#### E.4 — Évolutions modèle

**Phase 1** — on utilise ce qui existe :
- `BadgeAssignment.notes` : le champ actuel suffit pour afficher le texte.
- `BadgeAssignment.assigned_by` : qui a assigné.
- `BadgeAssignment.assigned_date` : quand.
- `BadgeEndorsement.notes` : notes de l'endorsement (critères informels).
- `Badge.description` : affiché dans le bloc "À propos" en attendant `criteria`.
- Pas besoin de migration.

**Phase 1.5** — migration prioritaire, dès que lieu + passeport fonctionnent :

1. **Ajouter `criteria` sur `Badge`** : `TextField(blank=True)`. Critères d'attribution publics. Distinct de `description` (qui décrit le badge) — `criteria` décrit ce qu'il faut faire pour l'obtenir. Dans les templates, afficher `badge.criteria or badge.description` pour rétrocompatibilité.

**Phase 3** — enrichir les récits :

2. **Séparer les commentaires** sur `BadgeAssignment` :
   - `structure_comment` : commentaire de la structure qui attribue.
   - `recipient_comment` : commentaire de la personne qui reçoit.
   - L'ancien `notes` reste pour la rétrocompatibilité.

3. **Modèle `EndorsementMedia`** : fichiers audio/vidéo attachés à un assignment.
   - `assignment` (FK BadgeAssignment)
   - `author_type` : 'structure' ou 'recipient'
   - `media_type` : 'audio' ou 'video'
   - `file` (FileField)
   - Lecteurs HTML5 natifs (`<audio>`, `<video>`), pas de librairie JS.
   - Formats : MP3/OGG audio, MP4/WebM vidéo.

**Important** : ne pas créer le modèle `EndorsementMedia` tant que les vues lieu et passeport ne fonctionnent pas. Une feature à la fois.

#### E.5 — Badge "level up" (progression de niveau)

Le `level` (débutant / intermédiaire / expert) est un champ du modèle **Badge**, pas de BadgeAssignment. Concrètement, "Tissage Débutant" et "Tissage Expert" sont deux badges distincts (deux UUID, deux lignes en base). Un "level up" est un nouvel assignment d'un badge différent.

**Conséquences sur l'affichage** :

1. **Passeport** : dans le bloc d'un lieu, une personne peut avoir "Tissage Débutant" (jan 2024) et "Tissage Expert" (mars 2025). Les deux apparaissent comme des badges distincts, triés par date. C'est naturel — ça raconte une progression.

2. **Vue Badge** : la page `/badge/<uuid>/` ne montre qu'un seul niveau. Mais dans la section détenteurs, on pourrait montrer que certains détenteurs ont aussi le niveau supérieur/inférieur. C'est du futur — pour l'instant, chaque badge est indépendant.

3. **Multi-focus** : si badge+structure sont sélectionnés, l'intersection montre les personnes qui ont CE niveau dans CE lieu. Pas de confusion.

4. **Regroupement visuel (futur)** : quand les badges partagent le même nom mais avec des niveaux différents (même `issuing_structure`, même `name`, `level` différent), on pourrait les regrouper visuellement dans le passeport et la vue lieu :

```
┌──────────────────────────────────────────┐
│  Tissage                                 │
│  ★☆☆ Débutant  →  ★★☆ Inter.  →  ★★★ Expert │
│  nov 2023          jan 2024       mars 2025    │
└──────────────────────────────────────────┘
```

Ce regroupement n'est pas prioritaire — phase 3 ou plus tard. En phase 1, chaque badge est une carte individuelle.

**Pas de migration nécessaire** : le modèle actuel gère déjà les niveaux. L'unique_together `['badge', 'assigned_structure', 'user']` empêche de recevoir le **même** badge deux fois de la même structure, mais "Tissage Débutant" et "Tissage Expert" sont deux badges différents.

---

### F. Cartographie ancien code → nouveau code

#### Templates à modifier

| Ancien template | Statut | Nouveau rôle |
|---|---|---|
| `core/home/index.html` | **Conservé** | Inchangé, page d'accueil recherche |
| `core/home/partial/search_results.html` | **À modifier** | Ajouter bouton "Forger un badge" |
| `core/home/partial/badge_focus.html` | **À modifier** | Ajouter bouton "Voir le badge" → `/badge/<uuid>/` + lien "Voir le lieu" → `/lieu/<uuid>/` |
| `core/home/partial/structure_focus.html` | **À modifier** | Lien "Voir le lieu" pointe vers `/lieu/` |
| `core/home/partial/person_focus.html` | **À modifier** | Lien "Voir le passeport" pointe vers `/passeport/` |
| `core/home/partial/multi_focus.html` | **À modifier** | Inclure `endorsement_story.html` en bas (section E) |
| `core/structures/detail.html` | **Remplacé** par `core/lieu/index.html` | Contenu migré (voir A.2) |
| `core/users/detail.html` | **Remplacé** par `core/passeport/index.html` | Contenu migré (voir B.2) |
| `core/users/cv*.html` (4 fichiers) | **Remplacé** par le passeport | Le passeport EST le CV |
| `core/assignments/detail.html` | **Remplacé** | Dépliable dans le passeport |
| `core/assignments/list_user_assignment.html` | **Remplacé** | Intégré dans le passeport (groupé par lieu) |
| `core/badges/detail.html` | **Remplacé** par `core/badge_page/index.html` | Contenu migré vers `/badge/<uuid>/` (section B.6) |
| `core/badges/create.html` | **Conservé** | Lié depuis "Forger un badge" |
| `core/badges/partials/badge_assignment.html` | **Conservé** | Réutilisé en modale HTMX (phase 2) |
| `core/badges/partials/badge_endorsement.html` | **Conservé** | Réutilisé en modale HTMX (phase 2) |
| `core/users/partials/user_profile_edit.html` | **Conservé** | Réutilisé en modale HTMX dans le passeport |
| `authentication/login.html` | **Conservé** | Inchangé |

#### Views à modifier

| Action existante | Statut | Nouveau rôle |
|---|---|---|
| `HomeViewSet.list` | **Conservé** | Inchangé |
| `HomeViewSet.search` | **À modifier** | Passer `search_query` au template pour "Forger" |
| `HomeViewSet.badge_focus` | **À modifier** | Ajouter lien `/badge/` et `/lieu/` dans le contexte |
| `HomeViewSet.structure_focus` | **À modifier** | Ajouter lien `/lieu/` dans le contexte |
| `HomeViewSet.person_focus` | **À modifier** | Ajouter lien `/passeport/` dans le contexte |
| `HomeViewSet.multi_focus` | **À modifier** | Charger endorsement/assignment si badge+structure (section E) |
| `HomeViewSet.lieu` | **Nouveau** | Vue lieu (section A) |
| `HomeViewSet.passeport` | **Nouveau** | Vue passeport (section B) |
| `HomeViewSet.badge_detail` | **Nouveau** | Vue badge (section B.6) |
| `StructureViewSet.retrieve` | **Redirige** | → `/lieu/<uuid>/` (phase 4) |
| `UserViewSet.retrieve` | **Redirige** | → `/passeport/<uuid>/` (phase 4) |
| `UserViewSet.cv` | **Redirige** | → `/passeport/<uuid>/` (phase 4) |
| `AssignmentViewSet.retrieve` | **Redirige** | → `/passeport/<uuid>/` (phase 4) |
| `BadgeViewSet.retrieve` | **Redirige** | → `/badge/<uuid>/` (phase 4) |

#### URLs

| Nouvelle URL | Action | Quand |
|---|---|---|
| `/lieu/<uuid>/` | `HomeViewSet.lieu` | Phase 1 |
| `/passeport/<uuid>/` | `HomeViewSet.passeport` | Phase 1 |
| `/badge/<uuid>/` | `HomeViewSet.badge_detail` | Phase 1 |

Les anciennes URLs (`/structures/<pk>/`, `/users/<pk>/`, `/users/<pk>/cv/`, `/assignments/<pk>/`, `/badges/<pk>/`) continuent de fonctionner via les anciens ViewSets. En phase 4, elles redirigent (HTTP 301) vers les nouvelles URLs.

---

### H. Réflexions UX

**Fluidité de navigation** :
- La home est un **moteur de recherche** (explorer, chercher, découvrir).
- Lieu et passeport sont des **pages de destination** (partager, lire, explorer un contexte).
- Les clics dans les pages de destination ne doivent pas renvoyer vers la home. Un badge dans la vue lieu se déplie sur place (avec un lien discret vers `/badge/`). Un lieu dans le passeport ouvre `/lieu/`. On ne revient à la home que par le bouton "<- FossBadge".

**Deux niveaux de lecture — focus (compact) et page dédiée (complet)** :
- Chaque objet a une version compacte (focus dans la home) ET une page dédiée complète.
- **Le focus et le multi-focus sont le cœur de la home. Ils ne changent pas.** Les pages dédiées sont un complément, pas un remplacement.
- Badge : focus dans la home (existant) + `/badge/<uuid>/` (section B.6).
- Structure : focus dans la home (existant) + `/lieu/<uuid>/` (section A).
- Personne : focus dans la home (existant) + `/passeport/<uuid>/` (section B).
- Bouton "Ouvrir le détail" dans chaque focus pour aller vers la page dédiée.

**Dépliables plutôt que modales** :
- Préférer les `<details>` HTML natifs aux modales SweetAlert2 pour les informations contextuelles.
- Modales uniquement pour les **formulaires** (assigner, endosser, inviter, éditer profil).
- Raison : les dépliables gardent le contexte visible, les modales l'occultent.

**Le passeport remplace le CV** :
- Les 4 templates CV (`cv.html`, `cv_bootstrap.html`, `cv_material.html`, `cv_liquid_glass.html`) disparaissent.
- Le passeport est le seul format. Il est imprimable via `@media print` en CSS.
- Le dropdown "Voir mon CV" dans l'ancien profil disparaît.

**Pas de sur-ingénierie audio/vidéo** :
- Le modèle `EndorsementMedia` ne sera créé qu'après que lieu + passeport fonctionnent.
- Phase 1 : afficher les `notes` existantes, c'est suffisant.
- Phase 3 : enrichir avec critères, commentaires séparés, puis médias.

---

### I. UX générale (améliorations futures)

- [ ] **Pagination / "Voir plus"** : actuellement limité à 5 résultats par catégorie. Ajouter un bouton "Voir tous les badges (12)" qui charge la suite.
- [ ] **Recherche par tags/catégories** : filtres avancés (niveau, domaine, territoire).
- [ ] **Résultats "vides" améliorés** : message contextuel quand une colonne est vide.
- [ ] **Raccourcis clavier** : Escape pour revenir aux résultats, flèches pour naviguer.

### J. Technique

- [ ] **Cache** : mettre en cache les résultats de recherche fréquents (Redis/Memcached).
- [ ] **Recherche full-text** : migrer vers `SearchVector` / `SearchRank` de PostgreSQL.
- [ ] **Tests** : écrire des tests pour chaque action du HomeViewSet + tests HTMX vs no-JS.
- [ ] **SEO** : meta tags dynamiques pour les pages lieu et passeport (Open Graph, titre, description).
- [ ] **Accessibilité** : audit complet WCAG, navigation clavier, annonces aria-live.

### K. Design

- [ ] **Mode sombre** : vérifier que toutes les classes Bootstrap respectent le thème.
- [ ] **Responsive mobile** : les 3 colonnes deviennent un accordéon vertical sur petit écran. Les grilles de badges passent de 3 à 1 colonne.
- [ ] **Illustrations vides** : SVG illustratifs quand il n'y a pas encore de résultats.
- [ ] **Print CSS** : `@media print` pour le passeport (version imprimable propre).
