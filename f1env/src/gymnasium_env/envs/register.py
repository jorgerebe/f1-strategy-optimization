from gymnasium.envs.registration import register

def register_envs():
    register(
        id="F1Env/Basic-v0",
        entry_point="gymnasium_env.envs.f1_env:F1Env",
    )
