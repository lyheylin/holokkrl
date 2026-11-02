# holokkrl

Goal: train a model that is proficient at winning Koi-Koi. See `README.md` for an overview.

## Where to look

- `docs/RULES.md` is the source of truth for game rules. Look rules up there, not from memory or the web. If code and rules disagree, it's a bug unless the rules are changed on purpose and the changelog updated. Cite rule IDs such as `R6.1` in code and tests where useful.
- `docs/ENVIRONMENT.md` covers actions, observations and rewards. Update it when the interface changes.
- `docs/ROADMAP.md` has the plan and exit criteria. Update it when a phase changes or a baseline is re-measured.

## Commands

The virtualenv is at `~/.venvs/holokkrl`, because `/mnt/e` doesn't allow symlinks. Run from the repo root:

- Tests: `~/.venvs/holokkrl/bin/python -m pytest`
- Smoke run: `~/.venvs/holokkrl/bin/python -m scripts.random_match`

## Conventions

- Judge agents by game points per round and match win rate, never by shaped reward.
- `scripts/train_ppo.py` overwrites `models/ppo_koikoi.zip` by default. Pass `--output` when experimenting.
- Package code goes in `holokkrl/`, runnable entry points in `scripts/`. `models/` and `references/` are local and not in git.
- Working files use CRLF, but the repo stores LF. Stage with `git -c core.autocrlf=input add <files>` so commits show only real changes, and use `git diff --ignore-space-at-eol` to review.
