# Phase 2b — Actions dans la vue lieu

## Prompt a copier-coller

```
Lis le fichier PLAN_HOME.md sections D.2, D.3 (Attribuer et Endosser depuis le lieu)
et section A.1 (wireframe Vue Lieu). Lis aussi CLAUDE.md.

Puis lis :
- templates/core/lieu/index.html (la vue lieu creee en phase 1a)
- templates/core/badge/partial/badge_assignment.html (formulaire existant)
- templates/core/badge/partial/badge_endorsement.html (formulaire existant)
- templates/core/structures/edit.html (formulaire edition structure existant)
- templates/core/structures/detail.html (ancien detail — boutons editer/supprimer)
- core/views.py (BadgeViewSet.assign, BadgeViewSet.endorse)
- core/permissions.py

Ajoute les boutons d'action dans la vue lieu. Il y a 3 types d'action :

**A. Depliable badge avec boutons Attribuer/Endosser**

Dans `lieu/index.html`, quand on clique sur un badge dans la grille, un `<details>`
se deplie. Dans ce depliable, ajouter :

1. Bouton "Attribuer" (si l'utilisateur est admin/editeur de CETTE structure
   ET la structure emet ou endosse ce badge).
   Clic -> modale HTMX qui charge `badge_assignment.html`.
   Le formulaire doit avoir `badge_pk` en hidden et `assigned_structure` pre-rempli
   avec le PK du lieu courant (pas la structure emettrice du badge).
   L'utilisateur ne choisit que la personne + les notes.

2. Bouton "Endosser" (si l'utilisateur est admin/editeur de CETTE structure
   ET le badge n'est PAS emis par cette structure ET pas deja endosse par elle).
   Clic -> modale HTMX qui charge `badge_endorsement.html`.
   Le formulaire a `badge_pk` et `structure` pre-remplis.

Pour les modales HTMX, utilise le pattern :
- Un `<div id="lieu-modal" class="lieu-modal-overlay">` en bas du template
- Le bouton fait `hx-get` vers l'URL d'assignment/endorsement avec les params pre-remplis
- `hx-target="#lieu-modal"` `hx-swap="innerHTML"`
- La modale se ferme avec un bouton X ou un clic en dehors

**B. Boutons Editer/Supprimer structure**

En haut a droite du header, si `is_admin` :
- Bouton "Editer" -> lien vers l'URL d'edition existante.
- Bouton "Supprimer" -> lien vers l'URL de suppression existante.
Discrets (petites icones, pas de gros boutons).

**C. Vue cote serveur**

Modifie la vue `lieu()` dans HomeViewSet pour ajouter au contexte :
- Pour chaque badge de la grille, precalculer `can_assign_this_badge` et
  `can_endorse_this_badge` pour l'utilisateur courant.
  Utilise une boucle simple (FALC) sur les badges :
  ```python
  for badge_item in issued_badges_list:
      badge_item.can_assign = is_admin or is_editor
      badge_item.can_endorse = False  # C'est un badge emis par le lieu
  for badge_item in endorsed_badges_list:
      badge_item.can_assign = is_admin or is_editor
      badge_item.can_endorse = False  # Deja endosse par le lieu
  ```

Attention : les formulaires `badge_assignment.html` et `badge_endorsement.html`
utilisent les vues existantes de BadgeViewSet. Il ne faut PAS creer de nouvelles
vues de soumission. On reutilise les URLs existantes (`badge-assign`, `badge-endorse`).
Si les formulaires attendent des noms de champs specifiques, adapte les hidden fields.

Lis bien les templates de formulaire avant de coder pour comprendre les noms
de champs attendus.
```

## Fichiers concernes

| Fichier | Action |
|---------|--------|
| `templates/core/lieu/index.html` | Ajouter depliables avec boutons + modale |
| `core/views.py` | Modifier `lieu()` pour precalculer permissions par badge |
| `static/css/custom.css` | Styles `.lieu-modal-*` |

## Verification

1. **Boutons Attribuer/Endosser dans le depliable** :
   - [ ] En tant qu'admin du lieu, clic badge -> deplie -> bouton "Attribuer" visible
   - [ ] Clic "Attribuer" -> modale avec formulaire, structure pre-remplie
   - [ ] Soumission du formulaire -> le badge est attribue (verifier en base)
   - [ ] Le bouton "Endosser" n'apparait PAS pour un badge emis par le lieu
   - [ ] En tant que visiteur : pas de boutons

2. **Boutons Editer/Supprimer** :
   - [ ] En tant qu'admin : petites icones en haut a droite
   - [ ] Clic Editer -> page d'edition de la structure
   - [ ] En tant que visiteur : pas de boutons

3. **Modale HTMX** :
   - [ ] La modale s'ouvre proprement (overlay + contenu centre)
   - [ ] La modale se ferme au clic sur X ou en dehors
   - [ ] Apres soumission reussie, la modale se ferme

4. **Pas de regression** :
   - [ ] La page lieu s'affiche correctement sans JS
   - [ ] Les depliables fonctionnent (clic ouvre/ferme)
   - [ ] Les autres pages ne sont pas impactees
