"""Texto (utilidad genérica, estilo Poseidón)."""


class TextUtils:
    @staticmethod
    def get_initial(texto):
        """Inicial del índice alfabético: A–Z (sin acentos: «Á» → A, «Ñ» → N); lo demás —números, símbolos, japonés,
        vacío— es «#»."""
        import unicodedata
        primero = str(texto or "").strip()[:1]
        base = unicodedata.normalize("NFKD", primero)[:1].upper()
        return base if "A" <= base <= "Z" else "#"
