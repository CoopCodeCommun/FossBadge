# Phase 1c — Vue Badge `/badge/<uuid>/`

## Prompt a copier-coller

```
Lis le fichier PLAN_HOME.md section B.6 et le fichier CLAUDE.md.

Puis lis ces fichiers existants :
- templates/core/badges/detail.html (l'ancien detail qu'on remplace)
- templates/core/home/base_home.html (la base a heriter)
- templates/core/home/partial/badge_focus.html (le focus compact existant)
- static/css/custom.css (les styles existants)
- core/views.py (le HomeViewSet)
- core/models.py (Badge, BadgeAssignment, BadgeEndorsement, Structure)
- core/permissions.py

Cree la page dediee `/badge/<uuid>/` selon le plan section B.6. Concretement :

1. **View** : ajoute une action `badge_detail()` dans le HomeViewSet de `core/views.py`.
   L'action est un `@action(detail=False)` avec `url_path="badge/(?P<badge_pk>[^/.]+)"`.
   Utilise le code Python de la section B.6 du plan comme base.
   Docstring FALC bilingue FR/EN.

   Attention a la performance de `can_assign` : le plan itere sur `all_structures`
   avec `any()` et appelle `is_admin()`/`is_editor()` pour chaque structure.
   Prefere une seule query :
   ```python
   can_assign = Structure.objects.filter(
       Q(endorsements__badge=badge) | Q(issued_badges=badge),
       Q(admins=request.user) | Q(editors=request.user),
   ).exists()
   ```

2. **Template** : cree `templates/core/badge_page/index.html` heritant de `base_home.html`.
   Contenu (voir wireframe section B.6) :
   - En-tete horizontal : icone 80px, nom + niveau (pastille) + "Emis par [structure]"
     + description + criteres (si badge.description renseigne).
   - Section "Structures qui reconnaissent ce badge" :
     Liste avec logo + nom + tag "Emetteur" ou "Endosse".
     Clic -> `/lieu/<uuid>/`.
   - Section "Detenteurs" :
     Liste avec avatar + nom + "via [structure d'attribution]".
     Tries par date (plus recent en haut).
     Clic -> `/passeport/<uuid>/`.
   - Boutons d'action en bas (selon permissions) :
     Attribuer, Endosser, Editer, Supprimer.
     Pour l'instant, les boutons sont des liens classiques vers les URLs existantes
     (`badge-assign`, `badge-endorse`, `badge-edit`, `badge-delete`).
     Les modales HTMX viendront en phase 2d.
   - Carte MapLibre en bas si au moins une structure a un marker.
   - Bouton retour "<- FossBadge" en haut a gauche.

3. **CSS** : styles `.badge-page-*` dans `custom.css`. Reutilise `.home-*`.

4. **Accessibilite** : `aria-label`, `data-testid`, `alt` sur images, `<time>` pour dates.

5. **i18n** : `{% translate %}` sur tous les textes.

Ne modifie PAS badge_focus.html ni les autres templates existants.
```

## Fichiers concernes

| Fichier | Action |
|---------|--------|
| `core/views.py` | Ajouter action `badge_detail()` dans HomeViewSet |
| `templates/core/badge_page/index.html` | **Creer** |
| `static/css/custom.css` | Ajouter styles `.badge-page-*` |

## Verification

1. **URL fonctionne** :
   ```bash
   docker exec fossbadge_django uv run python manage.py shell -c "
   from core.models import Badge
   b = Badge.objects.select_related('issuing_structure').first()
   if b:
       print(f'UUID: {b.uuid}')
       print(f'Nom: {b.name}')
       print(f'Niveau: {b.level}')
       print(f'Emetteur: {b.issuing_structure.name}')
   "
   # Puis ouvrir http://localhost:8000/badge/<uuid>/
   ```

2. **Contenu present** :
   - [ ] Icone + nom + niveau + emetteur + description
   - [ ] Liste des structures (emettrice + endosseuses) avec tags
   - [ ] Liste des detenteurs avec avatar et structure d'attribution
   - [ ] Boutons d'action (visibles selon permissions)
   - [ ] Carte si structures avec markers
   - [ ] Bouton retour vers /

3. **Permissions** :
   - [ ] Visiteur : pas de boutons d'action
   - [ ] Admin de la structure emettrice : Editer + Supprimer visibles
   - [ ] Editeur d'une structure endosseuse : Attribuer visible
   - [ ] User avec une structure : Endosser visible

4. **Liens fonctionnels** :
   - [ ] Clic structure -> /lieu/<uuid>/
   - [ ] Clic detenteur -> /passeport/<uuid>/

5. **Pas de regression** : home, lieu, passeport fonctionnent.
