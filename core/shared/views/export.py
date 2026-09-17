"""EXPORTAR una tabla Data a nuestro propio DUMP (json · json.gz): el respaldo alternativo al de la base.

Se puede tener el respaldo de Postgres o este dump, y recargarlo por el formulario del panel o por consola.
Lo que sale es EXACTAMENTE lo que se guardó al descargar (la columna `data` de cada fila, sin tocar), así que
lo exportado vuelve a entrar por el mismo cargador que lee los dumps de origen.

    class DataMalAnimeExportView(BaseDataMalAnime, BaseExportDumpView):
        prefijo = "mal-anime"        # nombre del archivo: mal-anime-<fecha>.json.gz

El archivo se arma por trozos y se envía comprimido: una tabla de 200.000 fichas no se carga entera en memoria.
"""
import gzip
import json
import time

from django.http import StreamingHttpResponse
from django.views.generic import View

from core.shared.views.base import BasePage

TAMANO_LOTE = 500      # filas que se leen de la BD de una vez


class BaseExportDumpView(BasePage, View):
    """GET → descarga el dump de ESTA tabla Data. Solo lee: no cambia nada."""
    staff_only = True
    prefijo = ""           # nombre base del archivo; vacío = el nombre del modelo
    solo_ok = True         # solo las filas cuyo fetch fue bien (data_status=True)

    def nombre_archivo(self):
        base = self.prefijo or self.model._meta.model_name
        return f"{base}-{time.strftime('%Y%m%d-%H%M%S')}.json.gz"

    def filas(self):
        qs = self.model.objects.all()
        if self.solo_ok:
            qs = qs.filter(data_status=True)
        return qs.order_by("pk").iterator(chunk_size=TAMANO_LOTE)

    def trozos(self):
        """El JSON completo, en pedazos y ya comprimido: `[` · fila · `,` · fila · … · `]`."""
        buffer = _BufferGzip()
        yield buffer.escribe("[\n")
        primera = True
        for fila in self.filas():
            if fila.data is None:
                continue
            coma = "" if primera else ",\n"
            primera = False
            trozo = buffer.escribe(coma + json.dumps(fila.data, ensure_ascii=False))
            if trozo:
                yield trozo
        yield buffer.cierra("\n]\n")

    def get(self, request, *args, **kwargs):
        respuesta = StreamingHttpResponse(self.trozos(), content_type="application/gzip")
        respuesta["Content-Disposition"] = f'attachment; filename="{self.nombre_archivo()}"'
        return respuesta


class _BufferGzip:
    """Comprime a trozos: acumula texto y suelta bytes cuando hay bastante."""

    def __init__(self):
        import io
        self.crudo = io.BytesIO()
        self.gz = gzip.GzipFile(fileobj=self.crudo, mode="wb")

    def _sacar(self):
        datos = self.crudo.getvalue()
        if datos:
            self.crudo.seek(0)
            self.crudo.truncate(0)
        return datos

    def escribe(self, texto):
        self.gz.write(texto.encode("utf-8"))
        return self._sacar()

    def cierra(self, texto=""):
        if texto:
            self.gz.write(texto.encode("utf-8"))
        self.gz.close()
        return self._sacar()
