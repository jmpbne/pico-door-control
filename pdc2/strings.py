strings = {}


def _(orig):
    return strings.get(orig, orig)
