"""
Settings ÚNICO de Artemisa — todo se maneja desde el .env.
No hay dev/prod separados: las diferencias se derivan de variables de entorno
(DEBUG, si hay EMAIL_HOST → SMTP, si hay DB_NAME → Postgres, etc.). El .env es
la única palanca. Ver .env.dev (perfil de trabajo) y .env.prod.example.
"""

import os
import sys
from pathlib import Path

try:
    from dotenv import load_dotenv

    load_dotenv()  # carga el .env de la raíz si existe
except ImportError:
    pass  # sin python-dotenv, se usan los defaults

BASE_DIR = Path(__file__).resolve().parent.parent


# ---- helpers de entorno ----
def env(name, default=""):
    return os.getenv(name, default)


def env_bool(name, default=False):
    val = os.getenv(name)
    return default if val is None else val.strip().lower() in ("1", "true", "yes", "on")


def env_list(name, default=""):
    return [x.strip() for x in os.getenv(name, default).split(",") if x.strip()]


# --- Identidad del sitio ---
SITE_NAME = env("SITE_NAME", "Frikiverso")
SITE_TAGLINE = "Todos tus gustos frikis, en un solo lugar"

# Cache-busting de estáticos (?v=...). Súbelo tras editar CSS/JS.
ASSET_VERSION = "346"

# --- Seguridad ---
SECRET_KEY = env("SECRET_KEY", "dev-insecure-cambiar-en-produccion")
DEBUG = env_bool("DEBUG", True)
ALLOWED_HOSTS = env_list("ALLOWED_HOSTS")
# Orígenes confiables extra para CSRF (dominios con esquema, separados por coma).
CSRF_TRUSTED_ORIGINS = env_list("CSRF_TRUSTED_ORIGINS")
# Fallo CSRF (sesión caducada, formulario viejo) → el 403 bonito de la casa.
CSRF_FAILURE_VIEW = "apps.pages.views.csrf_failure_view"

# --- Apps ---
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "import_export",  # importar/exportar por tabla en el /admin/
    "core.apps.CoreConfig",
    # --- Cara pública / cuentas ---
    "apps.pages",
    "apps.users",
    # --- Datos base y sistema (backend) ---
    "apps.catalogs",
    "apps.people",  # personas: entidad transversal (cine, TV, música y otaku la apuntan)
    "apps.companies",  # compañías: entidad transversal (cine, TV y otaku la apuntan)
    "apps.system",
    "apps.mailing",  # correos configurables (plantillas) + registro de enviados
    # --- Apps de contenido ---
    "apps.otaku",
    "apps.music",
    "apps.movies",
    "apps.series",
    "apps.games",
    # --- Staging de import ---
    # --- Colección (tracker del usuario) ---
    "apps.collections",
]

MIDDLEWARE = [
    "django.contrib.sessions.middleware.SessionMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",  # sirve estáticos
    "django.middleware.locale.LocaleMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
]

ROOT_URLCONF = "core.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.template.context_processors.media",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "core.context_processors.sitio",
                "core.context_processors.secciones",
                "core.context_processors.seccion_nav",
                "core.context_processors.sidebar",
            ],
            "loaders": [
                "django.template.loaders.filesystem.Loader",
                "django.template.loaders.app_directories.Loader",
            ],
        },
    },
]

WSGI_APPLICATION = "core.wsgi.application"
ASGI_APPLICATION = "core.asgi.application"

# --- Base de datos ---
# sqlite por defecto. Si defines DB_NAME en el .env → Postgres (para Docker/prod).
if env("DB_NAME"):
    DATABASES = {
        "default": {
            "ENGINE": env("DB_ENGINE", "django.db.backends.postgresql"),
            "NAME": env("DB_NAME"),
            "USER": env("DB_USER"),
            "PASSWORD": env("DB_PASSWORD"),
            "HOST": env("DB_HOST", "localhost"),
            "PORT": env("DB_PORT", "5432"),
            # Postgres, corre la suite ahí y la destruye (con --keepdb la conserva y la reutiliza: más rápido).
        }
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }

# --- Usuarios / autenticación ---
AUTH_USER_MODEL = "users.CustomUser"
AUTHENTICATION_BACKENDS = [
    "apps.users.backends.EmailOrUsernameBackend",
    "django.contrib.auth.backends.ModelBackend",
]
LOGIN_URL = "users:login"
LOGIN_REDIRECT_URL = "/"
LOGOUT_REDIRECT_URL = "/"

# --- Correo ---
# TODO desde el .env: con EMAIL_HOST_PASSWORD definido va por SMTP real
# (Gmail por defecto: contraseña de aplicación); sin él, a la consola (dev).
DEFAULT_FROM_EMAIL = env(
    "DEFAULT_FROM_EMAIL", f"{SITE_NAME} <no-reply@frikiverso.local>"
)
CONTACT_EMAIL = env(
    "CONTACT_EMAIL", DEFAULT_FROM_EMAIL
)  # a dónde llegan los avisos de contacto
SEND_EMAIL = env_bool(
    "SEND_EMAIL", False
)  # MASTER SWITCH: si es False, no se envía NINGÚN correo
PASSWORD_RESET_TIMEOUT = 60 * 60 * 24  # 24 h
if env("EMAIL_HOST_PASSWORD"):
    EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
    EMAIL_HOST = env("EMAIL_HOST", "smtp.gmail.com")
    EMAIL_PORT = int(env("EMAIL_PORT", "587"))
    EMAIL_USE_TLS = env_bool("EMAIL_USE_TLS", True)
    EMAIL_HOST_USER = env("EMAIL_HOST_USER")
    EMAIL_HOST_PASSWORD = env("EMAIL_HOST_PASSWORD")
else:
    EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"


# --- Celery (broker/backend desde el .env; síncrono si no está habilitado) ---
CELERY_ENABLED = env_bool("CELERY_ENABLED", False)
CELERY_TASK_ALWAYS_EAGER = not CELERY_ENABLED
CELERY_TASK_EAGER_PROPAGATES = True
CELERY_BROKER_URL = env("CELERY_BROKER_URL", "redis://localhost:6379/0")
CELERY_RESULT_BACKEND = env("CELERY_RESULT_BACKEND", "redis://localhost:6379/1")
CELERY_TASK_ACKS_LATE = True
# Con ACKS_LATE el mensaje no se confirma hasta ACABAR la tarea, y Redis lo REPARTE OTRA VEZ si en `visibility_timeout`
# nadie lo confirmó (por defecto 1 hora): un barrido de 3 h acababa corriendo por duplicado, misma tarea, mismo id.
# Tiene que superar la tarea más larga que exista; 24 h cubre un barrido entero del catálogo.
CELERY_BROKER_TRANSPORT_OPTIONS = {"visibility_timeout": 24 * 3600}
CELERY_WORKER_PREFETCH_MULTIPLIER = 1
CELERY_BROKER_CONNECTION_RETRY_ON_STARTUP = True

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"
    },
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# --- i18n ---
LANGUAGE_CODE = "es"
LANGUAGES = [("es", "Español"), ("en", "English")]
LOCALE_PATHS = [BASE_DIR / "locale"]
TIME_ZONE = env("TIME_ZONE", "America/Santiago")
USE_I18N = True
USE_TZ = True

# --- Estáticos + Media ---
STATIC_URL = "/static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

# WhiteNoise: manifest comprimido solo si USE_MANIFEST=1 — OJO: el manifest
# post-procesa los url() del CSS y FALLA si referencian archivos que aún no
# existen (fondos pendientes). Sin manifest va COMPRIMIDO igual (gzip/brotli);
# el cache-busting ya lo hace ?v=ASSET_VERSION.
STORAGES = {
    # MEDIA: siempre a disco local (core.storage.MediaLocalYNube); con USE_R2=1 la URL de cada archivo
    # apunta a R2 en cuanto la tarea de subida lo llevó allí (system.CloudFile), y a /media/ mientras tanto.
    "default": {"BACKEND": "core.storage.MediaLocalYNube"},
    "staticfiles": {
        "BACKEND": (
            "whitenoise.storage.CompressedManifestStaticFilesStorage"
            if env_bool("USE_MANIFEST", False)
            else "whitenoise.storage.CompressedStaticFilesStorage"
        )
    },
}

# Cloudflare R2 (S3-compatible) si USE_R2=1: NO reemplaza al disco local; es el destino de la tarea
# «Subir imágenes a R2» (core/shared/tasks/cloud.py, N al día por el tope de subidas). Requiere django-storages + boto3.
USE_R2 = env_bool("USE_R2", False)
R2_PUBLIC_DOMAIN = env("R2_PUBLIC_DOMAIN")
if USE_R2:
    AWS_ACCESS_KEY_ID = env("R2_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY = env("R2_SECRET_ACCESS_KEY")
    AWS_STORAGE_BUCKET_NAME = env("R2_BUCKET")
    AWS_S3_ENDPOINT_URL = env("R2_ENDPOINT_URL")
    AWS_S3_CUSTOM_DOMAIN = env("R2_PUBLIC_DOMAIN")
    AWS_DEFAULT_ACL = None
    AWS_QUERYSTRING_AUTH = False

# --- Seguridad extra en producción (cuando DEBUG=False) ---
if not DEBUG:
    SECURE_SSL_REDIRECT = env_bool("SECURE_SSL_REDIRECT", True)
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_HSTS_SECONDS = int(env("SECURE_HSTS_SECONDS", "0"))
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
