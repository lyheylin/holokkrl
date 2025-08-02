# card_utils.py

from card_data import CARD_DATA

CARD_ID_TO_MONTH = {cid: month for cid, month, _ in CARD_DATA}
CARD_ID_TO_TYPE = {cid: ctype for cid, _, ctype in CARD_DATA}

def get_month(card_id):
    return CARD_ID_TO_MONTH[card_id]

def get_type(card_id):
    return CARD_ID_TO_TYPE[card_id]
