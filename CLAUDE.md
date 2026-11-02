# holokkrl

Goal: train a model that is proficient at winning Koi-Koi. See `README.md` for an overview.

## Where to look

- `docs/RULES.md` is the source of truth for game rules. Look rules up there, not from memory or the web. If code and rules disagree, it's a bug unless the rules are changed on purpose and the changelog updated. Cite rule IDs such as `R6.1` in code and tests where useful.
- `docs/ENVIRONMENT.md` covers actions, observations and rewards. Update it when the interface changes.
- `docs/ROADMAP.md` has the plan and exit criteria. Update it when a phase changes or a baseline is re-measured.

## Commands

The virtualenv is at `~/.venvs/holokkrl`, because `/mnt/e` doesn't allow symlinks. Run from the repo root:

- Tests: `~/.venvs/holokkrl/bin/python -m pytest`
- Smoke run: `~/.venvs/holokkrl/bin/python -m environment.test`

## Conventions

- Judge agents by game points per round and match win rate, never by shaped reward.
- `environment/test_with_agent.py` overwrites `ppo_koikoi.zip` in the current directory. Run it from elsewhere when experimenting.
- Working files use CRLF, but the repo stores LF. Stage with `git -c core.autocrlf=input add <files>` so commits show only real changes, and use `git diff --ignore-space-at-eol` to review. `.gitignore` and `environment/test_with_agent.py` show as modified only because of line endings.
