from controller import config

strings = {
    "en": {},
    "pl": {
        "Close now": "Zamknij teraz",
        "Done": "Gotowe",
        "Duration": "Dlugosc",
        "Enter new value:": "Podaj nowa wartosc:",
        "Hour": "Godzina",
        "Minute": "Minuta",
        "Open now": "Otworz teraz",
        "Repeat count": "Powtorz razy",
        "Repeat every": "Powtorz co",
        "Set system time first": "Najpierw ustaw zegar",
        "Speed": "Predkosc",
        "System clock not set": "Nie ustawiono zegara",
        "System hour": "Godzina zegara",
        "System minute": "Minuta zegara",
    },
}


def gettext(text):
    return strings.get(config.MENU_LOCALE, {}).get(text, text)
