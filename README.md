# holokkrl

A reinforcement learning project with one goal: train a model that is proficient at winning [Koi-Koi](docs/RULES.md), the two-player Japanese card game played with a hanafuda deck.

## Status

**Early stage.** The game engine and its tests are in place, but there is no capable model yet. The included PPO script is a placeholder that doesn't currently learn to play, and the plan to get from here to a strong model is in the [roadmap](docs/ROADMAP.md).

## Documentation

| Document | Use it for |
|---|---|
| [docs/RULES.md](docs/RULES.md) | **The source of truth for game rules** |
| [docs/ENVIRONMENT.md](docs/ENVIRONMENT.md) | Actions, observations, rewards and the built-in opponent |
| [docs/ROADMAP.md](docs/ROADMAP.md) | The phased plan, baselines and the definition of "proficient" |

## Setup

This needs Python 3.12 and [uv](https://docs.astral.sh/uv/). It has been tested on WSL2 only, and installs CPU-only PyTorch.

```bash
uv venv --python 3.12 ~/.venvs/holokkrl
uv pip install --python ~/.venvs/holokkrl -r requirements.txt --index-strategy unsafe-best-match
source ~/.venvs/holokkrl/bin/activate
```

The virtualenv lives outside the repo because the Windows drive mount under WSL (`/mnt/e`) doesn't allow the symlinks it needs.

## Usage

Run these from the repository root:

```bash
# Run the test suite
python -m pytest

# Play in the terminal against the built-in opponent (add --log to write a log file)
python -m scripts.play

# Watch one match of random legal moves
python -m scripts.random_match

# Run the placeholder PPO training (see --help for options)
python -m scripts.train_ppo

# Run a saved model
python -m scripts.run_model models/ppo_koikoi.zip
```

To use the environment in code:

```python
import numpy as np
from holokkrl.envs.koikoi_env import KoiKoiEnv

env = KoiKoiEnv(max_rounds=12)
obs, info = env.reset(seed=0)
rng = np.random.default_rng(0)

terminated = truncated = False
while not (terminated or truncated):
    legal_actions = np.flatnonzero(env.action_masks())
    action = rng.choice(legal_actions)
    obs, reward, terminated, truncated, info = env.step(action)

print(f"You {env.your_score} - Opponent {env.opponent_score}")
```

`scripts.train_ppo` saves to `models/ppo_koikoi.zip` by default, replacing any file already there, and `--output` picks another path. A `ppo_koikoi.zip` from before the engine fixes won't load.

## Rule flags

Koi-Koi rules vary, so some can be switched to match the game you're playing on. For example, `--must-capture` requires playing a capturing card whenever you hold one. It works with all the scripts, and `KoiKoiEnv(rules=RuleConfig(...))` sets it in code. [docs/RULES.md](docs/RULES.md#9-rule-flags) lists the flags.

**A model only runs under the exact rules it was trained on.** `scripts.run_model` and `load_model` refuse a model if the flags don't match:

```bash
python -m scripts.train_ppo --must-capture    # Trained with the flag on
python -m scripts.run_model models/ppo_koikoi.zip --must-capture    # Runs
python -m scripts.run_model models/ppo_koikoi.zip    # Refused
```

Rule-flag checks only apply if you use `save_model` and `load_model` from `holokkrl/models.py`, so don't call `model.save()` or `PPO.load()` directly.

## Project layout

```
holokkrl/              The Python package
  game/
    cards.py           The 48-card deck and card lookups
    yaku.py            Yaku detection
    rules.py           Rule flags
  envs/
    koikoi_env.py      KoiKoiEnv: game flow and built-in opponent
    rewards.py         Reward tables and calculations
  models.py            Saving and loading models with their rules
scripts/               Things you run
  play.py              Play in the terminal
  random_match.py      Random-move smoke test
  train_ppo.py         Placeholder PPO training
  run_model.py         Run a saved model
tests/
  test_cards_yaku.py   Deck and yaku tests
  test_koikoi_env.py   Rules, reward and invariant tests
  test_rule_flags.py   Rule flags and model rule checks
docs/                  Rules, environment reference and roadmap
models/                Trained models (not in git)
references/            Local reference material (not in git)
```

## Changing the rules

Rule changes start in [docs/RULES.md](docs/RULES.md): update the ruleset and its changelog, then change the code and tests to match. A rules change makes models trained under the old rules obsolete.
