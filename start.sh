#!/bin/bash
set -e

#curl -sSL https://install.python-poetry.org | python3
export PATH="/home/fossbadge/.local/bin:$PATH"
poetry install
echo "Poetry install ok"

poetry run python3 manage.py migrate

# Install if no asset created :
poetry run python3 manage.py install
# New static for nginx ?
poetry run python3 manage.py collectstatic --noinput

echo "Run GUNICORN"
echo "You should be able to see the Fedow dashbord at :"
echo "https://$DOMAIN/dashboard/"
sqlite3 ./database/db.sqlite3 'PRAGMA journal_mode=WAL;'
sqlite3 ./database/db.sqlite3 'PRAGMA synchronous=normal;'
poetry run gunicorn fossbadge.wsgi --log-level=info --log-file /home/fossbadge/FossBadge/logs/gunicorn.logs -w 3 -b 0.0.0.0:8000

