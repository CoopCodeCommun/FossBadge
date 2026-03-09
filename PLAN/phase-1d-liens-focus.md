# Phase 1d — Boutons "Voir le detail" dans les focus

## Prerequis

Les phases 1a, 1b, 1c doivent etre terminees (les 3 pages dediees existent).

## Prompt a copier-coller

```
Lis le fichier PLAN_HOME.md section B.5 (liens entre les vues) et le fichier CLAUDE.md.

Puis lis ces templates de focus existants :
- templates/core/home/partial/badge_focus.html
- templates/core/home/partial/structure_focus.html
- templates/core/home/partial/person_focus.html

Et verifie que les pages dediees existent :
- core/views.py : actions lieu(), passeport(), badge_detail()

Ajoute un bouton "Voir le detail" dans chaque template de focus :

1. **badge_focus.html** : ajoute un bouton "Voir le badge" qui pointe vers
   `/badge/{{ badge.uuid }}/`. Place-le dans la carte de detail du badge,
   sous la description. Style : lien discret, petite fleche ->, couleur
   `--home-color-badges`. Pas un gros bouton, juste un lien texte.

2. **structure_focus.html** : ajoute un bouton "Voir le lieu" qui pointe vers
   `/lieu/{{ structure.uuid }}/`. Place-le dans la carte de detail de la structure,
   sous la description. Style : lien discret, couleur `--home-color-structures`.

3. **person_focus.html** : ajoute un bouton "Voir le passeport" qui pointe vers
   `/passeport/{{ person.uuid }}/`. Place-le dans la carte de detail de la personne.
   Style : lien discret, couleur `--home-color-personnes`.

Principes :
- Ce sont des liens `<a href="...">`, PAS des hx-get. On SORT de la home.
- Ajouter `data-testid` sur chaque lien.
- Ajouter `{% translate %}` sur les textes.
- Le style est coherent entre les 3 templates.
- Ne PAS modifier le comportement de focus/multi-focus existant.
  Le bouton est un complement, pas un remplacement du focus.

Ajoute aussi une classe CSS `.home-detail-link` dans custom.css pour styler
ces liens de maniere uniforme.
```

## Fichiers concernes

| Fichier | Action |
|---------|--------|
| `templates/core/home/partial/badge_focus.html` | Ajouter lien "Voir le badge" |
| `templates/core/home/partial/structure_focus.html` | Ajouter lien "Voir le lieu" |
| `templates/core/home/partial/person_focus.html` | Ajouter lien "Voir le passeport" |
| `static/css/custom.css` | Ajouter `.home-detail-link` |

## Verification

1. **Navigation fonctionnelle** :
   - [ ] Home -> rechercher -> clic badge -> focus badge -> "Voir le badge" -> /badge/<uuid>/
   - [ ] Home -> rechercher -> clic structure -> focus structure -> "Voir le lieu" -> /lieu/<uuid>/
   - [ ] Home -> rechercher -> clic personne -> focus personne -> "Voir le passeport" -> /passeport/<uuid>/

2. **Style coherent** :
   - [ ] Les 3 liens ont le meme style (discret, avec fleche)
   - [ ] Chaque lien est de la couleur de sa categorie

3. **Pas de regression** :
   - [ ] Le focus fonctionne toujours (clic item -> focus dans la colonne)
   - [ ] Le multi-focus fonctionne toujours
   - [ ] La recherche fonctionne toujours
   - [ ] Les liens dans les colonnes liees continuent de pointer vers les focus
