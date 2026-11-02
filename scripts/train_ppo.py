"""Placeholder PPO training run. It doesn't use action masking and doesn't yet learn to
play; see docs/ROADMAP.md."""

import argparse
from pathlib import Path

import gymnasium as gym
from stable_baselines3 import PPO

import holokkrl.envs  # noqa: F401  (registers KoiKoi-v0)
from holokkrl.game.rules import RuleConfig
from holokkrl.models import save_model

DEFAULT_OUTPUT = Path(__file__).resolve().parents[1] / "models" / "ppo_koikoi"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--timesteps", type=int, default=10000, help="Training timesteps")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT,
                        help="Where to save the model (replaces any existing file; .zip is added)")
    parser.add_argument("--must-capture", action="store_true",
                        help="Train with the must_capture_if_able rule (docs/RULES.md section 9)")
    args = parser.parse_args()

    env = gym.make("KoiKoi-v0", max_rounds=3, rules=RuleConfig(must_capture_if_able=args.must_capture))

    model = PPO("MultiInputPolicy", env, verbose=1)
    model.learn(total_timesteps=args.timesteps)

    print(f"Saved {save_model(model, args.output)}")

    # Test the trained agent
    obs, info = env.reset()
    done = False
    truncated = False
    while not (done or truncated):
        action, _states = model.predict(obs, deterministic=True)
        obs, reward, done, truncated, info = env.step(action)
        env.render()


if __name__ == '__main__':
    main()
