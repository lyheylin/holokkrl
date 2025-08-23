import gymnasium as gym
import environment 
from stable_baselines3 import PPO

gym.register(
    id="KoiKoi-v0",
    entry_point="environment.koikoienv:KoiKoiEnv",
)

# Create the env
env = gym.make("KoiKoi-v0", max_rounds=3)

# Create the agent
model = PPO("MultiInputPolicy", env, verbose=1)

# Train for some timesteps
model.learn(total_timesteps=10000)

# Save the model
model.save("ppo_koikoi")

# Test the trained agent
obs, info = env.reset()
done = False
truncated = False
while not (done or truncated):
    action, _states = model.predict(obs, deterministic=True)
    obs, reward, done, truncated, info = env.step(action)
    env.render()
