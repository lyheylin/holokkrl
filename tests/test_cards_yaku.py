"""Deck and yaku tests. Card ids: month = id // 4."""
import pytest

from holokkrl.envs import rewards
from holokkrl.game.cards import CARD_DATA
from holokkrl.game.yaku import detect_yaku

CRANE, CURTAIN, MOON, RAINMAN, PHOENIX = 0, 8, 28, 40, 44


def test_deck_composition():
    assert [c[0] for c in CARD_DATA] == list(range(48))
    counts = {t: sum(c[2] == t for c in CARD_DATA) for t in ("bright", "animal", "ribbon", "plain")}
    assert counts == {"bright": 5, "animal": 9, "ribbon": 10, "plain": 24}
    assert all(sum(c[1] == m for c in CARD_DATA) == 4 for m in range(12))


@pytest.mark.parametrize("cards, expected", [
    ([CRANE, CURTAIN], []),
    ([CRANE, CURTAIN, MOON], [("Sankou", 5)]),
    ([CRANE, CURTAIN, RAINMAN], []),
    ([CRANE, CURTAIN, MOON, PHOENIX], [("Shikou", 8)]),
    ([CRANE, CURTAIN, MOON, RAINMAN], [("Ame-Shikou", 7)]),
    ([CRANE, CURTAIN, MOON, RAINMAN, PHOENIX], [("Gokou", 10)]),
])
def test_bright_yaku(cards, expected):
    assert detect_yaku(cards)[0] == expected


@pytest.mark.parametrize("cards, expected", [
    ([20, 24, 36], [("Inoshikachou", 5)]),
    ([20, 24], []),
    ([1, 5, 9], [("Akatan", 5)]),
    ([1, 5, 13], []),
    ([21, 33, 37], [("Aotan", 5)]),
    ([21, 33, 13], []),
    ([1, 5, 13, 17], []),
    ([1, 5, 13, 17, 25], [("Tanzaku", 1)]),
    ([1, 5, 13, 17, 25, 42], [("Tanzaku", 2)]),
    ([4, 12, 16, 29], []),
    ([4, 12, 16, 29, 32], [("Tane", 1)]),
    ([4, 12, 16, 29, 32, 41], [("Tane", 2)]),
    ([2, 3, 6, 7, 10, 11, 14, 15, 18], []),
    ([2, 3, 6, 7, 10, 11, 14, 15, 18, 19], [("Kasu", 1)]),
    ([2, 3, 6, 7, 10, 11, 14, 15, 18, 19, 22], [("Kasu", 2)]),
])
def test_other_yaku(cards, expected):
    assert detect_yaku(cards)[0] == expected


def test_akatan_and_aotan_score_together():
    yaku, points = detect_yaku([1, 5, 9, 21, 33, 37])
    assert {n for n, _ in yaku} == {"Akatan", "Aotan", "Tanzaku"} and points == 12


def test_every_yaku_has_reward_entries():
    names = {n for n, _ in detect_yaku(range(48))[0]}
    names |= {"Sankou", "Shikou", "Ame-Shikou"}
    assert names == set(rewards.ONGOING_YAKU_REWARDS) == set(rewards.FORMATION_BONUSES)
