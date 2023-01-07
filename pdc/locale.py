try:
    from typing import Callable
except ImportError:
    Callable = ...

TRANSLATIONS = {
    "pl": {
        "Current time": "Aktualny czas",
        "Manual control": "Sterowanie reczne",
        "OK": "OK",
        "Opening time": "Czas otwarcia",
        "Opening...": "Otwieranie...",
        "Reset": "Reset",
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
