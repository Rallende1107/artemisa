"""Constantes del proyecto: archivos permitidos (extensiones y peso máximo) por TIPO. Un cambio aquí vale para
todos los formularios: el `accept` del input, el texto de ayuda y la validación del `clean_<campo>`."""

MB = 1024 * 1024


def listar_formatos(extensiones: tuple[str, ...]) -> str:
    """(".jpg", ".jpeg", ".png") → «JPG, JPEG o PNG» (sin repetir .jpeg, que es JPG)."""
    nombres = [e.lstrip(".").upper() for e in extensiones if e != ".jpeg"]
    return nombres[0] if len(nombres) == 1 else f"{', '.join(nombres[:-1])} o {nombres[-1]}"


# ---- Imágenes (portadas, categorías, avatares) ----
IMAGE_EXTENSIONS = (".jpg", ".jpeg", ".png", ".webp", ".gif", ".bmp", ".avif")
IMAGE_MAX_MB = 10
IMAGE_ACCEPT = "image/*"
IMAGE_FORMATS = listar_formatos(IMAGE_EXTENSIONS)                  # JPG, PNG, WEBP, GIF, BMP o AVIF
IMAGE_HINT = f"{IMAGE_FORMATS}. Máximo {IMAGE_MAX_MB} MB."

# ---- Audio (canciones) ----
AUDIO_EXTENSIONS = (".mp3", ".flac", ".wav", ".ogg", ".aac", ".m4a", ".wma")
AUDIO_MAX_MB = 50
AUDIO_ACCEPT = "audio/*"
AUDIO_FORMATS = listar_formatos(AUDIO_EXTENSIONS)                  # MP3, FLAC, WAV, OGG, AAC, M4A o WMA
AUDIO_HINT = f"{AUDIO_FORMATS}. Máximo {AUDIO_MAX_MB} MB."

# ---- Documentos (aún sin campo que los use: listos para el primero) ----
DOCUMENT_EXTENSIONS = (".pdf", ".epub", ".cbz", ".cbr", ".txt")
DOCUMENT_MAX_MB = 50
DOCUMENT_ACCEPT = ",".join(DOCUMENT_EXTENSIONS)
DOCUMENT_FORMATS = listar_formatos(DOCUMENT_EXTENSIONS)
DOCUMENT_HINT = f"{DOCUMENT_FORMATS}. Máximo {DOCUMENT_MAX_MB} MB."

# ---- Volcados de datos (dumps JSON de VNDB / MAL) ----
DUMP_EXTENSIONS = (".json", ".json.gz")
DUMP_MAX_MB = 500
