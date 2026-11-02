"""Training rewards. These are not part of the game rules; see docs/ENVIRONMENT.md.

Different parameters --
  progress_reward: small stepwise nudges toward yaku formation.
  ONGOING_YAKU_REWARDS: holding yakus generates constant positive reinforcement.
  FORMATION_BONUSES: one-time bonus when a new yaku appears.
  blocking_penalty: the opponent captured cards from the yaku pools.
  round_outcome_bonus: flat bonus for how the round ended.
Game points are also paid as reward when the player stops.
"""

from holokkrl.game.cards import get_card_info

ILLEGAL_ACTION_PENALTY = -1

# Keys must match the yaku names returned by detect_yaku.
ONGOING_YAKU_REWARDS = {
    "Kasu": 0.5,
    "Tane": 1.0,
    "Tanzaku": 1.0,
    "Sankou": 1.5,
    "Ame-Shikou": 1.75,
    "Shikou": 2.0,
    "Gokou": 3.0,
    "Inoshikachou": 1.5,
    "Akatan": 1.0,
    "Aotan": 1.0,
}

FORMATION_BONUSES = {
    "Kasu": 4,
    "Tane": 8,
    "Tanzaku": 8,
    "Sankou": 12,
    "Ame-Shikou": 15,
    "Shikou": 18,
    "Gokou": 30,
    "Inoshikachou": 12,
    "Akatan": 10,
    "Aotan": 10,
}

# Keys must match the categories returned by yaku_progress.
SHAPING_WEIGHTS = {
    "brights": 0.8,
    "poetry": 1.0,
    "blue": 1.0,
    "ribbon": 0.3,
    "animal": 0.35,
    "plain": 0.12,
    "ino_parts": 1.1,
}

BLOCKING_WEIGHTS = {
    "brights": -0.8,
    "poetry": -1.0,
    "blue": -1.0,
    "ribbon": -0.3,
    "animal": -0.4,
    "plain": -0.1,
    "ino_parts": -1.1,
}
BLOCKING_PENALTY_CAP = -2.0  # floor per opponent turn

ROUND_WIN_BONUS = 12
ROUND_LOSS_BONUS = -8


def yaku_progress(collected_cards):
    """Return card counts per yaku category for a collected pile."""
    prog = {
        "brights": 0,
        "poetry": 0,
        "blue": 0,
        "ribbon": 0,
        "animal": 0,
        "plain": 0,
        "ino_parts": 0,  # boar/deer/butterfly pieces
    }

    for card_id in collected_cards:
        info = get_card_info(card_id)
        card_type = info["type"]
        subtype = info["subtype"]

        if card_type == "bright":
            prog["brights"] += 1
        elif card_type == "ribbon":
            prog["ribbon"] += 1
            if subtype == "poetry":
                prog["poetry"] += 1
            if subtype == "blue":
                prog["blue"] += 1
        elif card_type == "animal":
            prog["animal"] += 1
            if subtype in ("boar", "deer", "butterfly"):
                prog["ino_parts"] += 1
        elif card_type == "plain":
            prog["plain"] += 1

    return prog


def _weighted_gain(weights, before, after):
    total = 0.0
    for category, weight in weights.items():
        delta = after[category] - before[category]
        if delta > 0:
            total += weight * delta
    return total


def progress_reward(before, after):
    """Positive-only shaping for the player's own captures."""
    return _weighted_gain(SHAPING_WEIGHTS, before, after)


def blocking_penalty(before, after):
    """Penalty for the opponent's captures, given the opponent's progress."""
    return max(_weighted_gain(BLOCKING_WEIGHTS, before, after), BLOCKING_PENALTY_CAP)


def round_outcome_bonus(score_diff):
    """Bonus from the round's score difference (yours minus the opponent's)."""
    if score_diff > 0:
        return ROUND_WIN_BONUS
    if score_diff < 0:
        return ROUND_LOSS_BONUS
    return 0
