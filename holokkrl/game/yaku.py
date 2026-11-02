"""Yaku detection. See docs/RULES.md section 5."""

from holokkrl.game.cards import SUBTYPE_MAP, TYPE_MAP

BRIGHTS = TYPE_MAP["bright"]
RIBBONS = TYPE_MAP["ribbon"]
ANIMALS = TYPE_MAP["animal"]
PLAINS = TYPE_MAP["plain"]

POETRY_RIBBONS = SUBTYPE_MAP["poetry"]
BLUE_RIBBONS = SUBTYPE_MAP["blue"]
RAINMAN = SUBTYPE_MAP["rainman"]
INOSHIKACHOU = SUBTYPE_MAP["boar"] | SUBTYPE_MAP["deer"] | SUBTYPE_MAP["butterfly"]


def detect_yaku(collected):
    """Return ([(name, points), ...], total points) for a collected pile."""
    collected_set = set(collected)
    yaku = []

    # At most one bright yaku applies (R5.2).
    bright = collected_set & BRIGHTS
    if len(bright) == 5:
        yaku.append(("Gokou", 10))
    elif len(bright) == 4:
        if bright & RAINMAN:
            yaku.append(("Ame-Shikou", 7))
        else:
            yaku.append(("Shikou", 8))
    elif len(bright) == 3 and not bright & RAINMAN:
        yaku.append(("Sankou", 5))

    if INOSHIKACHOU <= collected_set:
        yaku.append(("Inoshikachou", 5))

    if POETRY_RIBBONS <= collected_set:
        yaku.append(("Akatan", 5))

    if BLUE_RIBBONS <= collected_set:
        yaku.append(("Aotan", 5))

    ribbons = len(collected_set & RIBBONS)
    if ribbons >= 5:
        yaku.append(("Tanzaku", 1 + (ribbons - 5)))

    animals = len(collected_set & ANIMALS)
    if animals >= 5:
        yaku.append(("Tane", 1 + (animals - 5)))

    plains = len(collected_set & PLAINS)
    if plains >= 10:
        yaku.append(("Kasu", 1 + (plains - 10)))

    return yaku, sum(points for _, points in yaku)
