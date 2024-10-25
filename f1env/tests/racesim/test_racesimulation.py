import pytest

from racesim.racesimulation import RaceSimulation, RaceEndedException

@pytest.fixture
def get_racesim(get_config):
    return RaceSimulation(get_config, 1)
