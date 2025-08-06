# card_utils.py

from environment.card_data import CARD_DATA

CARD_ID_TO_MONTH = {cid: month for cid, month, _, _ in CARD_DATA}
CARD_ID_TO_TYPE = {cid: ctype for cid, _, ctype, _ in CARD_DATA}


#preprocess
TYPE_MAP = {}
SUBTYPE_MAP = {}

for card_id, _, card_type, sub_type in CARD_DATA:
    TYPE_MAP.setdefault(card_type, set()).add(card_id)
    if sub_type:
        SUBTYPE_MAP.setdefault(sub_type, set()).add(card_id)

def get_month(card_id):
    return CARD_ID_TO_MONTH[card_id]

def get_type(card_id):
    return CARD_ID_TO_TYPE[card_id]

def detect_yaku(collected):
    yaku = []
    points = 0

    collected_set = set(collected)

    def has_all(cards):
        return all(c in collected_set for c in cards)

    # Count by type
    bright = collected_set & TYPE_MAP.get("bright", set())
    ribbon = collected_set & TYPE_MAP.get("ribbon", set())
    animal = collected_set & TYPE_MAP.get("animal", set())
    plain = collected_set & TYPE_MAP.get("plain", set())

    poetry_ribbons = collected_set & SUBTYPE_MAP.get("poetry", set())
    blue_ribbons = collected_set & SUBTYPE_MAP.get("blue", set())
    rainman = SUBTYPE_MAP.get("rainman", set())

    # --- Yakus ---
    if len(bright) == 5:
        yaku.append(("Gokou", 10))
    elif len(bright) == 4:
        if bright & rainman:
            yaku.append(("Ame-Shikou", 7))  # Includes Rainman
        else:
            yaku.append(("Shikou", 8))
    elif len(bright) == 3:
        yaku.append(("Sankou", 5))

    if has_all(SUBTYPE_MAP.get("boar", set()) |
               SUBTYPE_MAP.get("deer", set()) |
               SUBTYPE_MAP.get("butterfly", set())):
        yaku.append(("Inoshikachou", 5))

    if len(poetry_ribbons) == 3:
        yaku.append(("Akatan", 5))

    if len(blue_ribbons) == 3:
        yaku.append(("Aotan", 5))

    if len(ribbon) >= 5:
        yaku.append(("Tanzaku", 1 + (len(ribbon) - 5)))

    if len(animal) >= 5:
        yaku.append(("Tane", 1 + (len(animal) - 5)))

    if len(plain) >= 10:
        yaku.append(("Kasu", 1 + (len(plain) - 10)))

    total_points = sum(p[1] for p in yaku)
    return yaku, total_points