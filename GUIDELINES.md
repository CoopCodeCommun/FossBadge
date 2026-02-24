# Guidelines TIBILLET

## Projet

**O2Badge** est un moteur opensource de visualisation, de création et de gestion d'open badge
Fabrique par la Cooperative Code Commun, licence AGPLv3.

Stack : Django, Python, Django REST Framework, PostgreSQL, Redis, Memcached, Celery, UV, Docker.

## FALC — Principe fondamental

**FALC = Facile A Lire et Comprendre.** C'est LA regle numero un du projet.

Ce projet est un commun numerique cooperatif. Le code doit etre lisible par des developpeurs non-experts. Concretement :

- **Noms de variables explicites et verbeux.** La longueur n'est pas un probleme.
- **Commentaires bilingues FR/EN** qui expliquent le *pourquoi*, pas le *quoi*.
- **Preferer les boucles `for` simples** aux comprehensions complexes. Le verbeux > le malin.
- **Phrases courtes, mots simples** dans les commentaires et les docstrings.
- **Pas de sucre syntaxique qui masque la logique.** On veut voir ce qui se passe. Eviter les abstractions magiques, les decorateurs complexes, les metaclasses. Le code doit se lire de haut en bas sans devoir aller fouiller dans 5 fichiers.

## Architecture — Choix deliberes

### Controleurs : `viewsets.ViewSet` (pas ModelViewSet)

On utilise `viewsets.ViewSet` de DRF comme controleur, y compris pour les vues qui rendent du HTML.
**Pas de `ModelViewSet`** : c'est trop de magie cachee. On ecrit explicitement `list()`, `retrieve()`, `create()`, etc.
Si besoin de route supplémentaire, on utilise les actions `@action()`.

Les ViewSets retournent soit :
- Des **templates Django** (pages completes ou partiels HTMX) pour l'UI
- Du **JSON** uniquement pour l'API v2 (`api_v2/`)

Exemple type (module `crowds`) :
```python
class InitiativeViewSet(viewsets.ViewSet):
    authentication_classes = [SessionAuthentication]
    permission_classes = [permissions.AllowAny]

    def list(self, request):
        # ... queryset explicite, pas de get_queryset() magique
        return render(request, "crowds/views/list.html", context)

    def retrieve(self, request, pk=None):
        initiative = get_object_or_404(Initiative, uuid=pk)
        return render(request, "crowds/views/detail.html", context)

    @action(detail=True, methods=["POST"])
    def vote(self, request, pk=None):
        # ... retourne un partiel HTMX
        return render(request, "crowds/partial/votes_badge.html", context)
```

### Validation : `serializers.Serializer` (pas de Django Forms)

**On n'utilise pas les forms Django.** Chaque input est valide par un `serializers.Serializer` de DRF.
Pas de `ModelSerializer` sauf dans `api_v2/` pour les endpoints JSON semantiques.

### Frontend : HTMX + Bootstrap 5

- **Rendu cote serveur uniquement.** Les vues retournent du HTML (pages completes ou partiels). Pas de JSON pour l'UI.
- **HTMX** pour les interactions dynamiques : `hx-get`, `hx-post`, `hx-target`, `hx-swap`, `hx-push-url`.
- **Bootstrap 5** pour le style et la grille.
- **Minimal JavaScript.** JS seulement pour les toasts SweetAlert2 et les petites interactions.
- **Anti-blink** : navigation liste/detail via `hx-target="body"` + `hx-swap="innerHTML"` pour ne pas recharger le `<head>`.
- **Toujours conserver `href`/`action`** pour le repli sans JS.
- **CSRF** : `hx-headers='{"X-CSRFToken": "{{ csrf_token }}"}'` sur le `<body>`.
- **i18n** : `{% translate %}` / `gettext` pour tout texte visible.

## Commandes de developpement

**Lancer le serveur en arriere-plan depuis un terminal :**

```bash
# Lance dans le terminal actuel ET garde un trace dans un fichier de log : 
docker exec fossbadge_django uv run python manage.py runserver 0.0.0.0:8000 2>&1 | tee logs/runserver.log
```

Les logs du serveur (tracebacks, requetes) sont ecrits dans un fichier temporaire :

**Pour que le mainteneur suive les logs en temps reel dans un terminal PyCharm :**
```bash
tail -f logs/runserver.log
```


```bash
# Demarrer la stack
docker compose up -d

# Commandes Django dans le conteneur
docker exec fossbadge_django uv run python manage.py <commande>

# Migrations 
docker exec fossbadge_django uv run python manage.py migrate 

# Collectstatic
docker exec fossbadge_django uv run python manage.py collectstatic --no-input

# i18n
docker exec fossbadge_django uv run django-admin makemessages -l fr
docker exec fossbadge_django uv run django-admin makemessages -l en
docker exec fossbadge_django uv run django-admin compilemessages

```

## Tests

### Regles d'ecriture des tests

1. **Atomique** : un test = un comportement precis.
2. **Verbeux** : noms de fonctions longs et clairs.
3. **Bilingue** : commentaires FR + EN.
4. **FALC** : mots simples.
5. **Incremental** : d'abord comprendre la structure (curl), ensuite ecrire le test.

## Accessibilite et themes

- `aria-label` pour les groupes d'info, `visually-hidden` pour decrire les valeurs.
- Ne pas encoder de texte dans les icones; elles sont decoratives (`aria-hidden="true"`).
- Utiliser les classes Bootstrap (`text-body`, `text-muted`, `bg-body-tertiary`, etc.) pour respecter clair/sombre.

## Anti-patterns (a eviter)

- **Reponses JSON pour piloter l'UI** — preferer HTML + `HX-Trigger` pour les toasts.
- **Swapper `html`/`head`** — provoque des clignotements et recharge les assets.
- **JS volumineux** pour des comportements que HTMX gere nativement.
- **ModelViewSet / ModelSerializer** pour les vues templates — trop de magie cachee.
- **Django Forms** — on utilise les serializers DRF.
- **Comprehensions complexes et one-liners** — preferer le code verbeux et lisible.
- **Decorateurs/metaclasses qui cachent la logique** — le code doit se lire lineairement.

## Git

**Ne jamais realiser d'operation git.** Pas de `git add`, `git commit`, `git push`, `git checkout`, `git branch`, etc. Le mainteneur s'en occupe.

## Check‑list avant merge

- [ ] Toutes les interactions renvoient du HTML (partials) — pas de JSON UI.
- [ ] Pas de « blink »: navigations `body` et swaps ciblés.
- [ ] Recherche/pagination/tag OK, URLs mises à jour (`hx-push-url`).
- [ ] FALC: libellés simples, pictos, contrastes, aides d’accessibilité.
- [ ] i18n: tous les labels dans `{% translate %}`.
- [ ] Sécurité: droits des actions, CSRF OK.
- [ ] Admin: URLs fonctionnelles dans Unfold.
