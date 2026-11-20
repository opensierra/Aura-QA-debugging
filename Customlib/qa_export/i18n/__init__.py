"""Textos i18n del reporte Excel (un modulo por idioma)."""
from . import en, es, vi, id, ur, pt, th  # noqa: F401

_L = {
    "en": en.TEXTS,
    "es": es.TEXTS,
    "vi": vi.TEXTS,
    "id": id.TEXTS,
    "ur": ur.TEXTS,
    "pt": pt.TEXTS,
    "th": th.TEXTS,
}


def _lang(code):
    return _L.get(str(code or "en").lower()[:2], _L["en"])
