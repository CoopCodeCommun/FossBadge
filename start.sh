#!/bin/bash
set -e

#curl -sSL https://install.python-poetry.org | python3
export PATH="/home/fossbadge/.local/bin:$PATH"
uv sync
echo "UV install ok"

# Migrate
uv run python3 manage.py migrate

# Add static to nginx
uv run python3 manage.py collectstatic --noinput

echo "Run GUNICORN"
echo "You should be able to see the fossbadge home at :"
echo "https://$DOMAIN/"

#uv run gunicorn fossbadge.wsgi --log-level=info --log-file /home/fossbadge/FossBadge/logs/gunicorn.logs -w 3 -b 0.0.0.0:8000
uv run gunicorn fossbadge.wsgi --log-level=info -w 3 -b 0.0.0.0:8000
