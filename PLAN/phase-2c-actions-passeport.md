# Phase 2c — Actions dans le passeport

## Prompt a copier-coller

```
Lis le fichier PLAN_HOME.md section B.1 (boutons conditionnels) et CLAUDE.md.

Puis lis :
- templates/core/passeport/index.html (cree en phase 1b)
- templates/core/users/partials/user_profile_edit.html (formulaire existant)
- templates/core/users/detail.html (l'ancien detail — voir bouton edit et deconnexion)
- core/views.py (UserViewSet, methode d'edition existante)

Ajoute les actions dans le passeport :

1. **Bouton "Editer mon profil"** (si `is_self`) :
   En bas de la page, bouton qui ouvre une modale HTMX.
   La modale charge `user_profile_edit.html` via `hx-get`.
   Reutilise l'URL existante de UserViewSet pour l'edition.
   Apres soumission reussie, la modale se ferme et la page se recharge
   (pour refleter les changements de nom/adresse).

2. **Bouton "Se deconnecter"** (si `is_self`) :
   En haut a droite, petit lien discret vers l'URL de logout existante.
   Utilise l'URL existante de deconnexion.

3. **Lien "Desactiver mon compte"** (si `is_self`) :
   Tout en bas de page, discret, petit texte gris.
   Reutilise le mecanisme existant de `users/detail.html` (lignes 133-151).

Pour la modale HTMX, reutilise le meme pattern que la vue lieu (phase 2b) :
`<div id="passeport-modal">` en bas du template.

Lis bien `user_profile_edit.html` pour comprendre les noms de champs et
l'URL de soumission avant de coder.
```

## Fichiers concernes

| Fichier | Action |
|---------|--------|
| `templates/core/passeport/index.html` | Ajouter boutons + modale |
| `static/css/custom.css` | Styles modale si pas deja fait en 2b |

## Verification

1. **Editer profil** :
   - [ ] Connecte sur son propre passeport : bouton "Editer mon profil" visible
   - [ ] Clic -> modale avec formulaire (nom, prenom, adresse)
   - [ ] Soumission -> modale ferme, page recharge avec les nouvelles infos
   - [ ] Sur le passeport d'un autre : bouton absent

2. **Se deconnecter** :
   - [ ] Connecte sur son propre passeport : lien visible en haut a droite
   - [ ] Clic -> deconnexion, redirection vers la home
   - [ ] Sur un autre passeport : lien absent

3. **Desactiver compte** :
   - [ ] Lien discret tout en bas, uniquement sur son propre passeport

4. **Pas de regression** : la timeline, la carte, le contenu restent intacts.
