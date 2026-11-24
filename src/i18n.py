"""
Tiny gettext-style translation for user-facing text.

English source strings are the keys. t(lang, "Raise your saddle ~{mm:.0f} mm", mm=6) looks the
template up in the language's catalog and formats it; unknown templates fall back to English, so a
missing translation never breaks a page.
"""
import string

from src.locale_de import DE

LANGS = ('en', 'de')
DEFAULT_LANG = 'en'
_CATALOGS = {'de': DE}


class _CommaDecimals(string.Formatter):
    """German number style: 13,7 instead of 13.7."""
    def format_field(self, value, spec):
        out = format(value, spec)
        return out.replace('.', ',') if isinstance(value, float) else out


_FORMATTERS = {'de': _CommaDecimals()}


def norm(lang):
    lang = (lang or '').lower()[:2]
    return lang if lang in LANGS else DEFAULT_LANG


def t(lang, text, **kw):
    tpl = _CATALOGS.get(norm(lang), {}).get(text, text)
    if not kw:
        return tpl
    fmt = _FORMATTERS.get(norm(lang))
    try:
        return fmt.format(tpl, **kw) if fmt else tpl.format(**kw)
    except (KeyError, IndexError, ValueError):
        return text.format(**kw)


def tr_item(lang, item):
    """Translate a stored [template, params] pair (or a plain string from an older fit)."""
    if isinstance(item, (list, tuple)) and len(item) == 2 and isinstance(item[1], dict):
        return t(lang, item[0], **item[1])
    return t(lang, str(item))
