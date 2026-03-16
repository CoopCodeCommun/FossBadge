# Phase 2d — Actions dans la vue badge

## Prompt a copier-coller

```
Lis le fichier PLAN_HOME.md sections D.2, D.3, D.4 et B.6 (boutons dans la vue badge).
Lis aussi CLAUDE.md.

Puis lis :
- templates/core/badge_page/index.html (cree en phase 1c)
- templates/core/badge/partial/badge_assignment.html
- templates/core/badge/partial/badge_endorsement.html
- templates/core/badges/edit.html
- templates/core/badges/delete.html
- templates/core/badges/detail.html (ancien detail — voir comment les boutons
  existants appellent les formulaires)
- core/views.py (BadgeViewSet — methodes assign, endorse, edit, delete)
- core/permissions.py

Transforme les boutons d'action de la vue badge en modales HTMX fonctionnelles :

1. **Bouton "Attribuer"** (si `can_assign`) :
   Ouvre une modale HTMX qui charge `badge_assignment.html`.
   Le champ `badge_pk` est pre-rempli en hidden.
   L'utilisateur choisit la structure parmi celles ou il est admin/editeur
   ET qui endossent/emettent ce badge, puis la personne, puis les notes.

2. **Bouton "Endosser"** (si `can_endorse`) :
   Ouvre une modale qui charge `badge_endorsement.html`.
   Le champ `badge_pk` est pre-rempli.
   L'utilisateur choisit la structure parmi les siennes qui n'endossent
   pas encore ce badge.

3. **Bouton "Editer"** (si `is_badge_editor`) :
   Lien classique vers l'URL d'edition existante (`badge-edit`).
   Pas besoin de modale, le formulaire d'edition est une page complete.

4. **Bouton "Supprimer"** (si `is_badge_editor`) :
   Lien classique vers l'URL de suppression existante (`badge-delete`).
   La page de confirmation existante suffit.

Pour les modales, reutilise le pattern des phases precedentes.
Adapte les hidden fields pour correspondre aux noms de champs attendus
par les formulaires existants.

Lis les vues `assign()` et `endorse()` du BadgeViewSet pour comprendre :
- Quelle URL POST elles attendent
- Quels champs elles attendent dans le body
- Quel template elles retournent apres succes

Si les formulaires existants ne supportent pas le pre-remplissage par
query params, modifie-les pour accepter `?badge_pk=` et `?structure=`.
```

## Fichiers concernes

| Fichier | Action |
|---------|--------|
| `templates/core/badge_page/index.html` | Transformer les liens en modales HTMX |
| `templates/core/badge/partial/badge_assignment.html` | Adapter si besoin (pre-remplissage) |
| `templates/core/badge/partial/badge_endorsement.html` | Adapter si besoin |
| `static/css/custom.css` | Styles modale si pas deja fait |

## Verification

1. **Attribuer** :
   - [ ] En tant qu'admin d'une structure endosseuse : bouton visible
   - [ ] Clic -> modale avec formulaire
   - [ ] Badge pre-rempli (non modifiable)
   - [ ] Soumission -> badge attribue (verifier en base + le detenteur apparait dans la liste)
   - [ ] En tant que visiteur : bouton absent

2. **Endosser** :
   - [ ] En tant qu'admin d'une structure non-endosseuse : bouton visible
   - [ ] Clic -> modale avec formulaire
   - [ ] Soumission -> endorsement cree (verifier en base + structure apparait dans la liste)

3. **Editer/Supprimer** :
   - [ ] En tant qu'admin de la structure emettrice : les 2 boutons visibles
   - [ ] Clic Editer -> page d'edition
   - [ ] Clic Supprimer -> page de confirmation

4. **Coherence des permissions** :
   - [ ] Un user sans structure ne voit aucun bouton d'action
   - [ ] Les boutons correspondent aux permissions de `core/permissions.py`
