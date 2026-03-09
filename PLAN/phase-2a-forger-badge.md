# Phase 2a — Bouton "Forger un badge"

## Prompt a copier-coller

```
Lis le fichier PLAN_HOME.md section D.1 et le fichier CLAUDE.md.

Puis lis :
- templates/core/home/partial/search_results.html
- templates/core/lieu/index.html (cree en phase 1a)
- templates/core/badges/create.html (le formulaire existant)
- core/urls.py (pour trouver l'URL de creation de badge)

Ajoute le bouton "Forger un badge" dans 2 emplacements :

1. **search_results.html** : quand la colonne Badges est vide (aucun resultat),
   ajouter un bouton "Forger un badge" sous le message "aucun resultat".
   Visible uniquement si l'utilisateur est authentifie.
   Lien vers `{% url 'core:create_badge' %}?name={{ search_query|urlencode }}`.
   Le `search_query` doit etre passe dans le contexte de la vue `search()`.

   Verifie que la vue `search()` dans `core/views.py` passe bien `search_query`
   au template. Si ce n'est pas le cas, ajoute-le.

2. **lieu/index.html** : en bas de la grille badges, ajouter le bouton
   "Forger un badge" visible si `is_admin or is_editor`.
   Lien vers `{% url 'core:create_badge' %}?structure={{ structure.pk }}`.

Style du bouton (identique dans les 2 emplacements) :
- Outline, border-color `--home-color-badges`
- Texte couleur `--home-color-badges`
- Au hover : fond plein orange, texte blanc
- Icone marteau/enclume (utiliser une icone Bootstrap Icons `bi-hammer`)
- Pas enorme, discret mais visible
- Classe CSS : `.home-forge-btn`

Ajouter `data-testid="btn-forge-badge"` sur les 2 boutons.
Texte dans `{% translate %}`.
```

## Fichiers concernes

| Fichier | Action |
|---------|--------|
| `templates/core/home/partial/search_results.html` | Ajouter bouton si 0 badges |
| `templates/core/lieu/index.html` | Ajouter bouton si admin/editeur |
| `core/views.py` | Verifier que `search_query` est dans le contexte de `search()` |
| `static/css/custom.css` | Ajouter `.home-forge-btn` |

## Verification

1. **Recherche sans resultat badge** :
   - [ ] Rechercher un terme qui ne donne pas de badge (ex: "zzzzzzz")
   - [ ] Le bouton "Forger un badge" apparait dans la colonne Badges
   - [ ] Le lien contient `?name=zzzzzzz`
   - [ ] Le bouton disparait si l'utilisateur est deconnecte

2. **Vue lieu** :
   - [ ] En tant qu'admin de la structure : le bouton est visible sous les badges
   - [ ] Le lien contient `?structure=<pk>`
   - [ ] En tant que visiteur : le bouton est absent

3. **Le formulaire de creation fonctionne** :
   - [ ] Cliquer "Forger" depuis la recherche -> le champ nom est pre-rempli
   - [ ] Cliquer "Forger" depuis le lieu -> la structure est pre-selectionnee

4. **Style** :
   - [ ] Bouton outline orange, hover orange plein
   - [ ] Meme style dans les 2 emplacements
