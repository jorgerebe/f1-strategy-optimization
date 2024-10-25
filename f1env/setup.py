from setuptools import setup

packages = ['gymnasium_env', 'gymnasium_env.envs','racesim']

entry_points = {
    'gymnasium.envs': ['F1Env=gymnasium_env.envs.register:register_envs']
}

setup(
    name="F1Env",
    version="0.0.1",
    install_requires=["gymnasium==0.28.1"],
    package_dir = {'':'src'},
    packages=packages,
    entry_points=entry_points,
    include_package_data=True,
)
