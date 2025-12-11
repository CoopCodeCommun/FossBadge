# UV
[(Page d'installation officiel)](https://docs.astral.sh/uv/getting-started/installation/)

---

## Installation

Il y a deux manières principales d'installer UV : 

### Installer depuis le script shell 

Pour lire le script sans l'exécuter :
```shell
  curl -LsSf https://astral.sh/uv/install.sh | less
```
Pour installer uv :
```shell
  curl -LsSf https://astral.sh/uv/install.sh | sh
```


### Installer depuis PyPi

Premièrement il faut installer pipx :

Debian et dérivé :
```shell
  sudo apt install pipx
```
Fedora et dérivé:
```shell
  sudo dnf install pipx
```

Pour s'assurer que le dossier de pipx soit dans le `PATH`, on lance la commande suivante :
```shell
  pipx ensurepath
```

Ensuite, on peut installer UV via pipx :

```shell
  pipx install uv
```

---

## Setup l'application :

```shell
  uv sync # (optionnel, uv le fait automatiquement)
  uv run python manage.py migrate
  uv run python manage.py populate_db --img # (Optionnel)
  uv run python manage.py createsuperuser # (Optionnel)
  uv run python manage.py runserver
```

---

## Commandes de bases :

Mettre à jour le lockfile :
```shell
  uv lock
```

Synchroniser les dépendances :
```shell
  uv sync
```

> **Note :** Uv met à jour le lockfile et synchronise les dépendances de manière automatique quand d'autres commandes sont éxécutées

Ajouter une dépendance :
```shell
  uv add <package_name>
```

Retirer une dépendance :
```shell
  uv remove <package_name>
```

Mettre à jour un paquet :
```shell
  uv lock --upgrade-package <package_name>
```

Mettre à jour tous les paquets : 
```shell
  uv lock --upgrade
```

Lancer des commandes dans l'environment virtuel :
```shell
  uv run <command> [args] ...
```
