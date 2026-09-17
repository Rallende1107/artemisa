# Formularios sin `.form-row` — checklist de revisión

La REGLA (ver [README §forms](../README.md) y `static/css/components/form.css`):
campos hermanos se agrupan en `<div class="form-row">` — la fila toma TODO el ancho y
se divide en columnas iguales (mínimo 220px c/u; bajo eso se apilan responsivas).
Campos sueltos en el grid base quedan angostos si el form tiene algún `.full`
(textarea/imagen los hace full automáticamente y eso reserva las columnas).

**CONVENCIÓN (decisión René 2026-09-01): TODO campo vive en una `.form-row`.**
- Cortos hermanos → juntos en una row (N campos = N columnas)
- Largos (textarea, archivo, multi-select) → SOLOS en su row (1 campo = fila completa)
El CSS auto-full (`:has(textarea)` etc.) queda como red de seguridad, no como regla.
Variantes: `.form-row-2-1` / `.form-row-1-2` para anchos asimétricos.
Ejemplo ya arreglado: `apps/catalogs/templates/common/form/country.html`.

Generado del barrido del 2026-09-12 — 109 plantillas con campos fuera de una `.form-row` (heurística por líneas; revisar a ojo):

- [ ] `apps/catalogs/templates/catalogs/form/country.html` — 6 sueltos
- [ ] `apps/catalogs/templates/catalogs/form/external_source.html` — 16 sueltos
- [ ] `apps/catalogs/templates/catalogs/form/format.html` — 10 sueltos
- [ ] `apps/catalogs/templates/catalogs/form/image_size.html` — 10 sueltos
- [ ] `apps/catalogs/templates/catalogs/form/language.html` — 7 sueltos
- [ ] `apps/catalogs/templates/catalogs/form/log_level.html` — 12 sueltos
- [ ] `apps/catalogs/templates/catalogs/form/quality.html` — 10 sueltos
- [ ] `apps/catalogs/templates/catalogs/form/relation_type.html` — 10 sueltos
- [ ] `apps/catalogs/templates/catalogs/form/role_type.html` — 10 sueltos
- [ ] `apps/catalogs/templates/catalogs/form/website.html` — 16 sueltos
- [ ] `apps/collections/templates/collections/form/anime_status.html` — 15 sueltos
- [ ] `apps/collections/templates/collections/form/game_status.html` — 15 sueltos
- [ ] `apps/collections/templates/collections/form/manga_status.html` — 15 sueltos
- [ ] `apps/collections/templates/collections/form/movie_status.html` — 15 sueltos
- [ ] `apps/collections/templates/collections/form/music_status.html` — 15 sueltos
- [ ] `apps/collections/templates/collections/form/serie_status.html` — 15 sueltos
- [ ] `apps/games/templates/games/form/creator.html` — 12 sueltos
- [ ] `apps/games/templates/games/form/creator_link.html` — 12 sueltos
- [ ] `apps/games/templates/games/form/creator_nickname.html` — 6 sueltos
- [ ] `apps/games/templates/games/form/creator_type.html` — 10 sueltos
- [ ] `apps/games/templates/games/form/development_engine.html` — 10 sueltos
- [ ] `apps/games/templates/games/form/game.html` — 39 sueltos
- [ ] `apps/games/templates/games/form/game_image.html` — 10 sueltos
- [ ] `apps/games/templates/games/form/game_image_extra.html` — 7 sueltos
- [ ] `apps/games/templates/games/form/game_link.html` — 12 sueltos
- [ ] `apps/games/templates/games/form/game_title.html` — 9 sueltos
- [ ] `apps/games/templates/games/form/genre.html` — 10 sueltos
- [ ] `apps/games/templates/games/form/medium.html` — 10 sueltos
- [ ] `apps/games/templates/games/form/platform.html` — 10 sueltos
- [ ] `apps/games/templates/games/form/status.html` — 10 sueltos
- [ ] `apps/games/templates/games/form/type.html` — 10 sueltos
- [ ] `apps/mailing/templates/mailing/form/email_template.html` — 18 sueltos
- [ ] `apps/movies/templates/movies/form/company.html` — 15 sueltos
- [ ] `apps/movies/templates/movies/form/genre.html` — 10 sueltos
- [ ] `apps/movies/templates/movies/form/movie.html` — 30 sueltos
- [ ] `apps/movies/templates/movies/form/movie_cast.html` — 12 sueltos
- [ ] `apps/movies/templates/movies/form/movie_image.html` — 10 sueltos
- [ ] `apps/movies/templates/movies/form/movie_image_extra.html` — 7 sueltos
- [ ] `apps/movies/templates/movies/form/movie_relation.html` — 9 sueltos
- [ ] `apps/movies/templates/movies/form/movie_staff.html` — 9 sueltos
- [ ] `apps/movies/templates/movies/form/movie_title.html` — 9 sueltos
- [ ] `apps/movies/templates/movies/form/rating.html` — 13 sueltos
- [ ] `apps/movies/templates/movies/form/role.html` — 13 sueltos
- [ ] `apps/movies/templates/movies/form/type.html` — 10 sueltos
- [ ] `apps/music/templates/music/form/album.html` — 18 sueltos
- [ ] `apps/music/templates/music/form/album_image.html` — 10 sueltos
- [ ] `apps/music/templates/music/form/album_image_extra.html` — 7 sueltos
- [ ] `apps/music/templates/music/form/album_type.html` — 10 sueltos
- [ ] `apps/music/templates/music/form/artist.html` — 18 sueltos
- [ ] `apps/music/templates/music/form/artist_image.html` — 10 sueltos
- [ ] `apps/music/templates/music/form/artist_image_extra.html` — 7 sueltos
- [ ] `apps/music/templates/music/form/artist_member.html` — 15 sueltos
- [ ] `apps/music/templates/music/form/artist_type.html` — 10 sueltos
- [ ] `apps/music/templates/music/form/genre.html` — 10 sueltos
- [ ] `apps/music/templates/music/form/role.html` — 13 sueltos
- [ ] `apps/music/templates/music/form/song.html` — 10 sueltos
- [ ] `apps/music/templates/music/form/song.original.html` — 19 sueltos
- [ ] `apps/otaku/templates/otaku/form/anime.html` — 51 sueltos
- [ ] `apps/otaku/templates/otaku/form/anime_character.html` — 9 sueltos
- [ ] `apps/otaku/templates/otaku/form/anime_image.html` — 10 sueltos
- [ ] `apps/otaku/templates/otaku/form/anime_image_extra.html` — 7 sueltos
- [ ] `apps/otaku/templates/otaku/form/anime_song.html` — 21 sueltos
- [ ] `apps/otaku/templates/otaku/form/anime_staff.html` — 9 sueltos
- [ ] `apps/otaku/templates/otaku/form/anime_title.html` — 9 sueltos
- [ ] `apps/otaku/templates/otaku/form/character.html` — 12 sueltos
- [ ] `apps/otaku/templates/otaku/form/character_image.html` — 10 sueltos
- [ ] `apps/otaku/templates/otaku/form/character_image_extra.html` — 7 sueltos
- [ ] `apps/otaku/templates/otaku/form/character_nickname.html` — 6 sueltos
- [ ] `apps/otaku/templates/otaku/form/character_voice.html` — 9 sueltos
- [ ] `apps/otaku/templates/otaku/form/demographic.html` — 10 sueltos
- [ ] `apps/otaku/templates/otaku/form/genre.html` — 10 sueltos
- [ ] `apps/otaku/templates/otaku/form/licensor.html` — 12 sueltos
- [ ] `apps/otaku/templates/otaku/form/manga.html` — 51 sueltos
- [ ] `apps/otaku/templates/otaku/form/manga_author.html` — 9 sueltos
- [ ] `apps/otaku/templates/otaku/form/manga_character.html` — 9 sueltos
- [ ] `apps/otaku/templates/otaku/form/manga_image.html` — 10 sueltos
- [ ] `apps/otaku/templates/otaku/form/manga_image_extra.html` — 7 sueltos
- [ ] `apps/otaku/templates/otaku/form/manga_title.html` — 9 sueltos
- [ ] `apps/otaku/templates/otaku/form/person_mal.html` — 28 sueltos
- [ ] `apps/otaku/templates/otaku/form/producer.html` — 12 sueltos
- [ ] `apps/otaku/templates/otaku/form/rating.html` — 13 sueltos
- [ ] `apps/otaku/templates/otaku/form/relation.html` — 15 sueltos
- [ ] `apps/otaku/templates/otaku/form/role.html` — 13 sueltos
- [ ] `apps/otaku/templates/otaku/form/season.html` — 10 sueltos
- [ ] `apps/otaku/templates/otaku/form/serialization.html` — 12 sueltos
- [ ] `apps/otaku/templates/otaku/form/song_type.html` — 10 sueltos
- [ ] `apps/otaku/templates/otaku/form/source.html` — 10 sueltos
- [ ] `apps/otaku/templates/otaku/form/status.html` — 10 sueltos
- [ ] `apps/otaku/templates/otaku/form/studio.html` — 12 sueltos
- [ ] `apps/otaku/templates/otaku/form/theme.html` — 10 sueltos
- [ ] `apps/otaku/templates/otaku/form/type.html` — 10 sueltos
- [ ] `apps/otaku/templates/otaku/form/year.html` — 3 sueltos
- [ ] `apps/people/templates/people/form/person.html` — 12 sueltos
- [ ] `apps/people/templates/people/form/person_image.html` — 10 sueltos
- [ ] `apps/people/templates/people/form/person_image_extra.html` — 7 sueltos
- [ ] `apps/people/templates/people/form/person_nickname.html` — 6 sueltos
- [ ] `apps/series/templates/series/form/company.html` — 15 sueltos
- [ ] `apps/series/templates/series/form/genre.html` — 10 sueltos
- [ ] `apps/series/templates/series/form/rating.html` — 13 sueltos
- [ ] `apps/series/templates/series/form/role.html` — 13 sueltos
- [ ] `apps/series/templates/series/form/serie.html` — 30 sueltos
- [ ] `apps/series/templates/series/form/serie_cast.html` — 12 sueltos
- [ ] `apps/series/templates/series/form/serie_image.html` — 10 sueltos
- [ ] `apps/series/templates/series/form/serie_image_extra.html` — 7 sueltos
- [ ] `apps/series/templates/series/form/serie_relation.html` — 9 sueltos
- [ ] `apps/series/templates/series/form/serie_staff.html` — 9 sueltos
- [ ] `apps/series/templates/series/form/serie_title.html` — 9 sueltos
- [ ] `apps/series/templates/series/form/type.html` — 10 sueltos
- [ ] `apps/users/templates/users/form/custom_user.html` — 21 sueltos
