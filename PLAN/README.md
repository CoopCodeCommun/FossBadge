# Prompts de realisation — PLAN_HOME.md

## Vue d'ensemble

Ce dossier contient les prompts a donner a Claude Code pour realiser le plan
decrit dans `PLAN_HOME.md`. Chaque fichier = une session de travail.

## Phases

| Phase | Fichier | Description | Duree estimee |
|-------|---------|-------------|---------------|
| 1a | `phase-1a-vue-lieu.md` | Page dediee `/lieu/<uuid>/` | 1 session |
| 1b | `phase-1b-vue-passeport.md` | Page dediee `/passeport/<uuid>/` | 1 session |
| 1c | `phase-1c-vue-badge.md` | Page dediee `/badge/<uuid>/` | 1 session |
| 1d | `phase-1d-liens-focus.md` | Boutons "Voir le detail" dans les focus | 1 session courte |
| 2a | `phase-2a-forger-badge.md` | Bouton "Forger un badge" (recherche + lieu) | 1 session courte |
| 2b | `phase-2b-actions-lieu.md` | Boutons d'action dans la vue lieu | 1 session |
| 2c | `phase-2c-actions-passeport.md` | Bouton "Editer profil" dans le passeport | 1 session courte |
| 2d | `phase-2d-actions-badge.md` | Boutons Attribuer/Endosser/Editer/Supprimer | 1 session |
| 3 | `phase-3-bloc-recit.md` | Bloc recit dans le multi-focus | 1 session |
| 4 | `phase-4-badge-criteria.md` | Migration modele BadgeCriteria | 1 session |
| 5 | `phase-5-nettoyage.md` | Redirections 301 + suppression anciens templates | 1 session |

## Quand faire /clear et /compact

### Regle generale

- **`/clear` entre chaque phase** (1a, 1b, 1c, etc.). Chaque phase est independante.
- **`/compact` a l'interieur d'une phase** si le contexte devient lourd (apres ~30 echanges
  ou si Claude commence a oublier des details).

### Guide detaille

```
Phase 1a (vue lieu)         -> /clear
Phase 1b (vue passeport)    -> /clear
Phase 1c (vue badge)        -> /clear
Phase 1d (liens focus)      -> /clear
---
Phase 2a (forger)           -> /clear
Phase 2b (actions lieu)     -> /clear  (reutilise les templates de 1a)
Phase 2c (actions passeport)-> /clear
Phase 2d (actions badge)    -> /clear
---
Phase 3 (bloc recit)        -> /clear
Phase 4 (badge criteria)    -> /clear
Phase 5 (nettoyage)         -> fin
```

### Quand /compact en cours de session

- Apres la creation du template si Claude doit encore ecrire le CSS et le JS
- Apres une longue phase de debug (les tracebacks encombrent le contexte)
- Si Claude repete des informations qu'il a deja dites

## Dependances entre phases

```
1a (lieu) ─────────────┐
1b (passeport) ────────┤── 1d (liens focus) ── 2a (forger)
1c (badge) ────────────┘
                            │
                            ├── 2b (actions lieu)
                            ├── 2c (actions passeport)
                            └── 2d (actions badge)
                                    │
                                    └── 3 (bloc recit) ── 4 (criteria) ── 5 (nettoyage)
```

Les phases 1a, 1b, 1c sont independantes entre elles et peuvent etre faites
dans n'importe quel ordre. Mais 1d depend des trois.
