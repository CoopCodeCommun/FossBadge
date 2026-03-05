# Phase 1a — Vue Lieu `/lieu/<uuid>/`

## Prompt a copier-coller

```
Lis le fichier PLAN_HOME.md sections A (A.1, A.2, A.3) et le fichier CLAUDE.md.

Puis lis ces fichiers existants pour comprendre le contexte :
- templates/core/structures/detail.html (l'ancien detail qu'on remplace)
- templates/core/home/base_home.html (la base a heriter)
- templates/core/home/partial/structure_focus.html (le focus compact existant)
- static/css/custom.css (les styles .home-* existants)
- core/views.py (le HomeViewSet existant)
- core/models.py (les modeles Structure, Badge, BadgeAssignment, BadgeEndorsement)
- core/permissions.py

Cree la page dediee `/lieu/<uuid>/` selon le plan section A. Concretement :

1. **View** : ajoute une action `lieu()` dans le HomeViewSet de `core/views.py`.
   L'action est un `@action(detail=False)` avec `url_path="lieu/(?P<structure_pk>[^/.]+)"`.
   Utilise le code Python donne dans la section A.3 du plan comme base.
   Ajoute une docstring FALC bilingue FR/EN avec LOCALISATION et FLUX.

2. **Template** : cree `templates/core/lieu/index.html` qui herite de `base_home.html`.
   Contenu (voir le wireframe section A.1) :
   - En-tete horizontal : logo 80px a gauche, nom + type + adresse + description a droite
   - Boutons Editer/Supprimer discrets en haut a droite (si is_admin)
   - Mini carte MapLibre sous l'en-tete si la structure a un marker (180px, non interactive)
   - Section "Badges" : grille de cartes reutilisant les classes `.home-result-item`.
     Chaque badge a un tag "Emis" (orange) ou "Endosse" (bleu).
     Clic sur un badge -> deplie un `<details>` sur place (pas de redirection).
   - Bouton "Forger un badge" en bas de la grille (si is_admin or is_editor).
     Lien vers `{% url 'core:create_badge' %}?structure={{ structure.pk }}`.
   - Section "Personnes" : liste avec avatar + nom + nombre de badges.
     Clic -> `/passeport/<uuid>/` (lien classique href, pas encore HTMX).
   - Section "Referent" en pied si renseigne.
   - Bouton retour "<- FossBadge" en haut a gauche (lien vers /).
   - SIRET en petit texte discret.

3. **CSS** : ajoute les styles `.lieu-*` dans `static/css/custom.css`.
   Reutilise au maximum les classes `.home-*` existantes.
   La mini carte a une hauteur fixe de 180px, border-radius 12px, overflow hidden.
   Le style doit etre sobre et editorial, meme famille visuelle que la home.

4. **Accessibilite** :
   - `aria-label` sur les sections (Badges, Personnes, Referent)
   - `data-testid` sur les elements interactifs
   - `aria-hidden="true"` sur les icones decoratives
   - Les images ont des alt descriptifs

5. **i18n** : tous les textes visibles dans `{% translate %}`.

6. **Pas de JS supplementaire** sauf pour la mini carte MapLibre.
   La mini carte utilise `initHomeMap` de `home_map.js` OU un init simplifie
   (carte statique, pas de popup, pas de liste, juste un marker).

Ne modifie PAS les templates de focus existants (badge_focus.html, etc.).
Les liens vers /passeport/ et /badge/ seront des href classiques pour l'instant
(ces pages n'existent pas encore, on les creera dans les phases suivantes).
```

## Fichiers concernes

| Fichier | Action |
|---------|--------|
| `core/views.py` | Ajouter action `lieu()` dans HomeViewSet |
| `templates/core/lieu/index.html` | **Creer** |
| `static/css/custom.css` | Ajouter styles `.lieu-*` |

## Verification

Apres la realisation, verifier :

1. **URL fonctionne** :
   ```bash
   # Trouver un UUID de structure existant
   docker exec fossbadge_django uv run python manage.py shell -c "
   from core.models import Structure
   s = Structure.objects.first()
   print(f'UUID: {s.uuid}')
   print(f'Nom: {s.name}')
   print(f'Has marker: {bool(s.marker_id)}')
   "
   # Puis ouvrir http://localhost:8000/lieu/<uuid>/ dans le navigateur
   ```

2. **Rendu sans JS** : acceder directement a `/lieu/<uuid>/` (pas via HTMX).
   La page complete doit se charger avec base_home.html.

3. **Contenu present** :
   - [ ] Logo + nom + type + adresse de la structure
   - [ ] Description
   - [ ] Liste des badges (emis + endosses) avec tags colores
   - [ ] Liste des personnes avec avatar
   - [ ] Referent si renseigne
   - [ ] SIRET si renseigne
   - [ ] Bouton retour vers /
   - [ ] Mini carte si marker present

4. **Permissions** :
   - [ ] Visiteur non connecte : pas de boutons Editer/Supprimer/Forger
   - [ ] Admin de la structure : boutons Editer/Supprimer visibles
   - [ ] Editeur de la structure : bouton Forger visible

5. **Accessibilite** : inspecter le HTML pour verifier les `aria-label`, `data-testid`, `alt`.

6. **Pas de regression** : la home page `/` fonctionne toujours normalement.
