# holokkrl

Goal: train a model that is proficient at winning Koi-Koi. See `README.md` for an overview.

## Where to look

- `docs/RULES.md` is the source of truth for game rules. Look rules up there, not from memory or the web. If code and rules disagree, it's a bug unless the rules are changed on purpose and the changelog updated. Cite rule IDs such as `R6.1` in code and tests where useful.
- The target game is Holo's Hanafuda's Koi-Koi mode. `docs/RULES.md` section 10 has its rules and each one's status, but the engine doesn't run them yet. `docs/HOLOS_HANAFUDA_CHECKLIST.md` holds the recorded results, the evidence log and the open items. Don't treat a checklist item as settled until its result is recorded.
- `docs/HOLOS_HANAFUDA_CARDS.md` maps the game's redrawn cards to card IDs. Identify cards by position, not by their art. The screenshots are in `screenshots/`. When new ones are added, log them, close the open items they settle, and turn score screens into tests.
- `docs/RULES.md` section 11 lists where each rule is set in the code and how to change one. Follow it when changing a rule, and keep it up to date.
- `docs/ENVIRONMENT.md` covers actions, observations and rewards. Update it when the interface changes.
- `docs/ROADMAP.md` has the plan and exit criteria. Update it when a phase changes or a baseline is re-measured.

## Commands

The virtualenv is at `~/.venvs/holokkrl`, because `/mnt/e` doesn't allow symlinks. Run from the repo root:

- Tests: `~/.venvs/holokkrl/bin/python -m pytest`
- Smoke run: `~/.venvs/holokkrl/bin/python -m scripts.random_match`

## Conventions

- Save and load models only through `holokkrl/models.py`, so a model can't run under rules it wasn't trained on (R9.2). Never call `model.save()` or `PPO.load()` directly.
- Add rule variations as flags in `holokkrl/game/rules.py`, documented in section 9 of `docs/RULES.md`. Raise `RULESET_VERSION` and the title of `docs/RULES.md` when gameplay changes.
- Judge agents by game points per round and match win rate, never by shaped reward.
- `scripts/train_ppo.py` overwrites `models/ppo_koikoi.zip` by default. Pass `--output` when experimenting.
- Package code goes in `holokkrl/`, runnable entry points in `scripts/`. `models/`, `references/` and the images in `screenshots/` are local and not in git.
- Working files use CRLF, but the repo stores LF. Stage with `git -c core.autocrlf=input add <files>` so commits show only real changes, and use `git diff --ignore-space-at-eol` to review.
