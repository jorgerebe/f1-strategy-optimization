"""
    _summary_

_extended_summary_

Returns:
    _description_
"""

from abc import ABC, abstractmethod

import numpy as np

import gymnasium as gym
from gymnasium.spaces import Discrete, Box

from racesim.racesimulation import RaceSimulation
from racesim.config import Config
from racesim.config import GridConfig

class F1Env(gym.Env):
    """
    F1Env _summary_

    _extended_summary_

    Arguments:
        gym -- _description_
    """

    metadata = {"render_modes": ["human"]}

    def __init__(self, render_mode=None, seed=0, reward_function=None,
                 grid_config:GridConfig=None, control_driver=True, randomness=0) -> None:
        super().__init__()

        if reward_function is None:
            reward_function = RewardFunctionPositionChange()

        self.reward_function = reward_function

        self.control_driver = control_driver
        self.randomness=randomness

        self.t = 0
        #actions of the agent are for the driver with id = n_drivers-1

        rand_gen = np.random.default_rng(seed)

        config = Config(rand_gen, grid_config=grid_config, control_driver=self.control_driver)

        self.n_drivers = config.n_drivers
        self.n_laps = 0
        self.max_laps = config.max_laps

        self.driver_to_control = config.driver_being_controlled_id
        self.race_simulation = RaceSimulation(config,
                                              driver_being_controlled=self.driver_to_control,
                                              control_driver=self.control_driver,
                                              randomness=self.randomness)

        self.our_driver = None
        self.last_position = -1
        self.start_position = -1
        self.n_stops = 0

        features_per_driver = 11

        # Define the low and high values for each field
        low = np.zeros((self.n_drivers,features_per_driver),
                       dtype=np.float32)

        high = np.full((self.n_drivers,features_per_driver),
                       1, dtype=np.float32)

        # low_race_state = np.array([0], dtype=np.float32)
        # high_race_state = np.array([1], dtype=np.float32)

        # driver_info = Box(low=np.append(low.flatten(), low_race_state),
        #                   high=np.append(high.flatten(), high_race_state),
        #                   shape=(self.n_drivers*features_per_driver+1,), dtype=np.float32)

        driver_info = Box(low = low.flatten(),
                          high = high.flatten(),
                          shape=(self.n_drivers*features_per_driver,), dtype=np.float32)

        self.observation_space = driver_info

        #action space of size 4 (no stop, soft tyre, medium tyre, hard tyre)
        self.action_space = Discrete(4)


        assert render_mode is None or render_mode in self.metadata["render_modes"]
        self.render_mode = render_mode

    def _get_obs(self):
        return self.race_simulation.to_gym_observation()


    def _get_info(self):
        return {}


    def reset(self, *, seed=None, options=None):
        """
        reset _summary_

        _extended_summary_

        Keyword Arguments:
            seed -- _description_ (default: {None})
            options -- _description_ (default: {None})

        Returns:
            _description_
        """

        super().reset(seed=seed, options=options)

        self.race_simulation.reset()

        self.our_driver = self.race_simulation.get_driver_by_id(self.driver_to_control)
        self.n_laps = self.race_simulation.n_laps
        self.start_position = self.our_driver.position
        self.last_position = self.our_driver.position
        self.t = 0
        self.n_stops = 0

        observation = self._get_obs()
        info = self._get_info()

        return observation, info

    def render(self):
        if self.render_mode == "human":
            return self.race_simulation.to_df()


    def step(self, action):

        terminated = False
        truncated = False

        self.race_simulation.simulate_timestep(action)

        self.t+=1

        reward = self.reward_function.compute_reward(self)

        #if the agent pits too many times, negative reward
        if action > 0:
            self.n_stops += 1
            if self.n_stops >= 5:
                reward -= 1

        self.last_position = self.our_driver.position

        if self.race_simulation.has_ended():
            if not self.our_driver.second_dry:
                reward -= 1
            terminated = True

        return self._get_obs(), reward, terminated, truncated, {}

class RewardFunction(ABC):
    @abstractmethod
    def compute_reward(self, env):
        pass

class RewardFunctionPositionChange(RewardFunction):
    def compute_reward(self, env):
        return env.last_position - env.our_driver.position


class RewardFunctionPositionChangeByLapsToGo(RewardFunction):
    def compute_reward(self, env):
        return (env.last_position - env.our_driver.position)*(env.t/env.n_laps)

class RewardFunctionPerPositionAtFinalLap(RewardFunction):

    position_to_reward = {
        1:  15,
        2:  13.5,
        3:  12.25,
        4:  11.0,
        5:  9.75,
        6:  8.75,
        7:  8.0,
        8:  7.25,
        9:  6.5,
        10: 5.75,
        11: 5.0,
        12: 4.25,
        13: 3.75,
        14: 3.25,
        15: 1.75,
        16: 1.25,
        17: 0.75,
        18: 0.5,
        19: 0.25,
        20: 0
    }

    def compute_reward(self, env):
        if env.race_simulation.has_ended():
            return self.position_to_reward[env.our_driver.position]
        return 0


class RewardFunctionPerPositionAtFinalLapEval(RewardFunction):

    def compute_reward(self, env):
        if env.race_simulation.has_ended():
            return env.our_driver.position
        return 0
