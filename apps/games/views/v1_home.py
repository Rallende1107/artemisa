"""games · los dos HOMES (gestión: tarjetas de entidades; público: filas de portadas)."""
from django.utils.translation import gettext_lazy as _

from apps.games.models import Creator, Game
from apps.games.views.base import _sub_juego
from core.shared.views.base import BaseHomeView, BasePublicHomeView
from core.utils.public import populares_de


# ==============================================================================
# Gestión
# ==============================================================================


class GamesHomeView(BaseHomeView):
    title = 'Juegos'
    active_entity = 'games-home'
    background_image = "bg-games-home"
    background_fallback = "bg-games-home"
    groups = [
        (_("Catálogo"), [
            ('game', _('Juegos'), '<i class="bi bi-controller"></i>', "bg-games-game"),
            ('game-title', _('Títulos'), '<i class="bi bi-type"></i>', "bg-games-title-game"),
            ('game-release', _('Lanzamientos de juego'), '<i class="bi bi-calendar3"></i>', "bg-games-game-release"),
            ('game-release-image', _('Imágenes de lanzamiento'), '<i class="bi bi-images"></i>', "bg-games-game-release-image"),
            ('game-image', _('Imágenes'), '<i class="bi bi-images"></i>', "bg-games-game-image"),
            ('game-link', _('Enlaces'), '<i class="bi bi-link-45deg"></i>', "bg-games-game-link"),
        ]),
        (_("Personajes"), [
            ('game-character', _('Personajes de juego'), '<i class="bi bi-person"></i>', "bg-games-game-character"),
            ('game-character-role', _('Roles de personaje'), '<i class="bi bi-diagram-2"></i>', "bg-games-game-character-role"),
            ('game-character-image', _('Imágenes de personaje de juego'), '<i class="bi bi-image"></i>', "bg-games-game-character-image"),
        ]),
        (_("Creadores"), [
            ('creator', _('Creadores'), '<i class="bi bi-person-gear"></i>', "bg-games-creator"),
            ('creator-nickname', _('Apodos'), '<i class="bi bi-chat-quote"></i>', "bg-games-creator-nickname"),
            ('creator-link', _('Enlaces'), '<i class="bi bi-link-45deg"></i>', "bg-games-creator-link"),
        ]),
        (_("Taxonomías"), [
            ('game-genre', _('Géneros'), '<i class="bi bi-tags"></i>', "bg-games-genre"),
            ('game-genre-alias', _('Alias de géneros'), '<i class="bi bi-tags"></i>', "bg-games-genre-alias"),
            ('tag', _('Etiquetas'), '<i class="bi bi-tag"></i>', "bg-games-tag"),
            ('tag-alias', _('Alias de etiquetas'), '<i class="bi bi-tags"></i>', "bg-games-tag-alias"),
            ('game-engine', _('Motores'), '<i class="bi bi-cpu"></i>', "bg-games-development-engine"),
            ('game-platform', _('Plataformas'), '<i class="bi bi-pc-display"></i>', "bg-games-platform"),
            ('game-medium', _('Medios'), '<i class="bi bi-disc"></i>', "bg-games-medium"),
        ]),
        # A importar se entra por la lista de DATOS de cada tipo (su botón «Importar»), como a un alta se entra
        # por su lista. Aquí solo queda lo que no tiene lista propia: el dump de tags.
        (_("Importación datos · VNDB"), [
            ("data-vndb-game", _("Datos · Juego (VNDB)"), '<i class="bi bi-controller"></i>', "bg-games-data-vndb-game"),
            ("data-vndb-creator", _("Datos · Creador (VNDB)"), '<i class="bi bi-person-workspace"></i>', "bg-games-data-vndb-creator"),
            ("data-vndb-release", _("Datos · Lanzamiento (VNDB)"), '<i class="bi bi-calendar3"></i>', "bg-games-data-vndb-release"),
            ("data-vndb-character", _("Datos · Personaje (VNDB)"), '<i class="bi bi-person"></i>', "bg-games-data-vndb-character"),

        ]),
        # Los dumps NO recorren ninguna API: se carga un archivo y llena la tabla de datos crudos.
        # Procesar es el paso de después, desde la lista de esa tabla.
        (_("Dumps"), [
            ("panel:dump-vndb-game", _("Cargar juegos (VNDB)"), '<i class="bi bi-filetype-json"></i>', "bg-games-load-dump-game"),
            ("panel:dump-vndb-creator", _("Cargar creadores (VNDB)"), '<i class="bi bi-filetype-json"></i>', "bg-games-load-dump-creator"),
            ("panel:dump-vndb-release", _("Cargar lanzamientos (VNDB)"), '<i class="bi bi-filetype-json"></i>', "bg-games-load-dump-release"),
            ("panel:dump-vndb-character", _("Cargar personajes (VNDB)"), '<i class="bi bi-filetype-json"></i>', "bg-games-load-dump-character"),
            ("panel:load-tags-vndb", _("Cargar tags (VNDB)"), '<i class="bi bi-tags"></i>', "bg-games-load-tags-vndb"),
        ]),
        (_("Importación datos · F95"), [
            ("data-f95-game", _("Datos · Juego (F95)"), '<i class="bi bi-joystick"></i>', "bg-games-data-f95-game"),
            ("data-f95-creator", _("Datos · Creador (F95)"), '<i class="bi bi-person-workspace"></i>', "bg-games-data-f95-creator"),
        ]),
        (_("Registro"), [
            ('game-log', _('Log de juegos'), '<i class="bi bi-journal-text"></i>', "bg-games-log"),
        ]),
    ]


# ==============================================================================
# Público
# ==============================================================================


class GamesPublicHomeView(BasePublicHomeView):
    section = "juegos"
    title = _("Visual novels y creadores")
    title_tab = _("Juegos")
    background_image = "bg-games-home"
    background_fallback = "bg-games-home"   # respaldo si falta la imagen
    queryset = Game.objects.filter(is_active=True)
    card_tag = _("Juego")
    card_sub = staticmethod(_sub_juego)
    detail_url = "games:game-detail"

    def get_rows(self):
        """Las filas del home. El `group` de cada una es su PESTAÑA."""
        activos = self.queryset
        creadores = Creator.objects.filter(is_active=True)
        JUEGOS, CREADORES = _("Juegos"), _("Creadores")
        return [
            self.row(
                    _("Juegos recientes"), activos.order_by("-created_at", "title")[:12], url="games:games-catalog", group=JUEGOS
                ),
            self.row(
                    _("Juegos populares"), populares_de(Game), url="games:games-catalog", group=JUEGOS
                ),
            self.row(
                    _("Creadores recientes"), creadores.order_by("-created_at", "name")[:12], _("Creador"), "games:creator-detail", url="games:creators-catalog", sub=lambda o: "", group=CREADORES
                ),
        ]
