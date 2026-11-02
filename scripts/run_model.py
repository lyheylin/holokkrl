"""Run a saved model for some matches. The engine's rule flags must match the model's."""

import argparse
import sys

import numpy as np

from holokkrl.envs.koikoi_env import KoiKoiEnv
from holokkrl.game.rules import RuleConfig
from holokkrl.models import RulesMismatchError, load_model


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("model", help="Path to the saved model")
    parser.add_argument("--matches", type=int, default=100, help="Matches to play")
    parser.add_argument("--rounds", type=int, default=3, help="Rounds per match")
    parser.add_argument("--seed", type=int, default=0, help="Seed of the first match")
    parser.add_argument("--must-capture", action="store_true",
                        help="Run with the must_capture_if_able rule (docs/RULES.md section 9)")
    args = parser.parse_args()

    env = KoiKoiEnv(max_rounds=args.rounds, rules=RuleConfig(must_capture_if_able=args.must_capture))
    try:
        model = load_model(args.model, env)
    except RulesMismatchError as error:
        sys.exit(f"Refusing to run: {error}")

    diffs = []
    cut_off = 0
    for match in range(args.matches):
        obs, info = env.reset(seed=args.seed + match)
        terminated = truncated = False
        while not (terminated or truncated):
            action, _states = model.predict(obs, deterministic=True)
            obs, reward, terminated, truncated, info = env.step(action)
        if truncated:
            cut_off += 1
        else:
            diffs.append(env.your_score - env.opponent_score)

    print(f"Matches: {args.matches}, cut off for illegal moves: {cut_off}")
    if diffs:
        diffs = np.array(diffs)
        print(f"Completed matches: won {np.mean(diffs > 0):.1%}, "
              f"points per round {diffs.mean() / args.rounds:+.2f}")


if __name__ == '__main__':
    main()
