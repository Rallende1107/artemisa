#!/bin/sh
# Arranque del contenedor: espera la BD, migra, junta estáticos y levanta
# gunicorn. Toda la config viene del entorno (.env vía docker-compose).
set -e

python - <<'PY'
import os
import time

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
django.setup()

from django.db import connections
from django.db.utils import OperationalError

for _ in range(30):
    try:
        connections["default"].cursor()
        break
    except OperationalError:
        time.sleep(1)
else:
    raise SystemExit("BD inalcanzable tras 30 s")
PY

# Con comando propio (worker/beat de Celery) solo se espera la BD y se ejecuta;
# el rol web (sin argumentos) además junta estáticos (sin DEV).
if [ "$#" -gt 0 ]; then
    exec "$@"
fi

# El web NO migra al arrancar: la base la crea `init` (un comando, una acción). Si el web
# migrara solo, aplicaría las migraciones que haya en la carpeta en ese momento (viejas o
# ninguna) y luego `clear_migrations` + `makemigrations` generarían 0001 con el mismo nombre
# que la base ya cree aplicadas: tablas viejas con código nuevo.

# DEV=1 en el .env → runserver con AUTORELOAD: tocas un .py o una plantilla y
# el contenedor se recarga solo (el codigo va montado como volumen). Los
# estaticos se sirven en vivo desde static/, sin collectstatic.
if [ "${DEV:-0}" = "1" ]; then
    echo ">> MODO DEV: runserver con autoreload (hot reload dentro de Docker)"
    exec python manage.py runserver 0.0.0.0:8000
fi

python manage.py collectstatic --noinput
# Sin access-log de gunicorn: ese ruido (una línea por request con user-agent)
# ya lo registra nginx. Aquí queda solo la SEÑAL: los «Not Found: /x» de
# Django, los errores de Python y el arranque — como la consola del runserver.
exec gunicorn core.wsgi:application \
    --bind 0.0.0.0:8000 \
    --workers "${GUNICORN_WORKERS:-3}" \
    --error-logfile -
