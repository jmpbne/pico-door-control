try:
    from typing import Callable
except ImportError:
    Callable = ...

TRANSLATIONS = {
    "pl": {
        "Current time": "Aktualna godzina",
        "Disp.Off": "Wył.ekran",
        "Manual control": "Sterowanie ręczne",
        "Now:": "Teraz:",
        "Open at:": "Otwórz o:",
        "Opening duration": "Czas otwierania",
        "Opening speed": "Prędkość otwierania",
        "Opening timer": "Godzina otwierania",
        "Opening...": "Otwieranie...",
    }
}


def gettext_en(source: str) -> str:
    return source


def gettext_pl(source: str) -> str:
    try:
        return TRANSLATIONS["pl"][source]
    except KeyError:
        # todo: logging?
        return source


def get_locale_function(locale: str) -> Callable[[str], str]:
    if locale == "en":
        return gettext_en
    if locale == "pl":
        return gettext_pl

    raise Exception(f"Locale '{locale}' not supported")
