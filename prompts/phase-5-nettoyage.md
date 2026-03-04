# Phase 5 — Nettoyage et redirections

## Prompt a copier-coller

```
Lis le fichier PLAN_HOME.md sections F (cartographie) et C.5 phase 4. Lis aussi CLAUDE.md.

Puis lis :
- core/urls.py
- core/views.py (StructureViewSet.retrieve, UserViewSet.retrieve, BadgeViewSet.retrieve,
  AssignmentViewSet.retrieve)
- Les templates qui vont etre supprimes (juste les lister, pas les lire en detail) :
  templates/core/structures/detail.html
  templates/core/users/detail.html
  templates/core/users/cv.html, cv_bootstrap.html, cv_liquid_glass.html, cv_material.html
  templates/core/assignments/detail.html
  templates/core/assignments/list_user_assignment.html
  templates/core/badges/detail.html

Effectue le nettoyage en 3 etapes :

**Etape 1 : Redirections 301**

Modifie les vues `retrieve()` des anciens ViewSets pour rediriger vers les
nouvelles URLs. Utilise `HttpResponsePermanentRedirect` (HTTP 301) :

- `StructureViewSet.retrieve(pk)` -> redirect vers `/lieu/<structure.uuid>/`
- `UserViewSet.retrieve(pk)` -> redirect vers `/passeport/<user.uuid>/`
- `BadgeViewSet.retrieve(pk)` -> redirect vers `/badge/<badge.uuid>/`
- `AssignmentViewSet.retrieve(pk)` -> redirect vers `/passeport/<assignment.user.uuid>/`
- Les vues CV (`UserViewSet.cv` et variantes) -> redirect vers `/passeport/<user.uuid>/`

Pour chaque redirection :
- Charge l'objet avec get_object_or_404 pour obtenir l'UUID
- Retourne le redirect 301
- Docstring FALC expliquant la redirection

**Etape 2 : Verifier les liens internes**

Cherche dans TOUS les templates du projet les references aux anciennes URLs :
- `{% url 'core:structure-detail' %}` ou similaire
- `{% url 'core:user-detail' %}` ou similaire
- `{% url 'core:badge-detail' %}` ou similaire
- `{% url 'core:assignment-detail' %}` ou similaire

Remplace-les par des liens directs vers `/lieu/`, `/passeport/`, `/badge/`.

Utilise Grep pour trouver toutes les occurrences.

**Etape 3 : Marquer les anciens templates comme deprecies**

NE PAS supprimer les templates pour l'instant. Ajoute juste un commentaire
en haut de chaque ancien template :
```html
<!-- DEPRECATED : ce template est remplace par core/lieu/index.html -->
<!-- Conserve temporairement pour la transition. A supprimer quand -->
<!-- toutes les references auront ete migrees. -->
```

La suppression definitive se fera manuellement par le mainteneur apres
avoir verifie qu'aucune reference ne subsiste.
```

## Fichiers concernes

| Fichier | Action |
|---------|--------|
| `core/views.py` | Modifier retrieve() de chaque ancien ViewSet |
| Tous les templates | Grep + remplacement des liens |
| Anciens templates | Ajouter commentaire DEPRECATED |

## Verification

1. **Redirections** :
   ```bash
   # Tester les redirections 301
   docker exec fossbadge_django uv run python manage.py shell -c "
   from core.models import Structure, User, Badge
   s = Structure.objects.first()
   u = User.objects.first()
   b = Badge.objects.first()
   print(f'Structure: /structures/{s.pk}/ -> /lieu/{s.uuid}/')
   print(f'User: /users/{u.pk}/ -> /passeport/{u.uuid}/')
   print(f'Badge: /badges/{b.pk}/ -> /badge/{b.uuid}/')
   "
   ```
   Puis dans le navigateur, verifier que :
   - [ ] `/structures/<pk>/` redirige (301) vers `/lieu/<uuid>/`
   - [ ] `/users/<pk>/` redirige vers `/passeport/<uuid>/`
   - [ ] `/badges/<pk>/` redirige vers `/badge/<uuid>/`
   - [ ] `/users/<pk>/cv/` redirige vers `/passeport/<uuid>/`

2. **Liens internes** :
   ```bash
   # Verifier qu'il ne reste plus de references aux anciennes URLs
   grep -r "structure-detail\|user-detail\|badge-detail\|assignment-detail" \
     templates/ --include="*.html" | grep -v DEPRECATED
   ```
   - [ ] Aucun resultat (ou seulement les fichiers marques DEPRECATED)

3. **Pas de regression** :
   - [ ] Les anciennes URLs fonctionnent (via redirect)
   - [ ] Les nouvelles pages s'affichent correctement
   - [ ] Les liens de navigation dans les nouvelles pages pointent vers les bonnes URLs
   - [ ] La home, le focus, le multi-focus fonctionnent

4. **SEO** :
   - [ ] Les redirections sont bien des 301 (permanent), pas des 302
   - [ ] Verifier avec curl : `curl -I http://localhost:8000/structures/<pk>/`
     doit retourner `HTTP/1.1 301 Moved Permanently` avec `Location: /lieu/<uuid>/`
