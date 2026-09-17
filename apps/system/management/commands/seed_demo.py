"""Seed DEMO temporal: 5 series, 5 películas, 5 juegos, 5 animes y 5 mangas
REALES en la BD, con portadas tomadas de una carpeta local de imágenes.

Para probar el panel con datos de verdad, el renderizado de portadas en las
vistas públicas y el flujo de colección (añadir/quitar). Idempotente:
`get_or_create` por título — correrlo dos veces no duplica nada.

    python manage.py seed_demo
    python manage.py seed_demo --imagenes "D:\\jago 100"
"""
from pathlib import Path

from django.core.files import File
from django.core.management.base import BaseCommand

from apps.companies.models import Company
from apps.games import models as games
from apps.movies import models as movie
from apps.otaku import models as otaku
from apps.series import models as serie
from core.shared.models.choices import MalRating


SERIES = [
    ("Breaking Bad", 2008, "Un profesor de química con cáncer se convierte en fabricante de metanfetamina."),
    ("Dark", 2017, "Cuatro familias de Winden atrapadas en un ciclo de viajes en el tiempo."),
    ("Severance", 2022, "Empleados con la memoria dividida entre el trabajo y su vida personal."),
    ("The Bear", 2022, "Un chef de alta cocina vuelve a Chicago a salvar la sandwichería familiar."),
    ("Shōgun", 2024, "Un navegante inglés naufraga en el Japón feudal en plena lucha de poder."),
]
MOVIES = [
    ("Interstellar", 2014, "Una expedición atraviesa un agujero de gusano en busca de un nuevo hogar."),
    ("El viaje de Chihiro", 2001, "Una niña queda atrapada en un mundo de espíritus y debe salvar a sus padres."),
    ("Parasite", 2019, "Una familia pobre se infiltra en la vida de una familia rica."),
    ("Mad Max: Fury Road", 2015, "Una huida frenética por el desierto en un mundo postapocalíptico."),
    ("Blade Runner 2049", 2017, "Un blade runner descubre un secreto que puede romper la sociedad."),
]
GAMES = [
    ("Doki Doki Literature Club", 2017, "Un club de literatura escolar que no es lo que parece."),
    ("Katawa Shoujo", 2012, "Una novela visual sobre la vida en la academia Yamaku."),
    ("Clannad", 2004, "Un estudiante desencantado y las historias que cambian su vida."),
    ("Steins;Gate", 2009, "Un microondas que envía mensajes al pasado y sus consecuencias."),
    ("Everlasting Summer", 2013, "Un joven despierta en un campamento soviético fuera del tiempo."),
]
ANIMES = [
    ("Fullmetal Alchemist: Brotherhood", 2009, 64, "Dos hermanos buscan la piedra filosofal para recuperar sus cuerpos."),
    ("Shingeki no Kyojin", 2013, 25, "La humanidad resiste tras murallas al acecho de los titanes."),
    ("Sousou no Frieren", 2023, 28, "Una maga elfa emprende un viaje para entender a los humanos."),
    ("Death Note", 2006, 37, "Un cuaderno que mata a quien cuyo nombre se escriba en él."),
    ("One Punch Man", 2015, 12, "Un héroe capaz de vencer a cualquiera de un solo golpe."),
]
MANGAS = [
    ("Berserk", 1989, 0, "La venganza de Guts, el espadachín negro, en un mundo oscuro."),
    ("One Piece", 1997, 0, "Luffy y su tripulación buscan el tesoro más grande del mundo."),
    ("Monster", 1994, 162, "Un neurocirujano persigue al monstruo que él mismo salvó."),
    ("Vagabond", 1998, 327, "La vida del legendario espadachín Miyamoto Musashi."),
    ("Chainsaw Man", 2018, 97, "Un cazador de demonios fusionado con su motosierra."),
]


class Command(BaseCommand):
    help = "Crea datos DEMO reales (series, películas, juegos, animes, mangas) con portadas."

    def add_arguments(self, parser):
        parser.add_argument("--imagenes", default=r"D:\jago 100",
                            help="Carpeta local con imágenes para las portadas.")
        parser.add_argument("--masivo", action="store_true",
                            help="Volumen de ESTRÉS por serie/película: 30 de reparto, "
                                 "20 de equipo y 100 fotos extra (para ver el comportamiento).")
        parser.add_argument("--repartos", action="store_true",
                            help="Repartos ENORMES en todos los medios: 30 reparto + 20 equipo "
                                 "por película/serie, 20 staff + 12 personajes por anime, "
                                 "4 autores + 8 personajes por manga, con voces (bulk).")
        parser.add_argument("--industria", type=int, default=0, metavar="N",
                            help="Crea N compañías por modelo (cine, TV, estudios, productoras, "
                                 "licenciatarias, revistas) y las reparte entre los títulos (bulk).")
        parser.add_argument("--biblioteca", type=int, default=0, metavar="N",
                            help="Genera N títulos por medio (películas, series, animes, "
                                 "mangas, juegos) y AÑADE TODO a la colección del primer "
                                 "superusuario, con estados/notas/favoritos variados.")
        parser.add_argument("--limpiar", action="store_true",
                            help="BORRA la paja demo: oyentes y sus colecciones, la "
                                 "Orquesta Errante, las traducciones lorem de canciones "
                                 "y el hilo de contacto de prueba. No toca títulos ni "
                                 "personas reales.")

    def handle(self, *args, **opts):
        if opts["limpiar"]:
            self._limpiar()
            return
        self.imgs = sorted(Path(opts["imagenes"]).glob("*.jpg"))
        if not self.imgs:
            self.stdout.write(self.style.WARNING("Sin imágenes: las entradas quedan sin portada."))
        self.idx = 0

        creados = 0
        for title, year, syn in SERIES:
            obj, new = serie.Serie.objects.get_or_create(
                title=title, defaults={"release_year": year, "synopsis": syn})
            creados += self._final(obj, new, serie.Genre)
        for title, year, syn in MOVIES:
            obj, new = movie.Movie.objects.get_or_create(
                title=title, defaults={"release_year": year, "synopsis": syn})
            creados += self._final(obj, new, movie.Genre)
        for title, year, syn in GAMES:
            obj, new = games.Game.objects.get_or_create(
                title=title, defaults={"release_date": f"{year}-01-01", "synopsis": syn})
            creados += self._final(obj, new, games.Genre)
        for title, year, eps, syn in ANIMES:
            obj, new = otaku.Anime.objects.get_or_create(
                title=title, defaults={"year": year, "episodes": eps, "synopsis": syn})
            creados += self._final(obj, new, otaku.Genre)
        for title, year, caps, syn in MANGAS:
            obj, new = otaku.Manga.objects.get_or_create(
                title=title, defaults={"year": year, "chapters": caps, "synopsis": syn})
            creados += self._final(obj, new, otaku.Genre)

        self._personas_y_reparto()
        self._enriquecer()
        self._relaciones_obras()
        self._otaku_completo()
        self._creadores_de_juegos()
        self._personajes()
        self._coleccion_musica()
        self._coleccion_catalogo()
        self._personas_y_artistas_con_filtros()
        if opts["masivo"]:
            self._masivo()
        if opts["biblioteca"]:
            self._biblioteca(opts["biblioteca"])
        if opts["industria"]:
            self._industria(opts["industria"])
        if opts["repartos"]:
            self._repartos_masivos()

        self.stdout.write(self.style.SUCCESS(f"Seed demo listo: {creados} entradas nuevas "
                                             f"(las existentes se conservan)."))

    def _relaciones_obras(self):
        """Relaciones entre películas de la demo (secuela / precuela / spin-off), con el catálogo genérico de tipos."""
        from apps.catalogs.models import RelationType
        tipos = {n: RelationType.objects.filter(name=n).first() for n in ("Sequel", "Prequel", "Spin-Off")}
        pelis = {m.title: m for m in movie.Movie.objects.filter(title__in=[t for t, _y, _s in MOVIES])}
        for a, b, tipo in [("Parasite", "Blade Runner 2049", "Sequel"), ("Blade Runner 2049", "Parasite", "Prequel"), ("Parasite", "Mad Max: Fury Road", "Spin-Off")]:
            if a in pelis and b in pelis and tipos.get(tipo):
                movie.MovieRelation.objects.get_or_create(movie=pelis[a], related=pelis[b], relation_type=tipos[tipo])

    def _otaku_completo(self):
        """Los animes y mangas de la demo con TODO lo que pinta la ficha: tipo, estado, fuente, temporada,
        clasificación, demografía, estudio/productora/licenciataria (o revista), títulos alternativos, equipo,
        voces (japonés e inglés), banda sonora (OP/ED/insert con artista), autores del manga y relaciones
        anime↔manga / secuela. Idempotente (get_or_create)."""
        from apps.catalogs.models import Language, RelationType
        from apps.music.models import Artist
        from apps.people.models import Person

        def cat(Model, name):
            return Model.objects.filter(name=name).first() or Model.objects.create(name=name)

        def persona(nombre):
            return Person.objects.get_or_create(full_name=nombre)[0]

        def rol(nombre):
            return otaku.Role.objects.filter(name=nombre).first() or otaku.Role.objects.create(name=nombre)

        jap = Language.objects.filter(name__in=("Japanese", "Japonés")).first() or Language.objects.create(name="Japanese")
        eng = Language.objects.filter(name__in=("English", "Inglés")).first() or Language.objects.create(name="English")
        tv, manga_t = cat(otaku.Type, "TV"), cat(otaku.Type, "Manga")
        fin, pub = cat(otaku.Status, "Finished Airing"), cat(otaku.Status, "Publishing")
        shounen = cat(otaku.Demographic, "Shounen")
        r17 = MalRating.R17
        director, guion, musica = rol("Director"), rol("Script"), rol("Music")
        autor = otaku.Role.objects.filter(name__in=("Story & Art", "Art & Story")).first() or rol("Story & Art")
        tipo_cancion = {"op": "OPENING", "ed": "ENDING", "in": "INSERT"}
        adapt, sequel, prequel = (RelationType.objects.filter(name=n).first() for n in ("Adaptation", "Sequel", "Prequel"))

        # (anime, japonés, inglés, temporada, fuente, estudio, productora, licenciataria, director, guion, música,
        #  [(tipo, nº, título, artista)], manga adaptado (título, año, capítulos, autor, revista))
        ANIMES_FULL = [
            ("Fullmetal Alchemist: Brotherhood", "鋼の錬金術師 FULLMETAL ALCHEMIST", "Fullmetal Alchemist: Brotherhood", "Spring", "Manga",
             "Bones", "Aniplex", "Funimation", "Yasuhiro Irie", "Hiroshi Ohnogi", "Akira Senju",
             [("op", 1, "Again", "YUI"), ("op", 2, "Hologram", "NICO Touches the Walls"), ("ed", 1, "Uso", "SID"), ("ed", 2, "Let It Out", "Miho Fukuhara"), ("in", 1, "Lapis Philosophorum", "Akira Senju")],
             ("Fullmetal Alchemist", 2001, 116, "Hiromu Arakawa", "Monthly Shounen Gangan")),
            ("Shingeki no Kyojin", "進撃の巨人", "Attack on Titan", "Spring", "Manga",
             "Wit Studio", "Production I.G", "Funimation", "Tetsurou Araki", "Yasuko Kobayashi", "Hiroyuki Sawano",
             [("op", 1, "Guren no Yumiya", "Linked Horizon"), ("op", 2, "Jiyuu no Tsubasa", "Linked Horizon"), ("ed", 1, "Utsukushiki Zankoku na Sekai", "Yoko Hikasa"), ("in", 1, "Vogel im Käfig", "Hiroyuki Sawano"), ("in", 2, "Call your name", "Hiroyuki Sawano")],
             ("Shingeki no Kyojin", 2009, 139, "Hajime Isayama", "Bessatsu Shounen Magazine")),
            ("Sousou no Frieren", "葬送のフリーレン", "Frieren: Beyond Journey's End", "Fall", "Manga",
             "Madhouse", "Toho Animation", "Crunchyroll", "Keiichirou Saitou", "Tomohiro Suzuki", "Evan Call",
             [("op", 1, "Yuusha", "YOASOBI"), ("ed", 1, "Anytime Anywhere", "milet"), ("in", 1, "Bliss", "milet")],
             ("Sousou no Frieren", 2020, 0, "Kanehito Yamada", "Weekly Shounen Sunday")),
            ("Death Note", "デスノート", "Death Note", "Fall", "Manga",
             "Madhouse", "VAP", "Viz Media", "Tetsurou Araki", "Toshiki Inoue", "Yoshihisa Hirano",
             [("op", 1, "the WORLD", "Nightmare"), ("op", 2, "What's up, people?!", "Maximum the Hormone"), ("ed", 1, "Alumina", "Nightmare"), ("in", 1, "Kyrie", "Yoshihisa Hirano")],
             ("Death Note", 2003, 108, "Tsugumi Ohba", "Weekly Shounen Jump")),
            ("One Punch Man", "ワンパンマン", "One Punch Man", "Fall", "Web Manga",
             "Madhouse", "Bandai Namco Pictures", "Viz Media", "Shingo Natsume", "Tomohiro Suzuki", "Makoto Miyazaki",
             [("op", 1, "THE HERO !!", "JAM Project"), ("ed", 1, "Hoshi yori Saki ni Mitsukete Ageru", "Hiroko Moriguchi")],
             ("One Punch-Man", 2012, 0, "ONE", "Tonari no Young Jump")),
        ]
        VOCES = {   # personaje → (seiyū japonés, voz inglesa)
            "Edward Elric": ("Romi Park", "Vic Mignogna"), "Alphonse Elric": ("Rie Kugimiya", "Maxey Whitehead"),
            "Roy Mustang": ("Shinichiro Miki", "Travis Willingham"), "Eren Yeager": ("Yuki Kaji", "Bryce Papenbrook"),
            "Mikasa Ackerman": ("Yui Ishikawa", "Trina Nishimura"), "Levi": ("Hiroshi Kamiya", "Matthew Mercer"),
            "Frieren": ("Atsumi Tanezaki", "Mallorie Rodak"), "Fern": ("Kana Ichinose", "Jill Harris"),
            "Light Yagami": ("Mamoru Miyano", "Brad Swaile"), "L": ("Kappei Yamaguchi", "Alessandro Juliani"),
            "Misa Amane": ("Aya Hirano", "Shannon Chan-Kent"), "Saitama": ("Makoto Furukawa", "Max Mittelman"),
            "Genos": ("Kaito Ishikawa", "Zach Aguilar"),
        }
        MANGAS_FULL = {  # manga de la demo → (autor, revista)
            "Berserk": ("Kentarou Miura", "Young Animal"), "One Piece": ("Eiichiro Oda", "Weekly Shounen Jump"),
            "Monster": ("Naoki Urasawa", "Big Comic Original"), "Vagabond": ("Takehiko Inoue", "Weekly Morning"),
            "Chainsaw Man": ("Tatsuki Fujimoto", "Weekly Shounen Jump"),
        }

        def relacion(a_kind, a, b_kind, b, tipo):
            if tipo and a.mal_id is not None and b.mal_id is not None:
                otaku.Relation.objects.get_or_create(from_type=a_kind, from_mal_id=a.mal_id, to_type=b_kind, to_mal_id=b.mal_id,
                                                     defaults={"relation_type": tipo})

        def manga_de(titulo, anio, caps, autor_n, revista):
            m, nuevo = otaku.Manga.objects.get_or_create(title=titulo, defaults={"year": anio, "chapters": caps})
            if nuevo:
                self._final(m, True, otaku.Genre)
            if m.manga_type_id is None:
                m.manga_type, m.status = manga_t, pub
                m.save(update_fields=["manga_type", "status"])
            m.demographics.add(shounen)
            m.serializations.add(cat(Company, revista))
            otaku.MangaAuthor.objects.get_or_create(manga=m, person=persona(autor_n), defaults={"role": autor})
            return m

        for (titulo, jp, en, temporada, fuente, estudio, productora, lic, dir_n, guion_n, mus_n, canciones, manga) in ANIMES_FULL:
            a = otaku.Anime.objects.filter(title=titulo).first()
            if a is None:
                continue
            cambios = {"anime_type": tv, "status": fin, "source": cat(otaku.Source, fuente), "season": temporada.upper(),
                       "rating": r17, "title_jap": jp, "title_eng": en}
            for k, v in cambios.items():
                setattr(a, k, v)
            a.save(update_fields=list(cambios))
            a.studios.add(cat(Company, estudio)); a.producers.add(cat(Company, productora)); a.licensors.add(cat(Company, lic))
            a.demographics.add(shounen)
            for idioma, t in ((jap, jp), (eng, en)):
                otaku.AnimeTitle.objects.get_or_create(anime=a, title_lang=idioma, title=t)
            for r, n in ((director, dir_n), (guion, guion_n), (musica, mus_n)):
                otaku.AnimeStaff.objects.get_or_create(anime=a, person=persona(n), defaults={"role": r})
            for clase, n, cancion, artista in canciones:
                art = Artist.objects.get_or_create(name=artista)[0]
                c = otaku.AnimeSong.objects.get_or_create(anime=a, type=tipo_cancion[clase], song_id=n, title=cancion)[0]
                c.artists.add(art)
            m = manga_de(*manga)
            relacion("anime", a, "manga", m, adapt)
            relacion("manga", m, "anime", a, adapt)

        for pj, (jp_n, en_n) in VOCES.items():
            ch = otaku.Character.objects.filter(full_name=pj).first()
            if ch is None:
                continue
            otaku.CharacterVoice.objects.get_or_create(person=persona(jp_n), character=ch, language=jap)
            otaku.CharacterVoice.objects.get_or_create(person=persona(en_n), character=ch, language=eng)

        for titulo, (autor_n, revista) in MANGAS_FULL.items():
            m = otaku.Manga.objects.filter(title=titulo).first()
            if m is not None:
                manga_de(titulo, m.year, m.chapters, autor_n, revista)

        # Secuela / precuela entre animes: Shingeki no Kyojin → Season 2 (nuevo, sin portada propia)
        snk = otaku.Anime.objects.filter(title="Shingeki no Kyojin").first()
        if snk is not None:
            s2, nuevo = otaku.Anime.objects.get_or_create(title="Shingeki no Kyojin Season 2",
                                                          defaults={"year": 2017, "episodes": 12, "anime_type": tv, "status": fin,
                                                                    "synopsis": "Eren y sus compañeros descubren titanes entre los muros."})
            if nuevo:
                self._final(s2, True, otaku.Genre)
            relacion("anime", snk, "anime", s2, sequel)
            relacion("anime", s2, "anime", snk, prequel)
        self.stdout.write("  otaku: fichas completas (tipo, industria, títulos, equipo, voces, banda sonora, autores, relaciones)")

    def _enriquecer(self):
        """Tipo, clasificación, productoras y distribuidoras en series/películas
        (si el catálogo los tiene), para que la ficha muestre la info completa."""
        for obj in serie.Serie.objects.all():
            cambios = []
            if obj.serie_type_id is None and serie.Type.objects.exists():
                obj.serie_type = serie.Type.objects.order_by("?").first()
                cambios.append("serie_type")
            if obj.serie_rating_id is None and serie.Rating.objects.exists():
                obj.serie_rating = serie.Rating.objects.order_by("?").first()
                cambios.append("serie_rating")
            if cambios:
                obj.save(update_fields=cambios)
            if not obj.producers.exists() and Company.objects.exists():
                obj.producers.set(Company.objects.order_by("?")[:2])
            if not obj.distributors.exists() and Company.objects.exists():
                obj.distributors.set(Company.objects.order_by("?")[:1])
        for obj in movie.Movie.objects.all():
            cambios = []
            if obj.movie_type_id is None and movie.Type.objects.exists():
                obj.movie_type = movie.Type.objects.order_by("?").first()
                cambios.append("movie_type")
            if obj.movie_rating_id is None and movie.Rating.objects.exists():
                obj.movie_rating = movie.Rating.objects.order_by("?").first()
                cambios.append("movie_rating")
            if cambios:
                obj.save(update_fields=cambios)
            if not obj.producers.exists() and Company.objects.exists():
                obj.producers.set(Company.objects.order_by("?")[:2])
            if not obj.distributors.exists() and Company.objects.exists():
                obj.distributors.set(Company.objects.order_by("?")[:1])

    def _creadores_de_juegos(self):
        """Creadores demo + 1-2 developers y 1 editora por juego (front cruzado)."""
        import random
        nombres = ["Team Salvato", "Four Leaf Studios", "07th Expansion",
                   "Key", "Nitroplus", "Winter Wolves"]
        editoras = ["Sekai Project", "MangaGamer"]
        creadores = [games.Creator.objects.get_or_create(name=n)[0] for n in nombres]
        pubs = [games.Creator.objects.get_or_create(name=n)[0] for n in editoras]
        through = games.Game.developers.through
        filas = []
        sin = games.Game.objects.filter(developers__isnull=True).values_list("pk", flat=True)
        for pk in sin:
            for c in random.sample(creadores, random.randint(1, 2)):
                filas.append(through(game_id=pk, creator_id=c.pk))
        through.objects.bulk_create(filas, ignore_conflicts=True, batch_size=2000)
        through_pub = games.Game.publishers.through
        filas = [through_pub(game_id=pk, creator_id=random.choice(pubs).pk)
                 for pk in games.Game.objects.filter(publishers__isnull=True).values_list("pk", flat=True)]
        through_pub.objects.bulk_create(filas, ignore_conflicts=True, batch_size=2000)
        self.stdout.write(f"  juegos con creador: {games.Game.objects.filter(developers__isnull=False).distinct().count()}"
                          f" | con editora: {games.Game.objects.filter(publishers__isnull=False).distinct().count()}")

    # --------------------- biblioteca masiva (colección) ---------------------
    def _biblioteca(self, n):
        """Genera N títulos por medio (películas, series, animes, mangas, juegos)
        y añade TODO a la colección del primer superusuario con estado/nota/
        favorito variados. MASIVO-friendly: las portadas se asignan REUSANDO
        rutas de imagen ya existentes (sin copiar archivos) y los géneros y la
        colección van por bulk_create. Idempotente."""
        import random
        from django.contrib.auth import get_user_model

        user = get_user_model().objects.filter(is_superuser=True).order_by("pk").first()
        if user is None:
            self.stdout.write(self.style.WARNING("Sin superusuario: no hay a quién llenarle la biblioteca."))
            return

        adjs = ["Perdido", "Eterno", "Carmesí", "Silente", "Errante", "Roto",
                "Lunar", "Salvaje", "Olvidado", "Radiante", "Umbrío", "Dorado",
                "Febril", "Austral", "Ígneo", "Bruma", "Cripta", "Vórtice",
                "Zafiro", "Errátil"]
        base_por_medio = {"pelicula": "Reino", "serie": "Círculo", "anime": "Sello",
                          "manga": "Trazo", "juego": "Laberinto"}

        def titulos(medio):
            base = base_por_medio[medio]
            for i in range(n):
                yield f"{base} {adjs[i % len(adjs)]} {i // len(adjs) + 1}", 1980 + (i % 45)

        def crear(Model, medio, defaults_por_anio, campo_img="image"):
            """Crea los títulos que falten, asignando portada por NOMBRE de
            archivo ya existente (sin copiar). Devuelve el modelo listo."""
            existentes = set(Model.objects.values_list("title", flat=True))
            nombres_img = list(Model.objects.exclude(**{campo_img: ""})
                               .values_list(campo_img, flat=True)[:200])
            creados = 0
            for i, (t, year) in enumerate(titulos(medio)):
                if t in existentes:
                    continue
                obj = Model(title=t, **defaults_por_anio(year))
                if nombres_img:
                    setattr(obj, campo_img, nombres_img[i % len(nombres_img)])
                obj.save()   # save() genera slug (y mal_id/p_mal_id donde aplique)
                creados += 1
            # géneros: 2 por título nuevo, por BULK sobre la tabla through
            try:
                gfield = Model._meta.get_field("genres")
                Genre = gfield.related_model
                generos = list(Genre.objects.filter(is_active=True).values_list("pk", flat=True))
                if generos:
                    through = getattr(Model, "genres").through
                    fk_self = through._meta.get_fields()
                    sin_genero = Model.objects.filter(genres__isnull=True).values_list("pk", flat=True)
                    filas = []
                    campo_obj = [f.name for f in through._meta.fields
                                 if getattr(f, "related_model", None) is Model][0]
                    campo_gen = [f.name for f in through._meta.fields
                                 if getattr(f, "related_model", None) is Genre][0]
                    for pk in sin_genero:
                        for g in random.sample(generos, min(2, len(generos))):
                            filas.append(through(**{f"{campo_obj}_id": pk, f"{campo_gen}_id": g}))
                    through.objects.bulk_create(filas, ignore_conflicts=True, batch_size=2000)
            except Exception:
                pass
            self.stdout.write(f"  {Model.__name__}: +{creados} nuevos "
                              f"(total {Model.objects.count()})")

        crear(movie.Movie, "pelicula",
              lambda y: {"release_year": y, "synopsis": "Título demo de biblioteca."})
        crear(serie.Serie, "serie",
              lambda y: {"release_year": y, "synopsis": "Título demo de biblioteca."})
        crear(otaku.Anime, "anime",
              lambda y: {"year": y, "episodes": 12 + (y % 14), "synopsis": "Título demo de biblioteca."})
        crear(otaku.Manga, "manga",
              lambda y: {"year": y, "chapters": 20 + (y % 80), "synopsis": "Título demo de biblioteca."})
        crear(games.Game, "juego",
              lambda y: {"release_date": f"{y}-06-01", "synopsis": "Título demo de biblioteca."})

        self._coleccion_catalogo()

    # --------------------- la colección del superusuario ---------------------
    def _coleccion_catalogo(self):
        """TODO el catálogo (películas, series, animes, mangas, juegos) a la colección
        del primer superusuario con estado, nota y favorito variados, y unos cuantos
        personajes y personas en su colección como favoritos. Bulk e idempotente: lo que ya está, se queda."""
        import random
        from django.contrib.auth import get_user_model
        from apps.collections.models import CharacterCollection, ModelBaseCollection, PersonCollection
        from apps.people.models import Person

        user = get_user_model().objects.filter(is_superuser=True).order_by("pk").first()
        if user is None:
            self.stdout.write(self.style.WARNING("Sin superusuario: no hay a quién llenarle la colección."))
            return
        agregados = 0
        for Model in (movie.Movie, serie.Serie, otaku.Anime, otaku.Manga, games.Game):
            tabla = ModelBaseCollection.de_contenido(Model)
            opciones = [k for k, _e in tabla.estados()]      # claves del choice del medio
            ya = set(tabla.objects.filter(user=user).values_list("content_id", flat=True))
            filas = []
            for pk in Model.objects.values_list("pk", flat=True):
                if pk in ya:
                    continue
                filas.append(tabla(
                    user=user, content_id=pk,
                    status=random.choice(opciones) if opciones else "",
                    score=random.randint(1, 10) if random.random() < 0.7 else None,
                    is_favorite=random.random() < 0.15,
                ))
            tabla.objects.bulk_create(filas, ignore_conflicts=True, batch_size=2000)
            agregados += len(filas)
        # personajes y personas: 1 de cada 3 a la colección, como favoritos
        favs = 0
        for Model, Fav in ((otaku.Character, CharacterCollection), (Person, PersonCollection)):
            pks = list(Model.objects.order_by("pk").values_list("pk", flat=True))[::3]
            filas = [Fav(user=user, content_id=pk, is_favorite=True) for pk in pks]
            Fav.objects.bulk_create(filas, ignore_conflicts=True, batch_size=2000)
            favs += len(filas)
        self.stdout.write(self.style.SUCCESS(
            f"Colección de «{user.username}»: {agregados} títulos añadidos · {favs} favoritos."))

    # ------------------------- modo masivo (estrés) -------------------------
    REPARTO_MASIVO = 30
    EQUIPO_MASIVO = 20
    FOTOS_MASIVO = 100

    def _personas_y_artistas_con_filtros(self):
        """Datos para PROBAR LOS FILTROS del panel: personas con país, fecha de nacimiento y
        apodos, y artistas con tipo, géneros y año de inicio. Idempotente (get_or_create)."""
        import datetime
        from apps.catalogs.models import Country
        from apps.music.models import Artist, ArtistType, Genre as MusicGenre
        from apps.people.models import Person, PersonNickname
        pais = {c.code: c for c in Country.objects.filter(code__in=["CHL", "JPN", "USA", "ESP", "GBR", "MEX", "ARG", "DEU", "FRA", "KOR"])}
        PERSONAS = [  # (nombre, ISO país, nacimiento, apodos)
            ("Bill Murray", "USA", "1950-09-21", ["Will"]), ("Hayao Miyazaki", "JPN", "1941-01-05", []),
            ("Pedro Pascal", "CHL", "1975-04-02", ["Pedrito"]), ("Penélope Cruz", "ESP", "1974-04-28", ["Pe"]),
            ("Emma Thompson", "GBR", "1959-04-15", []), ("Gael García Bernal", "MEX", "1978-11-30", []),
            ("Ricardo Darín", "ARG", "1957-01-16", []), ("Diane Kruger", "DEU", "1976-07-15", []),
            ("Marion Cotillard", "FRA", "1975-09-30", []), ("Song Kang-ho", "KOR", "1967-01-17", []),
            ("Ana de Armas", "ESP", "1988-04-30", ["Anita"]), ("Makoto Shinkai", "JPN", "1973-02-09", []),
            ("Keanu Reeves", "USA", "1964-09-02", ["Neo"]), ("Tilda Swinton", "GBR", "1960-11-05", []),
            ("Alfonso Cuarón", "MEX", "1961-11-28", []), ("Norma Aleandro", "ARG", "1936-05-02", []),
            ("Christoph Waltz", "DEU", "1956-10-04", []), ("Léa Seydoux", "FRA", "1985-07-01", []),
            ("Bong Joon-ho", "KOR", "1969-09-14", []), ("Daniela Vega", "CHL", "1989-06-03", []),
            ("Satoshi Kon", "JPN", "1963-10-12", []), ("Zendaya", "USA", "1996-09-01", ["Z"]),
            ("Javier Bardem", "ESP", "1969-03-01", []), ("Florence Pugh", "GBR", "1996-01-03", ["Flo"]),
        ]
        for nombre, iso, nac, apodos in PERSONAS:
            per, _ = Person.objects.get_or_create(full_name=nombre)
            per.country = pais.get(iso, per.country); per.birth_date = datetime.date.fromisoformat(nac); per.save()
            for a in apodos:
                PersonNickname.objects.get_or_create(person=per, nickname=a)
        tipo = {t.name: t for t in ArtistType.objects.filter(name__in=["Artist", "Band"])}
        gen = {g.name: g for g in MusicGenre.objects.filter(name__in=["Rock", "Pop", "Jazz", "Metal", "Electronic", "Hip Hop", "Folk", "Blues"])}
        ARTISTAS = [  # (nombre, tipo, [géneros], año de inicio)
            ("Radiohead", "Band", ["Rock", "Electronic"], 1985), ("Björk", "Artist", ["Pop", "Electronic"], 1977),
            ("Miles Davis", "Artist", ["Jazz"], 1944), ("Metallica", "Band", ["Metal", "Rock"], 1981),
            ("Daft Punk", "Band", ["Electronic"], 1993), ("Kendrick Lamar", "Artist", ["Hip Hop"], 2003),
            ("Joni Mitchell", "Artist", ["Folk", "Jazz"], 1964), ("B.B. King", "Artist", ["Blues"], 1949),
            ("Los Jaivas", "Band", ["Rock", "Folk"], 1963), ("Mon Laferte", "Artist", ["Pop", "Rock"], 2003),
            ("Nina Simone", "Artist", ["Jazz", "Blues"], 1954), ("Portishead", "Band", ["Electronic", "Rock"], 1991),
        ]
        for nombre, t, generos, anio in ARTISTAS:
            art, _ = Artist.objects.get_or_create(name=nombre)
            art.artist_type = tipo.get(t, art.artist_type); art.start_year = anio; art.save()
            art.genres.add(*[gen[g] for g in generos if g in gen])
        self.stdout.write(f"Personas y artistas con datos para filtros: {len(PERSONAS)} / {len(ARTISTAS)}")

    def _masivo(self):
        """Rellena cada serie/película hasta 30 reparto, 20 equipo y 100 fotos
        extra, para ver el comportamiento de la ficha con volumen. Idempotente."""
        from apps.people.models import Person
        nombres_pila = ["Ana", "Bruno", "Carla", "Diego", "Elena", "Fabián", "Gema",
                        "Hugo", "Irene", "Javier"]
        apellidos = ["Aravena", "Bustos", "Cáceres", "Durán", "Escobar",
                     "Fuentes", "Garrido", "Herrera", "Ibáñez", "Jara"]
        personas = []
        for ap in apellidos:
            for n in nombres_pila:
                if len(personas) >= self.REPARTO_MASIVO + self.EQUIPO_MASIVO:
                    break
                p, _ = Person.objects.get_or_create(full_name=f"{n} {ap}")
                self._foto(p)
                personas.append(p)
        actores = personas[:self.REPARTO_MASIVO]
        tecnicos = personas[self.REPARTO_MASIVO:]

        titulos = list(serie.Serie.objects.all()) + list(movie.Movie.objects.all())
        for obj in titulos:
            for i, per in enumerate(actores[:max(0, self.REPARTO_MASIVO - obj.cast.count())]):
                obj.cast.get_or_create(person=per, role=None,
                                       character_name=f"Personaje masivo {i + 1}")
            for per in tecnicos[:max(0, self.EQUIPO_MASIVO - obj.staff.count())]:
                obj.staff.get_or_create(person=per, role=None)
            faltan = self.FOTOS_MASIVO - obj.images.count()
            fk = obj.images.field.name
            for n in range(max(0, faltan)):
                extra = obj.images.model(**{fk: obj})
                with self._next_img().open("rb") as fh:
                    extra.image.save(f"{obj.slug or obj.pk}-masivo-{n}.jpg", File(fh), save=True)
            self.stdout.write(f"  {obj}: reparto={obj.cast.count()} equipo={obj.staff.count()} "
                              f"fotos={obj.images.count()}")

    def _personas_y_reparto(self):
        """Personas con foto + reparto (3) y equipo (2) por serie/película, para
        ver las secciones de la ficha pública. Idempotente."""
        from apps.people.models import Person
        nombres = ["Bryan Cranston", "Louis Hofmann", "Adam Scott", "Jeremy Allen White",
                   "Hiroyuki Sanada", "Anna Gunn", "Rebecca Ferguson", "Song Kang-ho"]
        personas = []
        for n in nombres:
            p, _ = Person.objects.get_or_create(full_name=n)
            self._foto(p)
            personas.append(p)
        for obj in list(serie.Serie.objects.all()) + list(movie.Movie.objects.all()):
            if not obj.cast.exists():
                for i, per in enumerate(personas[:3]):
                    obj.cast.get_or_create(person=per, role=None,
                                           character_name=f"Personaje {i + 1}")
            if not obj.staff.exists():
                for per in personas[3:5]:
                    obj.staff.get_or_create(person=per, role=None)

    def _personajes(self):
        """Personajes reales por anime/manga, con imagen, rol y actor de voz —
        alimentan el front de personajes y el cruce personaje ⇄ voz ⇄ persona.
        Idempotente."""
        from apps.catalogs.models import Language
        from apps.people.models import Person

        ANIME_CH = {
            "Fullmetal Alchemist: Brotherhood": [("Edward Elric", "Principal"), ("Alphonse Elric", "Principal"), ("Roy Mustang", "Secundario")],
            "Shingeki no Kyojin": [("Eren Yeager", "Principal"), ("Mikasa Ackerman", "Principal"), ("Levi", "Secundario")],
            "Sousou no Frieren": [("Frieren", "Principal"), ("Fern", "Principal")],
            "Death Note": [("Light Yagami", "Principal"), ("L", "Principal"), ("Misa Amane", "Secundario")],
            "One Punch Man": [("Saitama", "Principal"), ("Genos", "Secundario")],
        }
        MANGA_CH = {
            "Berserk": [("Guts", "Principal"), ("Griffith", "Secundario")],
            "One Piece": [("Monkey D. Luffy", "Principal"), ("Roronoa Zoro", "Secundario"), ("Nami", "Secundario")],
            "Monster": [("Kenzo Tenma", "Principal"), ("Johan Liebert", "Secundario")],
            "Vagabond": [("Miyamoto Musashi", "Principal")],
            "Chainsaw Man": [("Denji", "Principal"), ("Power", "Secundario"), ("Makima", "Secundario")],
        }
        VOCES = {  # personaje → seiyū (japonés)
            "Saitama": "Makoto Furukawa", "Light Yagami": "Mamoru Miyano",
            "L": "Kappei Yamaguchi", "Edward Elric": "Romi Park",
            "Eren Yeager": "Yuki Kaji", "Frieren": "Atsumi Tanezaki",
        }

        roles = {}

        def rol(nombre):
            if nombre not in roles:
                roles[nombre] = otaku.Role.objects.get_or_create(name=nombre)[0]
            return roles[nombre]

        def personaje(nombre):
            ch, _ = otaku.Character.objects.get_or_create(full_name=nombre)
            if not ch.images.exists() and self.imgs:
                img = otaku.CharacterImage(character=ch)
                with self._next_img().open("rb") as fh:
                    img.image.save(f"{ch.slug or ch.pk}.jpg", File(fh), save=True)
            return ch

        for titulo, lista in ANIME_CH.items():
            a = otaku.Anime.objects.filter(title=titulo).first()
            if a is None:
                continue
            for nombre, r in lista:
                otaku.AnimeCharacter.objects.get_or_create(
                    anime=a, character=personaje(nombre), defaults={"role": rol(r)})
        for titulo, lista in MANGA_CH.items():
            m = otaku.Manga.objects.filter(title=titulo).first()
            if m is None:
                continue
            for nombre, r in lista:
                otaku.MangaCharacter.objects.get_or_create(
                    manga=m, character=personaje(nombre), defaults={"role": rol(r)})

        jap = Language.objects.get_or_create(name="Japonés")[0]
        for pj, actor in VOCES.items():
            ch = otaku.Character.objects.filter(full_name=pj).first()
            if ch is None:
                continue
            p, _ = Person.objects.get_or_create(full_name=actor)
            self._foto(p)
            otaku.CharacterVoice.objects.get_or_create(person=p, character=ch, language=jap)

    def _repartos_masivos(self):
        """Repartos ENORMES en todos los medios (bulk, idempotente-ish):
        pool de 200 personas y 300 personajes (imágenes REUSANDO rutas ya
        existentes, sin copiar archivos); 30 reparto + 20 equipo por película
        y serie, 20 staff + 12 personajes por anime, 4 autores + 8 personajes
        por manga, y una voz por personaje."""
        import random
        from apps.catalogs.models import Language
        from apps.people.models import Person

        # --- pool de PERSONAS (reusa rutas de foto existentes) ---
        from apps.people.models import PersonImage
        fotos = list(PersonImage.objects.exclude(image="").values_list("image", flat=True)[:50])
        base = Person.objects.count()
        nuevos = [Person(full_name=f"Intérprete Errante {base + i + 1}", slug=f"interprete-errante-{base + i + 1}")
                  for i in range(max(0, 200 - base))]
        Person.objects.bulk_create(nuevos, batch_size=500)
        if fotos:   # la foto vive en PersonImage (bulk_create no pasa por save(): el orden va a mano)
            creados = Person.objects.filter(slug__startswith="interprete-errante-", images__isnull=True)
            PersonImage.objects.bulk_create([PersonImage(person=p, order=0, image=fotos[i % len(fotos)], image_downloaded=True)
                                             for i, p in enumerate(creados)], batch_size=500)
        personas = list(Person.objects.filter(is_active=True).values_list("pk", flat=True))

        # --- pool de PERSONAJES (reusa rutas de imagen existentes) ---
        imgs_pj = list(otaku.CharacterImage.objects.values_list("image", flat=True)[:30])
        base = otaku.Character.objects.count()
        # bulk_create no pasa por save(): mal_id y p_mal_id (únicos) van a mano.
        nuevos = [otaku.Character(full_name=f"Rostro Errante {base + i + 1}",
                                  slug=f"rostro-errante-{base + i + 1}",
                                  mal_id=-(900000 + base + i),
                                  p_mal_id=f"C{-(900000 + base + i)}")
                  for i in range(max(0, 300 - base))]
        otaku.Character.objects.bulk_create(nuevos, batch_size=500)
        if imgs_pj:
            sin_img = otaku.Character.objects.filter(images__isnull=True)
            otaku.CharacterImage.objects.bulk_create(
                [otaku.CharacterImage(character=ch, order=0,
                                      image=imgs_pj[i % len(imgs_pj)])
                 for i, ch in enumerate(sin_img)], batch_size=500)
        personajes = list(otaku.Character.objects.values_list("pk", flat=True))

        def roles(modelo, nombres):
            return [modelo.objects.get_or_create(name=n)[0].pk for n in nombres]

        EQUIPO = ["Dirección", "Guion", "Producción", "Fotografía", "Música", "Edición"]

        def llena(through, fk_obra, obra_qs, pks, cuantos, extra):
            """`cuantos` filas por obra con personas/personajes SIN repetir."""
            existentes = set(through.objects.values_list(f"{fk_obra}_id", "person_id")
                             if "person_id" in [f.attname for f in through._meta.fields]
                             else through.objects.values_list(f"{fk_obra}_id", "character_id"))
            campo_quien = ("person_id" if "person_id" in
                           [f.attname for f in through._meta.fields] else "character_id")
            filas = []
            for pk in obra_qs.values_list("pk", flat=True):
                for quien in random.sample(pks, cuantos):
                    if (pk, quien) in existentes:
                        continue
                    filas.append(through(**{f"{fk_obra}_id": pk, campo_quien: quien},
                                         **extra(quien)))
            through.objects.bulk_create(filas, ignore_conflicts=True, batch_size=2000)
            return len(filas)

        t = 0
        for app, Obra, Cast, Staff, fk in (
                (movie, movie.Movie, movie.MovieCast, movie.MovieStaff, "movie"),
                (serie, serie.Serie, serie.SerieCast, serie.SerieStaff, "serie")):
            rls = roles(app.Role, EQUIPO)
            t += llena(Cast, fk, Obra.objects.all(), personas, 30,
                       lambda q: {"character_name": f"Personaje {random.randint(1, 99)}"})
            t += llena(Staff, fk, Obra.objects.all(), personas, 20,
                       lambda q, rls=rls: {"role_id": random.choice(rls)})

        rls_anime = roles(otaku.Role, ["Director", "Guion", "Diseño de personajes", "Música", "Animación"])
        t += llena(otaku.AnimeStaff, "anime", otaku.Anime.objects.all(), personas, 20,
                   lambda q: {"role_id": random.choice(rls_anime)})
        rls_pj = roles(otaku.Role, ["Principal", "Secundario"])
        t += llena(otaku.AnimeCharacter, "anime", otaku.Anime.objects.all(), personajes, 12,
                   lambda q: {"role_id": random.choice(rls_pj)})
        rls_autor = roles(otaku.Role, ["Historia", "Arte"])
        t += llena(otaku.MangaAuthor, "manga", otaku.Manga.objects.all(), personas, 4,
                   lambda q: {"role_id": random.choice(rls_autor)})
        t += llena(otaku.MangaCharacter, "manga", otaku.Manga.objects.all(), personajes, 8,
                   lambda q: {"role_id": random.choice(rls_pj)})

        # una VOZ por personaje (cruce personaje ⇄ persona)
        jap = Language.objects.get_or_create(name="Japonés")[0]
        con_voz = set(otaku.CharacterVoice.objects.values_list("character_id", flat=True))
        filas = [otaku.CharacterVoice(character_id=ch, person_id=random.choice(personas),
                                      language=jap)
                 for ch in personajes if ch not in con_voz]
        otaku.CharacterVoice.objects.bulk_create(filas, ignore_conflicts=True, batch_size=2000)
        self.stdout.write(f"  repartos: {t} filas de reparto/equipo/personajes · {len(filas)} voces")

    def _coleccion_musica(self):
        """Álbumes, artistas y canciones a la colección del admin, con ~1 de
        cada 3 como favorito — alimenta las filas «Favoritos» del home de
        música. Idempotente (bulk + ignore_conflicts)."""
        from django.contrib.auth import get_user_model
        from apps.collections.models import ModelBaseCollection
        from apps.music.models import Album, Artist, Song

        user = get_user_model().objects.filter(is_superuser=True).order_by("pk").first()
        if user is None:
            return
        for modelo, tope in ((Album, None), (Artist, None), (Song, 120)):
            tabla = ModelBaseCollection.de_contenido(modelo)
            pks = modelo.objects.filter(is_active=True).values_list("pk", flat=True)
            filas = [tabla(user=user, content_id=pk, is_favorite=(i % 3 == 0))
                     for i, pk in enumerate(pks[:tope] if tope else pks)]
            tabla.objects.bulk_create(filas, ignore_conflicts=True, batch_size=2000)

    def _industria(self, n):
        """N compañías por modelo, repartidas entre los títulos (masivo, bulk).
        Película/serie: productoras Y distribuidoras (cada medio con su Company);
        anime: estudio + productoras + licenciataria; manga: revista de
        serialización. Idempotente: solo crea lo que falta y solo asigna a
        títulos sin esa relación."""
        import random
        from django.utils.text import slugify

        def crea(modelo, prefijo):
            base = modelo.objects.count()
            filas = [modelo(name=f"{prefijo} {base + i + 1}",
                            slug=slugify(f"{prefijo} {base + i + 1}"),
                            founded_year=random.randint(1950, 2020))
                     for i in range(max(0, n - base))]
            modelo.objects.bulk_create(filas, batch_size=1000)
            return list(modelo.objects.values_list("pk", flat=True))

        def reparte(Media, campo, pks, k=(1, 1)):
            """1..k compañías del pool a cada título SIN ninguna en ese campo."""
            campo_obj = Media._meta.get_field(campo)
            through = campo_obj.remote_field.through
            fk_media = campo_obj.m2m_field_name()
            fk_comp = campo_obj.m2m_reverse_field_name()
            sin = Media.objects.filter(**{f"{campo}__isnull": True}).values_list("pk", flat=True)
            filas = []
            for pk in sin:
                for cpk in random.sample(pks, random.randint(k[0], k[1])):
                    filas.append(through(**{f"{fk_media}_id": pk, f"{fk_comp}_id": cpk}))
            through.objects.bulk_create(filas, ignore_conflicts=True, batch_size=2000)
            return len(filas)

        cine = crea(Company, "Cine Austral")
        tv = crea(Company, "TV Andina")
        est = crea(Company, "Estudio Sakura")
        pro = crea(Company, "Comité Aozora")
        lic = crea(Company, "Licencias Fénix")
        rev = crea(Company, "Revista Hoshi")

        t = 0
        t += reparte(movie.Movie, "producers", cine, (1, 2))
        t += reparte(movie.Movie, "distributors", cine, (1, 1))
        t += reparte(serie.Serie, "producers", tv, (1, 2))
        t += reparte(serie.Serie, "distributors", tv, (1, 1))
        t += reparte(otaku.Anime, "studios", est, (1, 1))
        t += reparte(otaku.Anime, "producers", pro, (1, 2))
        t += reparte(otaku.Anime, "licensors", lic, (1, 1))
        t += reparte(otaku.Manga, "serializations", rev, (1, 1))
        self.stdout.write(f"  industria: {n} compañías por modelo · {t} vínculos nuevos")

    def _final(self, obj, new, GenreModel):
        """Portada + géneros + 4 imágenes (la primera es la portada; el resto, la galería de la ficha pública)."""
        if new and hasattr(obj, "genres") and GenreModel.objects.exists():
            obj.genres.set(GenreModel.objects.order_by("?")[:2])
        if not obj.image and self.imgs:
            with self._next_img().open("rb") as fh:
                obj.image.save(f"{obj.slug or obj.pk}.jpg", File(fh), save=True)
        # XxxImage = sus imágenes: la primera es la portada, las demás la galería de la ficha
        if hasattr(obj, "images") and not obj.images.exists() and self.imgs:
            fk = obj.images.field.name   # serie/movie/anime/manga/game/album
            for n in range(4):
                fila = obj.images.model(**{fk: obj})
                with self._next_img().open("rb") as fh:
                    fila.image.save(f"{obj.slug or obj.pk}-img-{n}.jpg", File(fh), save=True)
        return 1 if new else 0

    def _foto(self, p):
        """Foto de una persona del seed: fila PersonImage (la primera es su portada)."""
        from apps.people.models import PersonImage
        if not self.imgs or p.images.exists():
            return
        fila = PersonImage(person=p, image_downloaded=True)
        with self._next_img().open("rb") as fh:
            fila.image.save(f"{p.slug or p.pk}.jpg", File(fh), save=True)

    def _next_img(self):
        src = self.imgs[self.idx % len(self.imgs)]
        self.idx += 1
        return src

    def _limpiar(self):
        """Borra la PAJA demo dejando el catálogo intacto: oyentes (y sus
        colecciones y me-gusta, por cascada), la banda de estrés Orquesta
        Errante, las traducciones lorem y el hilo de contacto de prueba."""
        from django.contrib.auth import get_user_model
        from apps.mailing.models import ContactMessage
        from apps.music.models import Artist, SongTranslation

        User = get_user_model()
        n_oyentes, _ = User.objects.filter(username__startswith="oyente").delete()
        n_trad, _ = SongTranslation.objects.all().delete()
        n_banda, _ = Artist.objects.filter(name="Orquesta Errante").delete()
        n_hilo, _ = ContactMessage.objects.filter(
            subject="¿Cuándo agregan más álbumes?").delete()
        self.stdout.write(self.style.SUCCESS(
            f"Limpieza demo: {n_oyentes} filas de oyentes (con sus colecciones), "
            f"{n_trad} traducciones, {n_banda} de la Orquesta Errante y "
            f"{n_hilo} del hilo de contacto."))
