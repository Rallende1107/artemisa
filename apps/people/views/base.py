"""BASE de la sección Personas: config por entidad (clases privadas).

La clase privada `_Entidad` es la única fuente de config compartida; las vistas
de los módulos vN_*.py la heredan como PRIMER mixin — estilo Poseidon."""
from django.utils.translation import gettext_lazy as _

from apps.people.models import PeopleLog, Person, PersonImage, PersonLink, PersonNickname
from core.utils.public import url_detail
from core.utils.queries import con_relacion


FONDO_RESPALDO = "bg-catalogs-home"   # respaldo (imagen que sí existe)


def fondo_mal(vista):
    """Detalle / editar / eliminar de una persona CON ficha MAL (otaku.PersonMAL, uno a uno):
    la página usa el fondo otaku que declara el mixin en `background_mal`. Las listas y el alta
    no cambian (mezclan personas, o aún no se sabe cuál es). Mismo criterio que el público."""
    obj = getattr(vista, "object", None)
    persona = obj if isinstance(obj, Person) else getattr(obj, "person", None)
    if persona is not None and getattr(persona, "person_mal", None) is not None:
        vista.background_image = vista.background_mal
        vista.background_fallback = "bg-people-person"


# NAV PÚBLICO de la sección: las pastillas que se ven en las páginas públicas de esta app. Cada entrada es
#   (etiqueta, ruta, icono, {nombres de ruta donde queda ACTIVA})
# y la resuelve `core.context_processors.seccion_nav` (calcula el href y cuál se enciende). Se declara en
# `nav`; una vista puede pisarlo con el suyo, o con () para no pintar barra.
NAV_PUBLICO = (
    (_("Personas"), "personas:home", "bi-people", {"home"}),
    (_("Todas"), "personas:people-catalog", "bi-list-ul", {"people-catalog", "person-detail", "people-by", "person-images-by"}),
    (_("Cine"), "personas:film-catalog", "bi-film", {"film", "film-catalog"}),
    (_("TV"), "personas:tv-catalog", "bi-collection-play", {"tv", "tv-catalog"}),
    (_("Anime y Manga"), "personas:otaku-catalog", "bi-stars", {"otaku", "otaku-catalog"}),
    (_("Voces"), "personas:voices-catalog", "bi-mic", {"voices", "voices-catalog"}),
)


class _People:
    """Lo COMÚN de todas las entidades de la app: respaldo de fondo y sección (breadcrumb)."""
    background_fallback = FONDO_RESPALDO   # respaldo si falta la imagen
    section_url = "panel:people-home"
    section_label = _("Personas")
    nav = NAV_PUBLICO          # las pastillas públicas de la sección


class BasePerson(_People):
    model = Person
    entity = 'person'
    label = _('persona')
    label_plural = _('personas')
    background_image = "bg-people-person"
    background_mal = "bg-otaku-person"          # si la persona tiene ficha MAL

    def get_context_data(self, **kwargs):
        fondo_mal(self)
        return super().get_context_data(**kwargs)


class BasePersonContext(BasePerson):
    """Mapa «por» de personas: tipo → (campo que acota | "app.Modelo" del padre, título, fondo).
    Lo comparten las Data (filtran) y las ListBy (título, fondo, botones) de los dos lados."""
    filter_config = {
        "voces-anime": ("otaku.Anime", _("Actores de voz de {padre}"), "bg-otaku-voice-character"),
        "equipo-anime": ("otaku.Anime", _("Equipo de {padre}"), "bg-otaku-anime-staff"),
        "autores-manga": ("otaku.Manga", _("Autores de {padre}"), "bg-otaku-author-manga"),
        "voces-personaje": ("otaku.Character", _("Voces de {padre}"), "bg-otaku-voice-character"),
        "pais": ("country", _("Personas de {padre}"), "bg-catalogs-country"),
        "integrantes-artista": ("music.Artist", _("Integrantes de {padre}"), "bg-music-artist"),
    }
    sub_via = {"equipo-anime": ('staff', 'person_id', 'role__name'), "autores-manga": ('authors', 'person_id', 'role__name'), "voces-personaje": ('voices', 'person_id', 'language__name')}

    def filter_by(self, qs, padre, tipo):
        if tipo == "voces-anime":
            return qs.filter(voice_roles__is_active=True, voice_roles__character__is_active=True,
                             voice_roles__character__anime_appearances__anime=padre,
                             voice_roles__character__anime_appearances__is_active=True)
        if tipo == "equipo-anime":
            return qs.filter(anime_staff__anime=padre, anime_staff__is_active=True)
        if tipo == "autores-manga":
            return qs.filter(manga_authored__manga=padre, manga_authored__is_active=True)
        if tipo == "voces-personaje":
            return qs.filter(voice_roles__character=padre, voice_roles__is_active=True)
        if tipo == "integrantes-artista":
            return (qs.filter(artist_memberships__artist=padre,
                              artist_memberships__is_active=True).distinct())
        return super().filter_by(qs, padre, tipo)

    def subs_by(self, tipo, padre):
        if tipo == "voces-anime":   # el personaje al que pone voz EN ESTE anime
            from django.apps import apps
            out = {}
            for k, v in apps.get_model("otaku.CharacterVoice").objects.filter(is_active=True, character__anime_appearances__anime=padre).values_list("person_id", "character__full_name"):
                if v:
                    out.setdefault(k, []).append(str(v))
            return {k: ", ".join(v) for k, v in out.items()}
        return super().subs_by(tipo, padre)


class BasePersonImage(_People):
    model = PersonImage
    entity = 'person-image'
    label = _('imagen')
    label_plural = _('imágenes extra')
    background_image = "bg-people-person-image"
    background_mal = "bg-otaku-person"            # la foto es de la persona: su fondo

    def get_context_data(self, **kwargs):
        fondo_mal(self)
        return super().get_context_data(**kwargs)


class BasePersonImageContext(BasePersonImage):
    """Mapa «por» de imágenes extra de persona: tipo → (campo que acota | "app.Modelo" del padre, título, fondo).
    Lo comparten las Data (filtran) y las ListBy (título, fondo, botones) de los dos lados."""
    filter_config = {
        "persona": ("person", _("Imágenes de {padre}"), "bg-people-person"),
    }


class BasePersonLink(_People):
    model = PersonLink
    entity = 'person-link'
    label = _('enlace')
    label_plural = _('enlaces')
    background_image = "bg-people-person-link"


class BasePersonLinkContext(BasePersonLink):
    """Mapa «por» de enlaces de persona: tipo → (campo que acota | "app.Modelo" del padre, título, fondo).
    Lo comparten las Data (filtran) y las ListBy (título, fondo, botones)."""
    filter_config = {
        "persona": ("person", _("Enlaces de {padre}"), ""),
    }


class BasePersonNickname(_People):
    model = PersonNickname
    entity = 'person-nickname'
    label = _('apodo')
    label_plural = _('apodos')
    background_image = "bg-people-person-nickname"
    background_mal = "bg-otaku-person"            # el apodo es de la persona: su fondo

    def get_context_data(self, **kwargs):
        fondo_mal(self)
        return super().get_context_data(**kwargs)


class BasePersonNicknameContext(BasePersonNickname):
    """Mapa «por» de apodos de persona: tipo → (campo que acota | "app.Modelo" del padre, título, fondo).
    Lo comparten las Data (filtran) y las ListBy (título, fondo, botones) de los dos lados."""
    filter_config = {
        "persona": ("person", _("Apodos de {padre}"), ""),
    }


class BasePeopleLog(_People):
    model = PeopleLog
    entity = "people-log"
    label = "log de personas"
    label_plural = "log de personas"
    background_image = "bg-people-log"
    background_fallback = "bg-people-home"   # respaldo si falta la imagen


# Front público de PERSONAS — el corazón del FRONT CRUZADO: landing con
# sub-menús por dominio (cine, TV, anime y manga, voces), catálogos y la ficha
# desde la que se llega a sus obras; y desde cualquier reparto/equipo se llega
# a la persona. El hub de COMPAÑÍAS sigue en `apps/common` (urls).

def _obras(qs, obtener, ruta=None, sub=None, tope=10):
    """Tarjetas de obras: qs de filas through → objeto real via `obtener`.
    REGLA del cruce: lo desactivado (fila o destino) no se muestra."""
    try:
        qs = qs.filter(is_active=True)
    except Exception:
        pass
    items, total = [], qs.count()
    for fila in qs[:tope * 2]:
        if len(items) >= tope:
            break
        obj = obtener(fila)
        if obj is None or not getattr(obj, "is_active", True):
            continue
        items.append({
            "name": str(obj),
            "sub": sub(fila) if sub else "",
            "image": obj.cover_url,
            "url": url_detail(ruta, obj) if ruta else "",
        })
    return items, total


_DOMINIOS = {
    "cine": con_relacion(Person, "movie_cast", "movie_staff"),
    "tv": con_relacion(Person, "serie_cast", "serie_staff"),
    "otaku": con_relacion(Person, "anime_staff", "manga_authored"),
    "voces": con_relacion(Person, "voice_roles"),
}


def _personas_de(dominio):
    qs = Person.objects.filter(is_active=True)
    return qs.filter(_DOMINIOS[dominio]) if dominio else qs
