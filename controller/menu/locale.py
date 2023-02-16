from controller import config

strings = {
    "en": {},
    "pl": {
        "System minute": "Minuta sys.",
        "System hour": "Godzina sys.",
        "Close now": "Zamknij teraz",
        "Open now": "Otworz teraz",
        "Done": "Gotowe",
        "Repeat every": "Powtorz co",
        "Repeat count": "Powtorz razy",
        "Minute": "Minuta",
        "Hour": "Godzina",
        "Speed": "Predkosc",
        "Duration": "Dlugosc",
        "System clock not set": "Nie ustawiono zegara",
        "Enter new value:": "Podaj nowa wartosc:",
    },
}


def gettext(text):
    return strings.get(config.MENU_LOCALE, {}).get(text, text)
