import pytest
from unittest.mock import Mock

import numpy as np

from racesim.overtake import OvertakeModel

from racesim.driver import Driver

from racesim.drivermodetype import RaceMode, PitStopMode

from racesim.tyre import TyreType, Tyre, Strategy, PitStopInfo

from racesim.fuel import Fuel

##RANDOM GENERATOR
@pytest.fixture
def mock_random_generator():
    mock_rnd_gen = Mock(spec=np.random.Generator)
    mock_rnd_gen.uniform.return_value = 0.05
    mock_rnd_gen.integers.return_value = 1
    mock_rnd_gen.random.return_value = 0.1
    return mock_rnd_gen


##FUEL
@pytest.fixture
def fuel_fixture():
    return Fuel(10, 1, 0.1)


##TYRES AND STRATEGIES
@pytest.fixture
def soft_tyre_type(mock_random_generator):
    return TyreType(mock_random_generator, 1,
                        "soft", 90, 0.1, 0.1, 0.1, 0.1)

@pytest.fixture
def hard_tyre_type(mock_random_generator):
    return TyreType(mock_random_generator, 3,
                        "hard", 92, 0.05, 0.05, 0.05, 0.05)

@pytest.fixture
def pit_info():
    return {"pit_entry": 0.98, "pit_exit": 0.02, "n_tyres": 3, "max_stops":5}

@pytest.fixture
def tyre():
    return Tyre(1, 90, 0.1, 0.1)

@pytest.fixture
def soft_hard_strategy(soft_tyre_type, pitstopinfo_soft_to_hard):
    return Strategy("soft-hard", soft_tyre_type, [pitstopinfo_soft_to_hard], 0.1)

@pytest.fixture
def hard_soft_strategy(hard_tyre_type, pitstopinfo_hard_to_soft):
    return Strategy("hard-soft", hard_tyre_type, [pitstopinfo_hard_to_soft], 0.1)


@pytest.fixture
def pitstopinfo_soft_to_hard(mock_random_generator, hard_tyre_type):
    return PitStopInfo(mock_random_generator, 3, hard_tyre_type, 1)

@pytest.fixture
def pitstopinfo_hard_to_soft(mock_random_generator, soft_hard_strategy):
    return PitStopInfo(mock_random_generator, 6, soft_hard_strategy, 1)



##DRIVER

@pytest.fixture
def get_driver_1(hard_soft_strategy, pit_info, fuel_fixture):
    return Driver(1, hard_soft_strategy, fuel_fixture, 10, 1, 0.4, pit_info)


@pytest.fixture
def get_driver_without_strategy(pit_info, fuel_fixture):
    return Driver(1, None, fuel_fixture, 10, 1, 0.4, pit_info)

@pytest.fixture
def get_driver_2(soft_hard_strategy, pit_info, fuel_fixture):
    return Driver(2, soft_hard_strategy, fuel_fixture, 10, 2, 0.4, pit_info)


@pytest.fixture
def get_driver_one_lap_race(hard_soft_strategy, pit_info, fuel_fixture, get_racemode):
    driver = Driver(1, hard_soft_strategy, fuel_fixture, 1, 1, 0.4, pit_info)

    driver.add_mode(get_racemode(driver))

    driver.fit_start_tyre()

    return driver


##DRIVER MODE TYPE

@pytest.fixture
def get_racemode():
    def create_race_mode(driver):
        return RaceMode(driver)
    return create_race_mode

@pytest.fixture
def get_pitstopmode():
    def create_pitstop_mode(driver):
        return PitStopMode(driver, 25)
    return create_pitstop_mode

@pytest.fixture
def get_driver_in_pit_entry(get_driver_1, get_racemode):
    driver = get_driver_1
    driver.fit_start_tyre()
    race_mode = get_racemode(driver)
    driver.add_mode(race_mode)
    overtake_model = OvertakeModel(mock_random_generator, [driver], 0)
    race_mode.drive(100.009, overtake_model)
    return driver


##OVERTAKE
@pytest.fixture
def overtake_model_no_overtake():
    def create_overtake_model(driver):
        return OvertakeModel(mock_random_generator, [driver], 0)
    return create_overtake_model
