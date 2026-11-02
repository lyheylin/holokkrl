"""Rule and invariant tests for the Koi-Koi engine. Card ids: month = id // 4."""
import numpy as np
import pytest

from holokkrl.envs import rewards
from holokkrl.envs.koikoi_env import KoiKoiEnv
from holokkrl.game.yaku import detect_yaku

CRANE, CURTAIN, MOON, RAINMAN, PHOENIX = 0, 8, 28, 40, 44


class StubRng:
    """Scripted koi-koi decisions; everything else defers to a real generator."""

    def __init__(self, koikoi, seed=0):
        self.koikoi = koikoi
        self.real = np.random.default_rng(seed)

    def random(self):
        return 0.0 if self.koikoi else 0.99

    def choice(self, options):
        return options[0]

    def __getattr__(self, name):
        return getattr(self.real, name)


def rigged(hand, opp, field, deck, collected=(), opp_collected=(), max_rounds=3):
    env = KoiKoiEnv(max_rounds=max_rounds)
    env.reset(seed=0)
    env.player_hands = [sorted(hand), sorted(opp)]
    env.field = sorted(field)
    env.deck = list(deck)
    env.collected_cards = [list(collected), list(opp_collected)]
    env._player_progress = rewards.yaku_progress(env.collected_cards[0])
    env._opponent_progress = rewards.yaku_progress(env.collected_cards[1])
    env.best_yaku_points = {
        0: detect_yaku(env.collected_cards[0])[1],
        1: detect_yaku(env.collected_cards[1])[1],
    }
    env.current_yakus = {
        0: {n for n, _ in detect_yaku(env.collected_cards[0])[0]},
        1: {n for n, _ in detect_yaku(env.collected_cards[1])[0]},
    }
    return env


def play(env, card, field_card=None):
    slot = env.NO_MATCH if field_card is None else env.field.index(field_card)
    return env.encode_play(env.player_hands[0].index(card), slot)


def snapshot(env):
    return (
        list(env.player_hands[0]), list(env.player_hands[1]), list(env.field),
        list(env.deck), list(env.collected_cards[0]), list(env.collected_cards[1]),
        env.your_score, env.opponent_score, env.koikoi_pending,
    )


# --- Koi-Koi scoring ---

def sankou_env(**kwargs):
    """The player holds two brights and can capture a third by playing the moon."""
    return rigged(
        hand=[MOON, 5], opp=[14, 15], field=[30, 47, 10],
        deck=[20, 21, 22, 23], collected=[CRANE, CURTAIN], **kwargs,
    )


def form_sankou(env):
    return env.step(play(env, MOON, 30))


def test_points_are_not_banked_until_stop():
    env = sankou_env()
    _, reward, *_, info = form_sankou(env)
    assert info["awaiting_koikoi"] and env.koikoi_pending
    assert env.your_score == 0 and env.your_round_score == 0
    assert info["formation_bonus"] == rewards.FORMATION_BONUSES["Sankou"]
    assert info["ongoing_yaku_reward"] == rewards.ONGOING_YAKU_REWARDS["Sankou"]
    # Shaping for capturing the bright and the yaku rewards survive the decision step.
    assert reward == pytest.approx(0.8 + 0.12 + 12 + 1.5)


def test_stop_scores_once_and_ends_round_with_win_bonus():
    env = sankou_env()
    form_sankou(env)
    _, reward, _, _, info = env.step(env.STOP_ACTION)
    assert env.your_score == 5 and env.opponent_score == 0
    assert info["stopped"] and info["round_over"] and not info["match_over"]
    assert info["outcome_bonus"] == 12
    assert reward == 5 + 12
    assert env.round_count == 1


def test_koikoi_passes_to_opponent_and_does_not_score():
    env = sankou_env()
    form_sankou(env)
    opp_before = len(env.player_hands[1])
    env.step(env.KOIKOI_ACTION)
    assert len(env.player_hands[1]) == opp_before - 1
    assert env.your_score == 0 and not env.koikoi_pending


def test_no_reprompt_without_improvement_and_reprompt_on_improvement():
    env = rigged(
        hand=[5, 6, RAINMAN], opp=[14, 15, 18], field=[41, 47],
        deck=[20, 23, 26, 31, 34, 37, 38],
        collected=[CRANE, CURTAIN, MOON],
    )
    env.koikoi_declared[0] = True
    env.step(play(env, 5))
    assert not env.koikoi_pending and env.your_score == 0
    _, _, _, _, info = env.step(play(env, RAINMAN, 41))
    assert env.koikoi_pending and info["awaiting_koikoi"]
    assert [n for n, _ in info["yaku"]] == ["Ame-Shikou"]
    env.step(env.STOP_ACTION)
    assert env.your_score == 7


def test_exhausted_round_scores_nothing_even_after_koikoi():
    env = rigged(hand=[MOON], opp=[46], field=[30], deck=[20, 21, 22, 23],
                 collected=[CRANE, CURTAIN])
    env.step(play(env, MOON, 30))
    env.np_random = StubRng(koikoi=True)
    _, reward, _, _, info = env.step(env.KOIKOI_ACTION)
    assert info["round_over"] and info["outcome_bonus"] == 0
    assert env.your_score == 0 and env.opponent_score == 0
    assert env.round_count == 1


def test_opponent_stop_scores_only_opponent():
    env = rigged(hand=[5, 6], opp=[MOON, 46], field=[30], deck=[21, 22, 23, 25],
                 opp_collected=[CRANE, CURTAIN])
    env.np_random = StubRng(koikoi=False)
    _, _, _, _, info = env.step(play(env, 5))
    assert info["opponent_koikoi"] is False
    assert info["round_over"] and info["outcome_bonus"] == -8
    assert env.opponent_score == 5 and env.your_score == 0


def test_opponent_koikoi_redecides_only_on_improvement():
    env = rigged(hand=[5, 13, 17], opp=[MOON, RAINMAN, 46], field=[30, 41],
                 deck=[21, 22, 23, 25, 26, 27], opp_collected=[CRANE, CURTAIN])
    env.np_random = StubRng(koikoi=True)
    # The stubbed opponent plays the moon first, forming Sankou.
    _, _, _, _, info = env.step(play(env, 5))
    assert info["opponent_koikoi"] is True and env.opponent_score == 0
    # Next improvement (Ame-Shikou) triggers a fresh decision, this time stopping.
    env.np_random = StubRng(koikoi=False)
    _, _, _, _, info = env.step(play(env, 13))
    assert info["opponent_koikoi"] is False and env.opponent_score == 7


def test_opponent_does_not_redecide_without_improvement():
    env = rigged(hand=[5, 13, 17], opp=[MOON, 46, 47], field=[30],
                 deck=[21, 22, 23, 25, 26, 27], opp_collected=[CRANE, CURTAIN])
    env.np_random = StubRng(koikoi=True)
    _, _, _, _, info = env.step(play(env, 5))
    assert info["opponent_koikoi"] is True
    env.np_random = StubRng(koikoi=False)  # Would stop if it were asked again.
    _, _, _, _, info = env.step(play(env, 13))
    assert "opponent_koikoi" not in info and env.opponent_score == 0
    assert not info["round_over"]


def test_round_state_is_cleared_between_rounds():
    env = sankou_env()
    form_sankou(env)
    env.step(env.STOP_ACTION)
    assert env.collected_cards[0] == []
    assert env.current_yakus[0] == set()
    assert env.best_yaku_points[0] == 0
    assert env.your_round_score == 0 and env.opponent_round_score == 0
    assert env.koikoi_declared == [False, False]
    assert env.last_drawn_card is None
    assert env.your_score == 5  # The match score carries over.


# --- Rewards ---

def test_blocking_penalty_zero_when_opponent_takes_nothing_useful():
    env = rigged(hand=[5, 6], opp=[46, 47], field=[1], deck=[9, 13, 17, 25])
    _, _, _, _, info = env.step(play(env, 5))
    assert info["blocking_penalty"] == 0.0


def test_blocking_penalty_applies_and_is_capped():
    env = rigged(hand=[5, 6], opp=[CRANE, 46], field=[1, 13], deck=[17, 25, 42, 33])
    # Opponent captures a bright + poetry ribbon: -0.8 + -0.3 + -1.0 = -2.1, floored at -2.0.
    _, _, _, _, info = env.step(play(env, 5))
    assert info["blocking_penalty"] == -2.0
    env = rigged(hand=[5, 6], opp=[46, 47], field=[45], deck=[17, 25, 42, 33])
    _, _, _, _, info = env.step(play(env, 5))
    assert info["blocking_penalty"] == pytest.approx(-0.2)


def test_forced_draw_capture_earns_progress_shaping():
    env = rigged(hand=[5, 6], opp=[46, 47], field=[2], deck=[CRANE, 20, 21, 22])
    _, reward, _, _, _ = env.step(play(env, 5))
    assert reward == pytest.approx(0.8 + 0.12)  # bright + plain captured from the draw


def test_chosen_draw_capture_earns_progress_shaping():
    env = rigged(hand=[5, 6], opp=[46, 47], field=[1, 2], deck=[CRANE, 20, 21, 22])
    _, reward, _, _, _ = env.step(play(env, 5))
    assert reward == 0
    _, reward, _, _, _ = env.step(env.DRAW_MATCH_FIRST)  # takes the poetry ribbon
    assert reward == pytest.approx(0.8 + 1.0 + 0.3)


def test_play_capture_reward_survives_pending_draw_choice():
    env = rigged(hand=[CRANE, 6], opp=[46, 47], field=[1, 21, 22], deck=[20, 23, 25, 26])
    _, reward, _, _, info = env.step(play(env, CRANE, 1))
    assert info["awaiting_draw_match"]
    assert reward == pytest.approx(0.8 + 1.0 + 0.3)  # bright + poetry ribbon


def test_formation_bonus_is_paid_once_and_ongoing_every_turn():
    env = rigged(hand=[MOON, 5, 13], opp=[14, 15, 18], field=[30], deck=[20, 22, 26, 31, 34, 38],
                 collected=[CRANE, CURTAIN])
    _, _, _, _, info = env.step(play(env, MOON, 30))
    assert info["formation_bonus"] == 12 and info["ongoing_yaku_reward"] == 1.5
    env.step(env.KOIKOI_ACTION)
    _, _, _, _, info = env.step(play(env, 5))
    assert info["formation_bonus"] == 0 and info["ongoing_yaku_reward"] == 1.5


def test_yaku_formed_together_are_reported_in_stable_order():
    env = rigged(hand=[9, 6], opp=[46, 47], field=[CURTAIN], deck=[20, 21, 22, 23],
                 collected=[CRANE, MOON, 1, 5])
    _, _, _, _, info = env.step(play(env, 9, CURTAIN))
    assert info["new_yakus"] == ["Akatan", "Sankou"]


def test_opponent_draw_capture_counts_as_blocking():
    env = rigged(hand=[5, 6], opp=[46], field=[1], deck=[20, CRANE, 21, 22])
    _, _, _, _, info = env.step(play(env, 5))
    # Crane drawn by the opponent captures the poetry ribbon: -0.8 - 1.0 - 0.3, floored.
    assert info["blocking_penalty"] == -2.0


def test_koikoi_reward_excludes_earlier_turn_rewards():
    env = sankou_env()
    form_sankou(env)
    _, reward, _, _, info = env.step(env.KOIKOI_ACTION)
    assert reward == info["blocking_penalty"]


# --- Matching rules ---

def test_illegal_actions_leave_state_untouched():
    env = rigged(hand=[CRANE, 4], opp=[10, 11], field=[1, 47], deck=[45, 46, 20, 21])
    before = snapshot(env)
    for action in (
        play(env, 4, 1),            # wrong month
        play(env, CRANE),           # declining an available match
        env.encode_play(5, 0),      # empty hand slot
        env.encode_play(0, 16),     # empty field slot
        env.KOIKOI_ACTION,          # no decision pending
        env.STOP_ACTION,
        env.DRAW_MATCH_FIRST,
        -1,
        env.total_actions,
    ):
        _, reward, terminated, truncated, info = env.step(action)
        assert reward == -1 and "error" in info
        assert not terminated and not truncated
        assert snapshot(env) == before


def test_koikoi_decision_rejects_other_actions():
    env = sankou_env()
    form_sankou(env)
    _, reward, _, _, info = env.step(0)
    assert reward == -1 and "error" in info and env.koikoi_pending


def test_repeated_illegal_actions_truncate_instead_of_hanging():
    env = rigged(hand=[CRANE], opp=[10], field=[47], deck=[45, 46, 20, 21])
    for _ in range(env.MAX_CONSECUTIVE_ILLEGAL - 1):
        assert not env.step(env.encode_play(7, 0))[3]
    assert env.step(env.encode_play(7, 0))[3] is True


def test_legal_action_resets_illegal_counter():
    env = rigged(hand=[5, 6], opp=[46, 47], field=[1], deck=[9, 13, 17, 25])
    for _ in range(env.MAX_CONSECUTIVE_ILLEGAL - 1):
        env.step(env.encode_play(7, 0))
    env.step(play(env, 5))
    assert not env.step(env.encode_play(7, 0))[3]


def test_playing_fourth_card_captures_all_three():
    env = rigged(hand=[CRANE, 4], opp=[10, 11], field=[1, 2, 3, 47], deck=[45, 46, 20, 21])
    _, _, _, _, info = env.step(play(env, CRANE, 2))
    assert sorted(env.collected_cards[0][:4]) == [0, 1, 2, 3]
    assert sorted(info["player_field_captured"]) == [1, 2, 3]
    assert not any(c // 4 == 0 for c in env.field)


def test_drawing_fourth_card_captures_all_three():
    env = rigged(hand=[5, 6], opp=[46, 47], field=[1, 2, 3], deck=[CRANE, 20, 21, 22])
    env.step(play(env, 5))
    assert sorted(env.collected_cards[0]) == [0, 1, 2, 3]


def test_opponent_fourth_card_captures_all_three():
    env = rigged(hand=[5, 6], opp=[CRANE, 46], field=[1, 2, 3], deck=[20, 33, 22, 23])
    env.step(play(env, 5))
    assert sorted(env.collected_cards[1]) == [0, 1, 2, 3]


@pytest.mark.parametrize("choice, taken", [("DRAW_MATCH_FIRST", 1), ("DRAW_MATCH_SECOND", 2)])
def test_player_chooses_between_two_draw_matches(choice, taken):
    env = rigged(hand=[5, 6], opp=[46, 47], field=[1, 2], deck=[CRANE, 20, 21, 22])
    obs, _, _, _, info = env.step(play(env, 5))
    assert info["awaiting_draw_match"] and obs["phase"] == env.PHASE_DRAW_MATCH
    assert obs["last_drawn_card"][CRANE] == 1
    assert len(env.player_hands[1]) == 2  # Opponent waits for the decision.
    mask = env.action_masks()
    assert mask.sum() == 2 and mask[env.DRAW_MATCH_FIRST] and mask[env.DRAW_MATCH_SECOND]

    obs, _, _, _, info = env.step(getattr(env, choice))
    assert info["player_draw_match"] == taken
    assert sorted(env.collected_cards[0]) == sorted([CRANE, taken])
    assert obs["phase"] == env.PHASE_PLAY
    assert len(env.player_hands[1]) == 1


def test_field_cards_past_the_eighth_can_be_matched():
    field = [1, 5, 9, 13, 17, 21, 25, 29, 33, 37]
    env = rigged(hand=[34, 45], opp=[46, 47], field=field, deck=[41, 43, 42, 40])
    action = play(env, 34, 33)
    assert env.field.index(33) >= 8 and env.action_masks()[action]
    env.step(action)
    assert {33, 34} <= set(env.collected_cards[0])


def test_hand_and_field_order_is_derivable_from_observation():
    env = KoiKoiEnv()
    env.reset(seed=3)
    for _ in range(30):
        obs = env._get_obs()
        assert env.player_hands[0] == list(np.flatnonzero(obs["hand"]))
        assert env.field == list(np.flatnonzero(obs["field"]))
        legal = np.flatnonzero(env.action_masks())
        if env.step(int(legal[0]))[2]:
            break


def test_four_of_a_month_on_field_forces_redeal():
    env = KoiKoiEnv()
    calls = []
    real_shuffle = np.random.default_rng(1).shuffle

    class Rng(StubRng):
        def shuffle(self, deck):
            calls.append(1)
            if len(calls) == 1:
                rest = [c for c in deck if c >= 4]
                deck[:] = rest[:16] + [0, 1, 2, 3] + rest[16:]
            else:
                real_shuffle(deck)

    env.np_random = Rng(koikoi=False)
    env.round_count = 0
    env._start_new_round()
    assert len(calls) >= 2
    months = [c // 4 for c in env.field]
    assert max(months.count(m) for m in months) < 4


# --- Dealer ---

def test_round_winner_deals_next_round():
    env = sankou_env()
    form_sankou(env)
    env.dealer = 1
    env.step(env.STOP_ACTION)
    assert env.dealer == 0
    assert len(env.player_hands[1]) == 8

    env = rigged(hand=[5, 6], opp=[MOON, 46], field=[30], deck=[21, 22, 23, 25],
                 opp_collected=[CRANE, CURTAIN])
    env.np_random = StubRng(koikoi=False)
    env.dealer = 0
    _, _, _, _, info = env.step(play(env, 5))
    assert env.dealer == 1
    # Opponent opened the new round, so it holds one card fewer than the player.
    assert len(env.player_hands[0]) == 8 and len(env.player_hands[1]) == 7
    assert "opening_opponent_turn" in info


def test_exhausted_round_keeps_dealer():
    env = rigged(hand=[5], opp=[46], field=[47], deck=[21, 22, 23, 25])
    env.dealer = 1
    env.player_hands[1] = []  # Dealer already played its last card.
    _, _, _, _, info = env.step(play(env, 5))
    assert info["round_over"] and env.dealer == 1


def test_non_dealer_plays_last_card_when_opponent_opened():
    env = rigged(hand=[5, 13], opp=[46], field=[47], deck=[21, 22, 23, 25])
    env.dealer = 1
    _, _, _, _, info = env.step(play(env, 5))
    # Opponent's hand is now empty, but the player still has a card to play.
    assert not info["round_over"] and env.player_hands == [[13], []]
    _, _, _, _, info = env.step(play(env, 13))
    assert info["round_over"]


def test_both_dealers_occur_on_reset():
    dealers = set()
    for seed in range(40):
        env = KoiKoiEnv()
        _, info = env.reset(seed=seed)
        dealers.add(env.dealer)
        assert ("opening_opponent_turn" in info) == (env.dealer == 1)
    assert dealers == {0, 1}


# --- Observations and API ---

def test_card_zero_appears_as_last_drawn():
    env = KoiKoiEnv()
    env.reset(seed=0)
    env.last_drawn_card = 0
    assert env._get_obs()["last_drawn_card"][0] == 1


def test_terminal_observation_is_in_space():
    env = sankou_env(max_rounds=1)
    form_sankou(env)
    obs, _, terminated, _, info = env.step(env.STOP_ACTION)
    assert terminated and info["match_over"]
    assert env.observation_space.contains(obs)


def full_game_trace(seed):
    env = KoiKoiEnv()
    obs, _ = env.reset(seed=seed)
    trace = [snapshot(env)]
    rng = np.random.default_rng(seed)
    terminated = False
    while not terminated:
        action = int(rng.choice(np.flatnonzero(env.action_masks())))
        obs, _, terminated, truncated, _ = env.step(action)
        assert not truncated
        trace.append(snapshot(env))
    return trace


def test_seed_reproduces_whole_match():
    assert full_game_trace(11) == full_game_trace(11)
    assert full_game_trace(11) != full_game_trace(12)


def test_invariants_over_random_matches():
    max_field = 0
    for seed in range(300):
        env = KoiKoiEnv()
        obs, _ = env.reset(seed=seed)
        assert env.observation_space.contains(obs)
        rng = np.random.default_rng(seed)
        terminated = False
        steps = 0
        while not terminated:
            steps += 1
            assert steps < 200
            piles = [*env.player_hands[0], *env.player_hands[1], *env.field, *env.deck,
                     *env.collected_cards[0], *env.collected_cards[1]]
            if env.pending_draw_card is not None:
                piles.append(env.pending_draw_card)
            assert sorted(piles) == list(range(48))
            assert len(env.field) <= env.max_field_size
            max_field = max(max_field, len(env.field))
            mask = env.action_masks()
            assert mask.any()
            action = int(rng.choice(np.flatnonzero(mask)))
            obs, reward, terminated, truncated, info = env.step(action)
            assert "error" not in info and not truncated
            assert env.observation_space.contains(obs)
        assert env.round_count == env.max_rounds
    assert max_field > env.field_size


def test_registered_with_gymnasium():
    import gymnasium as gym
    import holokkrl.envs  # noqa: F401
    env = gym.make("KoiKoi-v0", max_rounds=2)
    env.reset(seed=0)
    assert env.unwrapped.max_rounds == 2


def test_passes_stable_baselines_env_checker():
    from stable_baselines3.common.env_checker import check_env
    check_env(KoiKoiEnv(), warn=False)
