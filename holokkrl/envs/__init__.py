import gymnasium as gym

gym.register(
    id="KoiKoi-v0",
    entry_point="holokkrl.envs.koikoi_env:KoiKoiEnv",
)
