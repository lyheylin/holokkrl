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
python -m harness.test_harness

# Watch one match of random legal moves
python -m environment.test
```

To use the environment in code:

```python
import numpy as np
from environment.koikoienv import KoiKoiEnv

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

`environment/test_with_agent.py` trains the placeholder PPO agent. It writes `ppo_koikoi.zip` to the current directory, replacing any file with that name. An existing `ppo_koikoi.zip` from before the engine fixes won't load.

## Project layout

```
environment/
  card_data.py        The 48-card deck
  card_utils.py       Card lookups, formatting and yaku detection
  koikoienv.py        Game logic, built-in opponent and rewards (KoiKoiEnv)
  test.py             Random-move smoke script
  test_with_agent.py  Placeholder PPO training script
harness/
  test_harness.py     Play in the terminal
tests/
  test_koikoi_env.py  Rules, reward and invariant tests
docs/                 Rules, environment reference and roadmap
```

## Changing the rules

Rule changes start in [docs/RULES.md](docs/RULES.md): update the ruleset and its changelog, then change the code and tests to match. A rules change makes models trained under the old rules obsolete.
