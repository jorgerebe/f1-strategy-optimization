import pytest

from racesim.fuel import Fuel

class TestConstructor(object):

    def test_valid_arguments(self):
        fuel = Fuel(10, 1, 0.1)
        assert fuel.fuel_mass == 10
        assert fuel.mass_effect == 1
        assert fuel.consumption_per_lap == 0.1
        assert fuel.consumed_laps == 0


class TestConsumeFuel(object):

    def test_consume_fuel(self, fuel_fixture):
        #Arrange, #Act
        fuel_fixture.consume_fuel()
        #Assert
        assert fuel_fixture.consumed_laps == 1

class TestGetLapTimeEffect(object):

    def test_get_lap_time_effect(self, fuel_fixture):
        #Arrange, #Act
        lap_time_effect = fuel_fixture.get_lap_time_effect(1)
        #Assert
        assert lap_time_effect == 9.9
