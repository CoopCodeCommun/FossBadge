#!/bin/bash
set -e

#curl -sSL https://install.python-poetry.org | python3
export PATH="/home/fossbadge/.local/bin:$PATH"
uv sync
echo "UV install ok"

#poetry run python3 manage.py migrate
# Install if no asset created :
#poetry run python3 manage.py install
# New static for nginx ?
#poetry run python3 manage.py collectstatic --noinput

uv run python manage.py migrate

if [[ "$GUNICORN" == "1" ]]; then
    echo "→ Gunicorn activé, démarrage…"
    uv run python3 manage.py collectstatic --noinput
    uv run gunicorn fossbadge.wsgi --log-level=info -w 3 -b 0.0.0.0:8000
else
    echo "→ Gunicorn désactivé, on sleep…"
	  echo "To start the server : rsp"
    sleep infinity
fi
#echo "Run GUNICORN"
#echo "You should be able to see the Fedow dashbord at :"
#echo "https://$DOMAIN/dashboard/"
#poetry run gunicorn fossbadgeallet_django.wsgi --log-level=info --log-file /home/fossbadge/Fedow/logs/gunicorn.logs -w 5 -b 0.0.0.0:8000

