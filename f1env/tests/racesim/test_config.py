import pytest
from unittest.mock import Mock

import numpy as np

from racesim.config import Config
from racesim.config import RaceParameters

from racesim.tyre import TyreType
from racesim.tyre import Strategy
from racesim.tyre import PitStopInfo

from racesim.fuel import Fuel

from racesim.driver import Driver

def get_min_fuel():
    return Fuel(10, 0.1, 0.1)

@pytest.fixture
def get_raceparameters(mock_random_generator):
    mock_race_parameters = Mock(spec=RaceParameters)
    mock_race_parameters.n_laps = 10
    mock_race_parameters.n_drivers = 1
    mock_race_parameters.start_interval = 0.4
    mock_race_parameters.rand_generator = mock_random_generator
    mock_race_parameters.overtake_chance = 0.1

    pit_info = {"pit_entry": 0.98,"pit_exit": 0.02,"pitstop_time": 24}

    mock_race_parameters.pit = pit_info

    mock_race_parameters.fuel = {"mass_effect": 0.1,"consumption_per_lap_inKg": 1}

    soft_type = TyreType(mock_random_generator, 0, "soft", 90, 0.1, 0.1, 0.02, 0.01)
    hard_type = TyreType(mock_random_generator, 1, "hard", 91.1, 0.01, 0.01, 0.005, 0.0005)

    mock_race_parameters.tyre_types = np.array([soft_type, hard_type])
    mock_race_parameters.tyre_type_to_id = {soft_type: 0, hard_type: 1}

    strategies = [Strategy("soft-hard", soft_type, [PitStopInfo(mock_random_generator, 3, hard_type, 2)], 1)]

    mock_race_parameters.strategies = strategies

    mock_race_parameters.get_min_fuel_to_complete_race.return_value = get_min_fuel()

    driver = Driver(0, strategies[0], get_min_fuel(), 10, 1, 0.4, pit_info)
    driver.fit_start_tyre()

    mock_race_parameters.drivers = [driver]

    def reset_driver(driver):
        driver.reset(strategies[0], get_min_fuel(), 10, 1, 0.4)
        return driver

    mock_race_parameters.get_drivers.return_value = [reset_driver(driver)]
    mock_race_parameters.get_min_fuel_to_complete_race = get_min_fuel()

    return mock_race_parameters

@pytest.fixture
def get_config(mock_random_generator, get_raceparameters):
    mock_config = Mock(spec=Config)

    race_params = get_raceparameters

    mock_config.rand_generator = mock_random_generator
    mock_config.n_drivers = 1
    mock_config.max_laps = 10

    mock_config.circuit_configs = [race_params]

    mock_config.get_circuit_config.return_value = race_params

    return mock_config
