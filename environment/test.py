import gymnasium as gym
from environment.koikoienv import KoiKoiEnv
import numpy as np

env = KoiKoiEnv()
num_episodes = 5

for ep in range(num_episodes):
    print(f"Episode: {ep} running.")
    obs, info = env.reset()
    done = False
    truncated = False
    total_reward = 0
    step_count = 0

    while not done and not truncated:
        # Random action
        action = env.action_space.sample()
        obs, reward, terminated, truncated, info = env.step(action)
        total_reward += reward
        step_count += 1

    print(f"Episode {ep+1}: Steps={step_count}, Total Reward={total_reward}, Info={info}")
