from gymnasium.envs.registration import register

register(
    id="F1Env-v0",
    entry_point="f1env.gymnasium_env.envs.f1_env:F1Env",
)
