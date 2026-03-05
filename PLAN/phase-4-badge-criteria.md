# Phase 4 — Migration BadgeCriteria

## Prompt a copier-coller

```
Lis le fichier PLAN_HOME.md sections E.4 (phase 1.5) et le fichier CLAUDE.md.

Puis lis :
- core/models.py (les modeles existants, notamment Badge et BadgeEndorsement)
- templates/core/home/partial/endorsement_story.html (cree en phase 3)
- templates/core/lieu/index.html (depliable badge)
- templates/core/passeport/index.html (depliable assignment)
- templates/core/badge_page/index.html (page badge)

Cree le modele BadgeCriteria et integre-le dans l'affichage.

1. **Modele** : ajoute dans `core/models.py` :
   ```python
   class BadgeCriteria(models.Model):
       uuid = models.UUIDField(primary_key=True, default=uuid4)
       badge = models.ForeignKey(Badge, on_delete=models.CASCADE, related_name='criteria_set')
       structure = models.ForeignKey(Structure, on_delete=models.CASCADE, related_name='badge_criteria')
       criteria = models.TextField(verbose_name="Criteres d'attribution")

       class Meta:
           unique_together = [['badge', 'structure']]
           verbose_name = "Criteres d'attribution"
           verbose_name_plural = "Criteres d'attribution"
   ```

2. **Migration** : cree et applique la migration.

3. **Affichage** dans 4 endroits :

   a. **endorsement_story.html** (multi-focus) :
      Ajoute les criteres entre la description et les notes d'endorsement.
      "Criteres de [structure] : [texte]".
      La vue `multi_focus()` doit charger `BadgeCriteria.objects.filter(
      badge=selected_badge, structure=selected_structure).first()`.

   b. **lieu/index.html** (depliable badge) :
      Quand on deplie un badge, afficher les criteres de CE lieu pour ce badge
      (si existants). La vue `lieu()` doit precalculer les criteres.

   c. **passeport/index.html** (depliable assignment) :
      Quand on deplie un badge, afficher les criteres de la structure d'attribution
      pour ce badge (si existants). La vue `passeport()` doit faire un lookup
      par `(badge, assigned_structure)`.

   d. **badge_page/index.html** (page badge) :
      Nouvelle section "Criteres par structure" qui liste tous les BadgeCriteria
      de ce badge, groupes par structure. La vue `badge_detail()` doit charger
      `BadgeCriteria.objects.filter(badge=badge).select_related('structure')`.

4. **Admin** : enregistre BadgeCriteria dans l'admin Django pour pouvoir
   creer des criteres de test.

NE PAS implementer la feature "copier les criteres d'une autre structure"
(mentionnee dans le plan). C'est du futur.

NE PAS creer de formulaire de saisie des criteres. Pour l'instant on les
cree via l'admin Django.
```

## Fichiers concernes

| Fichier | Action |
|---------|--------|
| `core/models.py` | Ajouter modele `BadgeCriteria` |
| `core/admin.py` | Enregistrer `BadgeCriteria` |
| `core/views.py` | Modifier `multi_focus()`, `lieu()`, `passeport()`, `badge_detail()` |
| `templates/core/home/partial/endorsement_story.html` | Ajouter criteres |
| `templates/core/lieu/index.html` | Ajouter criteres dans depliable |
| `templates/core/passeport/index.html` | Ajouter criteres dans depliable |
| `templates/core/badge_page/index.html` | Ajouter section criteres |
| Migration | **Creer** |

## Verification

1. **Migration** :
   ```bash
   docker exec fossbadge_django uv run python manage.py makemigrations core
   docker exec fossbadge_django uv run python manage.py migrate
   ```

2. **Creer des donnees de test** :
   ```bash
   docker exec fossbadge_django uv run python manage.py shell -c "
   from core.models import Badge, Structure, BadgeCriteria
   badge = Badge.objects.first()
   structure = badge.issuing_structure
   criteria, created = BadgeCriteria.objects.get_or_create(
       badge=badge,
       structure=structure,
       defaults={'criteria': 'La personne doit demontrer une maitrise complete des techniques.'}
   )
   print(f'Created: {created}, Badge: {badge.name}, Structure: {structure.name}')
   "
   ```

3. **Affichage** :
   - [ ] Multi-focus badge+structure : les criteres apparaissent dans le bloc recit
   - [ ] Vue lieu : depliable badge montre les criteres du lieu
   - [ ] Passeport : depliable assignment montre les criteres de la structure d'attribution
   - [ ] Page badge : section "Criteres" avec liste par structure

4. **Cas sans criteres** :
   - [ ] Si pas de BadgeCriteria -> la section/ligne n'apparait pas (pas de bloc vide)

5. **Admin** :
   - [ ] http://localhost:8000/admin/ -> BadgeCriteria accessible
   - [ ] On peut creer/editer/supprimer des criteres

6. **Unique constraint** :
   ```bash
   # Tenter de creer un doublon doit echouer
   docker exec fossbadge_django uv run python manage.py shell -c "
   from core.models import Badge, Structure, BadgeCriteria
   from django.db import IntegrityError
   badge = Badge.objects.first()
   structure = badge.issuing_structure
   try:
       BadgeCriteria.objects.create(badge=badge, structure=structure, criteria='Doublon')
       print('ERREUR: le doublon a ete cree!')
   except IntegrityError:
       print('OK: IntegrityError levee comme attendu')
   "
   ```
