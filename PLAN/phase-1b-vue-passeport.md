# Phase 1b — Vue Passeport `/passeport/<uuid>/`

## Prompt a copier-coller

```
Lis le fichier PLAN_HOME.md sections B (B.1, B.2, B.3, B.4) et le fichier CLAUDE.md.

Puis lis ces fichiers existants pour comprendre le contexte :
- templates/core/users/detail.html (l'ancien profil qu'on remplace)
- templates/core/assignments/detail.html (le detail d'assignment a integrer)
- templates/core/assignments/list_user_assignment.html (la liste qu'on remplace)
- templates/core/home/base_home.html (la base a heriter)
- templates/core/home/partial/person_focus.html (le focus compact existant)
- static/css/custom.css (les styles .home-* et .lieu-* existants)
- core/views.py (le HomeViewSet, notamment la vue lieu() si elle existe deja)
- core/models.py (User, BadgeAssignment, Badge, Structure)

Cree la page dediee `/passeport/<uuid>/` selon le plan section B. Concretement :

1. **View** : ajoute une action `passeport()` dans le HomeViewSet de `core/views.py`.
   L'action est un `@action(detail=False)` avec `url_path="passeport/(?P<person_pk>[^/.]+)"`.
   Utilise le code Python de la section B.4 du plan comme base.
   Docstring FALC bilingue FR/EN avec LOCALISATION et FLUX.

2. **Template** : cree `templates/core/passeport/index.html` qui herite de `base_home.html`.
   Contenu (voir wireframe section B.1) :
   - En-tete horizontal : avatar 80px a gauche, nom + adresse + compteurs a droite.
     Compteurs : "12 badges · 3 lieux" (calcules dans la vue).
   - Tag "Inactif" discret si le user est inactif (is_active=False).
   - Section "Parcours" : **timeline chronologique** du plus recent au plus ancien.
     Chaque badge est un `<details>` HTML natif.
     Le `<summary>` affiche : icone badge, nom, niveau (pastille coloree),
     date d'obtention, "via [structure]" (lien vers /lieu/<uuid>/),
     "par [assigned_by]".
     Si pas de structure (assigned_structure is None) : "attribue par [nom]" sans lieu.
     Le contenu deplie montre : notes (si presentes),
     lien "Voir le badge" -> /badge/<uuid>/,
     lien "Voir le lieu" -> /lieu/<uuid>/ (si structure).
   - Section "Carte du parcours" en bas : MapLibre avec les lieux du parcours.
     Utilise les PKs des structures collectees dans `structures_pks_csv`.
   - Bouton "Editer mon profil" en bas (si is_self). Lien classique pour l'instant.
   - Bouton "Se deconnecter" en haut a droite (si is_self).
   - Bouton retour "<- FossBadge" en haut a gauche (lien vers /).

3. **CSS** : ajoute les styles `.passeport-*` dans `static/css/custom.css`.
   Reutilise les classes `.home-*` existantes.
   Le `<details>` a un style sobre : pas de carte surelevee, juste un fond leger
   au hover sur le summary, et une transition douce a l'ouverture.
   Les pastilles de niveau reutilisent `.home-level-tag`.

4. **Accessibilite** :
   - La timeline est une `<ol>` avec `role="list"` et `aria-label="Parcours"`
   - Chaque `<details>` a un `aria-label` avec le nom du badge
   - `data-testid` sur les elements interactifs
   - Les dates utilisent `<time datetime="...">`

5. **i18n** : tous les textes dans `{% translate %}` et `{% blocktrans %}`.

6. **Important** : chaque badge dans la timeline est une carte INDIVIDUELLE.
   Pas de groupement par structure, pas de groupement par badge.
   Un badge "Tissage Debutant" (jan 2024) et "Tissage Expert" (mars 2025)
   apparaissent comme deux cartes distinctes triees par date.

Ne modifie PAS les templates existants. Les liens vers /badge/<uuid>/ et /lieu/<uuid>/
sont des href classiques (ces pages existent peut-etre deja si phase 1a est faite).
```

## Fichiers concernes

| Fichier | Action |
|---------|--------|
| `core/views.py` | Ajouter action `passeport()` dans HomeViewSet |
| `templates/core/passeport/index.html` | **Creer** |
| `static/css/custom.css` | Ajouter styles `.passeport-*` |

## Verification

1. **URL fonctionne** :
   ```bash
   docker exec fossbadge_django uv run python manage.py shell -c "
   from core.models import User, BadgeAssignment
   u = User.objects.filter(badge_assignments__isnull=False).distinct().first()
   if u:
       count = BadgeAssignment.objects.filter(user=u).count()
       print(f'UUID: {u.uuid}')
       print(f'Nom: {u.get_full_name()}')
       print(f'Badges: {count}')
   else:
       print('Aucun user avec des badges')
   "
   # Puis ouvrir http://localhost:8000/passeport/<uuid>/
   ```

2. **Rendu sans JS** : page complete chargee directement.

3. **Contenu present** :
   - [ ] Avatar + nom + compteurs (badges, lieux)
   - [ ] Timeline chronologique (plus recent en haut)
   - [ ] Chaque badge est un `<details>` cliquable
   - [ ] Le deplie montre les notes et les liens
   - [ ] Badges sans structure affiches correctement ("attribue par X")
   - [ ] Carte du parcours en bas (si structures avec markers)
   - [ ] Bouton retour vers /

4. **Permissions** :
   - [ ] Page publique (tout le monde peut voir un passeport)
   - [ ] "Editer mon profil" visible uniquement si is_self
   - [ ] "Se deconnecter" visible uniquement si is_self

5. **Ordre chronologique** : verifier que les badges sont tries du plus recent au plus ancien.

6. **Pas de regression** : la home page `/` et `/lieu/` fonctionnent toujours.
