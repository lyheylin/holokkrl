"""Smoke test: play one match of random legal moves through gym.make."""

import argparse

import gymnasium as gym
import numpy as np

import holokkrl.envs  # noqa: F401  (registers KoiKoi-v0)
from holokkrl.game.rules import RuleConfig


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--must-capture", action="store_true",
                        help="Play with the must_capture_if_able rule (docs/RULES.md section 9)")
    args = parser.parse_args()

    env = gym.make("KoiKoi-v0", max_rounds=3, rules=RuleConfig(must_capture_if_able=args.must_capture))
    obs, info = env.reset()

    done = False
    truncated = False
    step_count = 0

    while not done and not truncated:
        # Sample random legal action
        action = env.action_space.sample(mask=env.unwrapped.action_masks().astype(np.int8))

        obs, reward, done, truncated, info = env.step(action)
        step_count += 1

        print(f"Step {step_count}: Action={action}, Reward={reward}")
        print(f"Round: {obs['round']+1}, Turn: {obs['turn']}")
        print(f"Your Score: {obs['your_score']}, Opponent Score: {obs['opponent_score']}")
        print(f"Round Over: {info.get('round_over')}, Match Over: {info.get('match_over')}\n")

        env.render()

    print(f"Game finished in {step_count} steps.")
    print(f"Final Score: You {obs['your_score']} - Opponent {obs['opponent_score']}")


if __name__ == '__main__':
    main()
