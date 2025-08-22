import gymnasium as gym
from environment.koikoienv import KoiKoiEnv
import numpy as np

gym.register(
    id="KoiKoi-v0",
    entry_point="environment.koikoienv:KoiKoiEnv",
)

# Then make it
env = gym.make("KoiKoi-v0", max_rounds=3)
obs, info = env.reset()

done = False
truncated = False
step_count = 0

while not done and not truncated:
    # Sample random action
    action = env.action_space.sample()
    
    obs, reward, done, truncated, info = env.step(action)
    step_count += 1
    
    print(f"Step {step_count}: Action={action}, Reward={reward}")
    print(f"Round: {obs['round']+1}, Turn: {obs['turn']}")
    print(f"Your Score: {obs['your_score']}, Opponent Score: {obs['opponent_score']}")
    print(f"Round Over: {info.get('round_over')}, Match Over: {info.get('match_over')}\n")
    
    # Optional: render the state
    env.render()

print(f"Game finished in {step_count} steps.")
print(f"Final Score: You {obs['your_score']} - Opponent {obs['opponent_score']}")
