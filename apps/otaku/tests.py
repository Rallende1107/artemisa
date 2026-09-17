"""Tests de humo de la app `otaku`: rutas del panel, listas «by» (404 con tipo inválido) y rutas públicas.

Correr solo esta app:  docker compose exec web python manage.py test_changed --app otaku
"""
from core.shared import testing


class OtakuSmokeTests(testing.AppSmokeTestCase):
    app_label = "otaku"
    public_namespace = "otaku"

    # ---- temporada calculada por la fecha «desde» (ene-mar invierno · abr-jun primavera · jul-sep verano · oct-dic otoño)
    CASOS = ((1, "WINTER"), (3, "WINTER"), (4, "SPRING"), (6, "SPRING"), (7, "SUMMER"), (9, "SUMMER"), (10, "FALL"), (12, "FALL"))

    def test_season_por_script(self):
        """Alta por ORM (importadores): sin temporada, se calcula de from_date; con temporada dada, se respeta."""
        from datetime import date
        from apps.otaku.models import Anime, Manga
        for mes, esperada in self.CASOS:
            with self.subTest(mes=mes):
                a = Anime.objects.create(title=f"Anime mes {mes}", from_date=date(2020, mes, 15))
                m = Manga.objects.create(title=f"Manga mes {mes}", from_date=date(2020, mes, 15))
                self.assertEqual((a.season, m.season, a.year), (esperada, esperada, 2020))
        fija = Anime.objects.create(title="Anime con temporada dada", from_date=date(2020, 1, 1), season="FALL")
        self.assertEqual(fija.season, "FALL")
        self.assertEqual(Anime.objects.create(title="Sin fecha").season, "")

    def test_season_por_formulario(self):
        """Alta por el panel (front): el formulario deja la temporada vacía y el modelo la calcula al guardar."""
        from apps.otaku.forms import AnimeForm, MangaForm
        for Form in (AnimeForm, MangaForm):
            for mes, esperada in self.CASOS:
                with self.subTest(form=Form.__name__, mes=mes):
                    form = Form(data={"title": f"{Form.__name__} {mes}", "from_date": f"2021-{mes:02d}-10", "season": "", "rating": "", "year": "", "is_active": "on"})
                    self.assertTrue(form.is_valid(), form.errors.as_text())
                    self.assertEqual(form.save().season, esperada)
