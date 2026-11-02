"""Tests for rule flags and for tying saved models to the rules they were trained under."""
from pathlib import Path
import re

import gymnasium as gym
import numpy as np
import pytest
from stable_baselines3 import PPO

import holokkrl.envs  # noqa: F401
from holokkrl.envs.koikoi_env import KoiKoiEnv
from holokkrl.game.rules import RULESET_VERSION, RuleConfig
from holokkrl.models import RulesMismatchError, load_model, read_model_rules, save_model

STRICT = RuleConfig(must_capture_if_able=True)


def rigged(rules, hand, field):
    env = KoiKoiEnv(rules=rules)
    env.reset(seed=0)
    env.player_hands = [sorted(hand), [46, 47]]
    env.field = sorted(field)
    env.deck = [20, 21, 22, 23]
    env.collected_cards = [[], []]
    return env


def legal_plays(env):
    return {tuple(divmod(int(a), env.max_field_size + 1)) for a in np.flatnonzero(env.action_masks())}


# --- The flag ---

def test_default_rules_are_the_free_discard_rule():
    assert KoiKoiEnv().rules == RuleConfig(must_capture_if_able=False)


def test_rules_cannot_change_after_creation():
    with pytest.raises(AttributeError):
        STRICT.must_capture_if_able = False


def test_free_rule_allows_discard_while_another_card_could_capture():
    env = rigged(RuleConfig(), hand=[0, 4], field=[1, 45])
    no_match = env.NO_MATCH
    assert legal_plays(env) == {(0, env.field.index(1)), (1, no_match)}


def test_strict_rule_forbids_discard_while_another_card_could_capture():
    env = rigged(STRICT, hand=[0, 4], field=[1, 45])
    assert legal_plays(env) == {(0, env.field.index(1))}
    discard = env.encode_play(1, env.NO_MATCH)
    before = list(env.player_hands[0])
    _, reward, _, _, info = env.step(discard)
    assert reward == -1 and "error" in info and env.player_hands[0] == before


def test_strict_rule_allows_any_discard_when_nothing_can_capture():
    env = rigged(STRICT, hand=[0, 4], field=[45, 41])
    assert legal_plays(env) == {(0, env.NO_MATCH), (1, env.NO_MATCH)}


def test_strict_rule_still_lets_player_choose_among_capturing_cards():
    env = rigged(STRICT, hand=[0, 4, 12], field=[1, 2, 5, 45])
    assert legal_plays(env) == {(0, env.field.index(1)), (0, env.field.index(2)), (1, env.field.index(5))}


def test_flag_reaches_env_through_gym_make():
    env = gym.make("KoiKoi-v0", rules=STRICT)
    assert env.unwrapped.rules == STRICT


@pytest.mark.parametrize("rules", [RuleConfig(), STRICT])
def test_invariants_and_masks_over_random_matches(rules):
    for seed in range(150):
        env = KoiKoiEnv(rules=rules)
        obs, _ = env.reset(seed=seed)
        rng = np.random.default_rng(seed)
        terminated = False
        while not terminated:
            piles = [*env.player_hands[0], *env.player_hands[1], *env.field, *env.deck,
                     *env.collected_cards[0], *env.collected_cards[1]]
            if env.pending_draw_card is not None:
                piles.append(env.pending_draw_card)
            assert sorted(piles) == list(range(48))

            mask = env.action_masks()
            assert mask.any()
            if not env.koikoi_pending and env.pending_draw_card is None:
                # Independent derivation of who may discard, from months alone.
                field_months = {c // 4 for c in env.field}
                can_capture = [c for c in env.player_hands[0] if c // 4 in field_months]
                discards = {h for h, f in legal_plays(env) if f == env.NO_MATCH}
                free = {i for i, c in enumerate(env.player_hands[0]) if c // 4 not in field_months}
                assert discards == (set() if rules.must_capture_if_able and can_capture else free)

            action = int(rng.choice(np.flatnonzero(mask)))
            obs, _, terminated, truncated, info = env.step(action)
            assert "error" not in info and not truncated
            assert env.observation_space.contains(obs)


def test_builtin_opponent_obeys_strict_rule():
    env = KoiKoiEnv(rules=STRICT)
    for seed in range(100):
        env.reset(seed=seed)
        env.player_hands[1] = [0, 4]
        env.field = [1, 45]
        env.player_hands[0] = [12, 13]
        env.deck = [20, 25, 30, 35]
        env.collected_cards = [[], []]
        _, _, _, _, info = env.step(env.encode_play(0, env.NO_MATCH))
        assert info["opponent_played_card"] == 0 and info["opponent_play_match"] == 1


def test_ruleset_version_matches_rules_document():
    text = (Path(__file__).parents[1] / "docs" / "RULES.md").read_text(encoding="utf-8")
    assert re.search(r"^# Koi-Koi Rules \(Project Ruleset v([\d.]+)\)", text, re.M).group(1) == RULESET_VERSION
    assert "`must_capture_if_able`" in text


# --- Models are tied to their rules ---

@pytest.fixture(scope="module")
def saved_models(tmp_path_factory):
    folder = tmp_path_factory.mktemp("models")
    paths = {}
    for name, rules in (("free", RuleConfig()), ("strict", STRICT)):
        model = PPO("MultiInputPolicy", KoiKoiEnv(rules=rules), n_steps=8, batch_size=8, n_epochs=1, device="cpu")
        paths[name] = save_model(model, folder / name)
    return paths


def test_saved_model_records_its_rules(saved_models):
    assert read_model_rules(saved_models["free"]) == RuleConfig().signature()
    assert read_model_rules(saved_models["strict"]) == STRICT.signature()


@pytest.mark.parametrize("name, rules", [("free", RuleConfig()), ("strict", STRICT)])
def test_model_loads_and_runs_when_rules_match(saved_models, name, rules):
    env = KoiKoiEnv(rules=rules)
    model = load_model(saved_models[name], env)
    obs, _ = env.reset(seed=0)
    action, _ = model.predict(obs, deterministic=True)
    env.step(action)


@pytest.mark.parametrize("name, rules", [("free", STRICT), ("strict", RuleConfig())])
def test_model_is_refused_when_rules_differ(saved_models, name, rules):
    with pytest.raises(RulesMismatchError, match="different rules"):
        load_model(saved_models[name], KoiKoiEnv(rules=rules))


def test_model_is_refused_through_wrappers(saved_models):
    with pytest.raises(RulesMismatchError):
        load_model(saved_models["free"], gym.make("KoiKoi-v0", rules=STRICT))


def test_model_without_recorded_rules_is_refused(tmp_path):
    model = PPO("MultiInputPolicy", KoiKoiEnv(), n_steps=8, batch_size=8, n_epochs=1, device="cpu")
    model.save(tmp_path / "unlabelled")
    with pytest.raises(RulesMismatchError, match="no recorded rules"):
        load_model(tmp_path / "unlabelled", KoiKoiEnv())


def test_model_from_another_ruleset_version_is_refused(saved_models, monkeypatch):
    monkeypatch.setattr("holokkrl.game.rules.RULESET_VERSION", "999")
    with pytest.raises(RulesMismatchError):
        load_model(saved_models["free"], KoiKoiEnv())


def test_project_code_saves_and_loads_models_only_through_models_module():
    root = Path(__file__).parents[1]
    unguarded = re.compile(r"\b(model|PPO|MaskablePPO|algo)\.(save|load)\(")
    for path in [*root.joinpath("holokkrl").rglob("*.py"), *root.joinpath("scripts").rglob("*.py")]:
        if path.name != "models.py":
            assert not unguarded.search(path.read_text(encoding="utf-8")), path


def test_recorded_rules_come_from_the_training_env(tmp_path):
    model = PPO("MultiInputPolicy", gym.make("KoiKoi-v0", rules=STRICT), n_steps=8, batch_size=8, n_epochs=1, device="cpu")
    path = save_model(model, tmp_path / "wrapped")
    assert read_model_rules(path)["must_capture_if_able"] is True
