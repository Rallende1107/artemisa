"""CURSOR de lote por fuente y tipo (system.ImportCursor).

`siguiente()` dice desde qué id parte el próximo lote; `avanzar()` lo mueve cuando un lote se reparte.
Nunca se calcula desde el mayor id descargado: una importación suelta o el buscador por nombre traen ids
enormes (One Ok Rock es el #4531854 en Deezer) y el beat saltaría de 100 a 4 millones."""


def _fila(source, kind):
    from apps.system.models import ImportCursor
    fila, _ = ImportCursor.objects.get_or_create(source=source, type=kind)
    return fila


def siguiente(source, kind):
    """Próximo id del lote (1 si nunca se lanzó ninguno)."""
    return _fila(source, kind).next_id


def cantidad_de(source, kind, pedida=None):
    """Cuántos trae el lote: la cantidad pedida (tarea programada) o, si no viene, la del cursor."""
    return int(pedida) if pedida else _fila(source, kind).batch_size


def avanzar(source, kind, hasta):
    """El lote cubrió hasta `hasta`: el próximo empieza en `hasta` + 1 (nunca retrocede)."""
    fila = _fila(source, kind)
    if hasta + 1 > fila.next_id:
        fila.next_id = hasta + 1
        fila.save(update_fields=["next_id", "updated_at"])
    return fila.next_id


def avanzar_si_contiguo(source, kind, inicio, fin):
    """Un RANGO manual mueve el cursor solo si continúa desde él (inicio ≤ próximo id ≤ fin): «del 1 al
    5.000» avanza; «del 4531854 al 4531854» (una búsqueda) no. Devuelve True si avanzó."""
    fila = _fila(source, kind)
    if inicio <= fila.next_id <= fin:
        avanzar(source, kind, fin)
        return True
    return False
