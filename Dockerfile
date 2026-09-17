# Imagen de Artemisa/Frikiverso: Django + gunicorn + whitenoise.
# La config NO se hornea: sale del .env en tiempo de ejecución (settings único).
FROM python:3.14-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1

# gettext: msgfmt para compilar las traducciones al construir (el .mo no viaja en git).
RUN apt-get update \
    && apt-get install -y --no-install-recommends gettext \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Dependencias primero (capa cacheada mientras no cambien los requirements).
COPY requirements.txt ./
RUN pip install -r requirements.txt

COPY . .
# Blindaje contra CRLF de Windows y permisos del entrypoint.
RUN sed -i 's/\r$//' docker/entrypoint.sh && chmod +x docker/entrypoint.sh \
    && python manage.py compilemessages -l en

EXPOSE 8000
ENTRYPOINT ["./docker/entrypoint.sh"]
