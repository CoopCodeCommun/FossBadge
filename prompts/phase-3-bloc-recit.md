# Phase 3 — Bloc recit dans le multi-focus

## Prompt a copier-coller

```
Lis le fichier PLAN_HOME.md sections E.1, E.2, E.3 et le fichier CLAUDE.md.

Puis lis :
- templates/core/home/partial/multi_focus.html
- core/views.py (HomeViewSet.multi_focus)
- core/models.py (BadgeAssignment, BadgeEndorsement, Badge)

Ajoute le bloc recit ("endorsement story") dans le multi-focus.
Il y a 2 cas :

**Cas 1 : Badge + Structure selectionnes (2 items)**

Sous les 3 colonnes, ajouter un bloc "A propos de ce badge ici" qui affiche :
- `badge.description` (toujours affiche, c'est la description generale)
- `endorsement.notes` (si un endorsement existe entre ce badge et cette structure)

Modifie la vue `multi_focus()` pour charger ces donnees :
```python
# Si badge + structure selectionnes, chercher l'endorsement
# If badge + structure selected, look for endorsement
if selected_badge and selected_structure:
    try:
        endorsement_info = BadgeEndorsement.objects.get(
            badge=selected_badge,
            structure=selected_structure,
        )
    except BadgeEndorsement.DoesNotExist:
        endorsement_info = None
    context['endorsement_info'] = endorsement_info
```

**Cas 2 : Badge + Structure + Personne selectionnes (3 items)**

Le bloc devient "Histoire de cet endossement" et affiche en plus :
- Date d'attribution
- "par [assigned_by] ([structure])"
- Notes de l'assignment

Modifie la vue pour charger aussi l'assignment :
```python
if selected_badge and selected_structure and selected_person:
    try:
        endorsement_assignment = BadgeAssignment.objects.select_related(
            'assigned_by'
        ).get(
            badge=selected_badge,
            assigned_structure=selected_structure,
            user=selected_person,
        )
    except BadgeAssignment.DoesNotExist:
        endorsement_assignment = None
    context['endorsement_assignment'] = endorsement_assignment
```

**Template** : cree `templates/core/home/partial/endorsement_story.html`.
Inclus-le en bas de `multi_focus.html` avec `{% include %}`.

Le bloc est sobre : pleine largeur sous les colonnes, fond `bg-body-secondary`,
padding 1.5rem, pas de carte surelevee. Juste du texte structure avec des
separateurs legers.

Si ni description, ni endorsement, ni assignment n'existent -> le bloc ne
s'affiche pas du tout.

i18n : `{% translate %}` et `{% blocktrans %}` pour les textes.
Accessibilite : `aria-label` sur le bloc, dates dans `<time>`.
```

## Fichiers concernes

| Fichier | Action |
|---------|--------|
| `core/views.py` | Modifier `multi_focus()` pour charger endorsement/assignment |
| `templates/core/home/partial/endorsement_story.html` | **Creer** |
| `templates/core/home/partial/multi_focus.html` | Ajouter `{% include %}` |
| `static/css/custom.css` | Styles `.home-story-*` si necessaire |

## Verification

1. **Cas badge + structure** :
   ```bash
   # Trouver un badge endosse par une structure
   docker exec fossbadge_django uv run python manage.py shell -c "
   from core.models import BadgeEndorsement
   e = BadgeEndorsement.objects.select_related('badge', 'structure').first()
   if e:
       print(f'Badge UUID: {e.badge.uuid}')
       print(f'Structure UUID: {e.structure.uuid}')
       print(f'Notes: {e.notes}')
   "
   ```
   - [ ] Selectionner ce badge + cette structure dans la home
   - [ ] Le bloc "A propos" apparait sous les colonnes
   - [ ] La description du badge est affichee
   - [ ] Les notes d'endorsement sont affichees (si presentes)

2. **Cas badge + structure + personne** :
   ```bash
   docker exec fossbadge_django uv run python manage.py shell -c "
   from core.models import BadgeAssignment
   a = BadgeAssignment.objects.select_related(
       'badge', 'assigned_structure', 'user', 'assigned_by'
   ).filter(assigned_structure__isnull=False).first()
   if a:
       print(f'Badge UUID: {a.badge.uuid}')
       print(f'Structure UUID: {a.assigned_structure.uuid}')
       print(f'User UUID: {a.user.uuid}')
       print(f'Notes: {a.notes}')
   "
   ```
   - [ ] Selectionner les 3 dans la home
   - [ ] Le bloc "Histoire" apparait avec date, assigneur, notes

3. **Cas sans donnees** :
   - [ ] Selectionner badge + structure sans endorsement -> bloc avec description seule
   - [ ] Si badge sans description ET pas d'endorsement -> pas de bloc

4. **Pas de regression** :
   - [ ] Multi-focus 2 items fonctionne (colonnes + intersection)
   - [ ] Multi-focus 3 items fonctionne
   - [ ] Boutons X de retrait fonctionnent
