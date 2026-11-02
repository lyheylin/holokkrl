"""Score screens saved from Holo's Hanafuda, compared with detect_yaku.

Card IDs were read by eye from the screenshots; see docs/HOLOS_HANAFUDA_CARDS.md. None of these
screens involve a rule that differs from the base rules, so they also hold under RULES.md section 10.
"""
from collections import Counter

import pytest

from holokkrl.game.cards import get_card_info, get_month
from holokkrl.game.yaku import detect_yaku

ROUND_1_TANE = [41, 29, 36, 4, 12]
ROUND_2_TAN = [9, 25, 33, 21, 13]
ROUND_2_KASU = [10, 27, 34, 23, 14, 45, 46, 7, 43, 11]

# The whole collected pile, in the groups the game shows it in.
ROUND_3_BRIGHTS = [8]
ROUND_3_ANIMALS = [20, 4, 41, 12]
ROUND_3_RIBBONS = [21, 17, 5, 42, 13]
ROUND_3_PLAINS = [23, 47, 46, 6, 22, 18, 7, 34, 35, 10]
ROUND_3_PILE = ROUND_3_BRIGHTS + ROUND_3_ANIMALS + ROUND_3_RIBBONS + ROUND_3_PLAINS


@pytest.mark.parametrize("cards, yaku, total", [
    (ROUND_1_TANE, [("Tane", 1)], 1),
    (ROUND_2_TAN + ROUND_2_KASU, [("Tanzaku", 1), ("Kasu", 1)], 2),
    (ROUND_3_PILE, [("Tanzaku", 1), ("Kasu", 1)], 2),
])
def test_score_screen_matches_detect_yaku(cards, yaku, total):
    assert detect_yaku(cards) == (yaku, total)


@pytest.mark.parametrize("cards, card_type", [
    (ROUND_1_TANE, "animal"),
    (ROUND_2_TAN, "ribbon"),
    (ROUND_2_KASU, "plain"),
    (ROUND_3_BRIGHTS, "bright"),
    (ROUND_3_ANIMALS, "animal"),
    (ROUND_3_RIBBONS, "ribbon"),
    (ROUND_3_PLAINS, "plain"),
])
def test_game_groups_cards_by_the_engine_types(cards, card_type):
    assert {get_card_info(card)["type"] for card in cards} == {card_type}


def test_full_pile_could_come_from_real_captures():
    # Captures take 2 or 4 cards of a month, so every month's count must be even.
    assert len(set(ROUND_3_PILE)) == len(ROUND_3_PILE) == 20
    assert all(count % 2 == 0 for count in Counter(map(get_month, ROUND_3_PILE)).values())
