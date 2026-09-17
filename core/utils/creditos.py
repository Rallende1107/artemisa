"""CRÉDITOS de artista tal como los escribe una fuente («The Seatbelts feat. Mai Yamane»): partirlos en trozos para
pintarlos con link solo en los artistas que alguien enlazó A MANO (el procesado no enlaza por nombre)."""
from __future__ import annotations

import re
from collections.abc import Iterable

# Separadores entre artistas; con grupo de captura para poder conservarlos al pintar.
SEPARADORES = re.compile(r"(\s+(?:feat\.?|ft\.?|featuring|with|x|×)\s+|\s*[&,/、]\s*)", re.IGNORECASE)


def clave_artista(nombre: str) -> str:
    """Clave para comparar nombres: minúsculas, espacios simples y sin «The» inicial («The Seatbelts» = «Seatbelts»)."""
    clave = " ".join(str(nombre or "").split()).lower()
    return clave[4:] if clave.startswith("the ") else clave


def trozos_credito(credito: str, artistas: Iterable) -> list[tuple[str, object | None]]:
    """El crédito en trozos [(texto, artista o None)], con los separadores como texto suelto: cada nombre que casa con
    un artista (por `clave_artista`) lleva su objeto para enlazarlo. Sin crédito: los artistas separados por coma."""
    por_clave = {clave_artista(a.name): a for a in artistas}
    if not (credito or "").strip():
        lista = list(por_clave.values())
        trozos = []
        for n, artista in enumerate(lista):
            trozos.append((str(artista), artista))
            if n < len(lista) - 1:
                trozos.append((", ", None))
        return trozos
    trozos = []
    for i, parte in enumerate(SEPARADORES.split(credito)):
        if not parte:
            continue
        if i % 2:                                   # separador: se conserva tal cual (con un espacio a cada lado)
            trozos.append((f" {parte.strip()} " if parte.strip() not in ",、" else f"{parte.strip()} ", None))
        else:
            texto = " ".join(parte.split())
            trozos.append((texto, por_clave.get(clave_artista(texto))))
    return trozos
