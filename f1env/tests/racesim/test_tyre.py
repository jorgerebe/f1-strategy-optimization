import pytest

from racesim.tyre import TyreType, Tyre, Strategy, PitStopInfo, PitStop


class TestConstructorTyreType(object):

    def test_valid_arguments(self, mock_random_generator):
        soft_type = TyreType(mock_random_generator, 1,
                        "soft", 90, 0.1, 0.1, 0.1, 0.1)

        assert soft_type.rand_generator == mock_random_generator
        assert soft_type.type_id == 1
        assert soft_type.name == "soft"
        assert soft_type.base_lap_time == 90
        assert soft_type.squared_deg == 0.1
        assert soft_type.linear_deg == 0.1
        assert soft_type.perf_var == 0.1
        assert soft_type.deg_var == 0.1

class TestGetTyre():

    def test_get_tyre(self, soft_tyre_type):
        tyre = soft_tyre_type.get_tyre()

        assert tyre.compound == 1
        assert tyre.base_lap_time == 90.05
        assert tyre.squared_deg == 0.15
        assert tyre.linear_deg == 0.15



class TestConstructorTyre():

    def test_valid_arguments(self):
        new_tyre = Tyre(1, 90, 0.1, 0.1)

        assert new_tyre.compound == 1
        assert new_tyre.base_lap_time == 90
        assert new_tyre.squared_deg == 0.1
        assert new_tyre.linear_deg == 0.1
        assert new_tyre.used_laps == 0

class TestDegrade():

    def test_degrade(self, tyre):
        tyre.degrade()

        assert tyre.used_laps == 1

class TestDegEffect():

    def test_deg_effect_new_tyre(self, tyre):
        assert tyre.deg_effect(0) == 0

    def test_deg_effect_used_tyre_one_lap(self, tyre):
        assert tyre.deg_effect(1) == 0.1+0.1

    def test_deg_effect_used_tyre_two_laps(self, tyre):
        assert tyre.deg_effect(2) == 0.2+0.4

class TestGetLapTime():

    def test_get_lap_time_used_tyre_two_laps(self, tyre):
        assert tyre.get_lap_time(2) == 90.6

class TestConstructorStrategy(object):

    def test_valid_arguments_no_pitstops(self, soft_tyre_type):
        strategy = Strategy("soft", soft_tyre_type, [], 0.1)

        assert strategy.name == "soft"
        assert strategy.start_tyre == soft_tyre_type
        assert strategy.pitstops == []
        assert strategy.probability == 0.1

    def test_valid_arguments_with_pitstops(self, soft_tyre_type, pitstopinfo_soft_to_hard):

        strategy = Strategy("soft", soft_tyre_type, [pitstopinfo_soft_to_hard], 0.1)

        assert strategy.name == "soft"
        assert strategy.start_tyre == soft_tyre_type
        assert strategy.pitstops == [pitstopinfo_soft_to_hard]
        assert strategy.probability == 0.1

class TestGetStartTyre():

    def test_get_start_tyre(self, soft_hard_strategy):
        start_tyre = soft_hard_strategy.get_start_tyre()

        assert start_tyre.compound == 1
        assert start_tyre.base_lap_time == 90.05
        assert start_tyre.squared_deg == 0.15
        assert start_tyre.linear_deg == 0.15

class TestGetPitStops():

    def test_get_pitstops(self, soft_hard_strategy, hard_tyre_type):
        pitstops = soft_hard_strategy.get_pitstops()

        assert len(pitstops) == 1
        assert pitstops[0].lap_number == 4
        assert pitstops[0].tyre == hard_tyre_type

class TestConstructorPitStopInfo:

    def test_valid_arguments(self, mock_random_generator, soft_tyre_type):
        pitstop_info = PitStopInfo(mock_random_generator, 10, soft_tyre_type, 1)

        assert pitstop_info.rand_generator == mock_random_generator
        assert pitstop_info.lap_number == 10
        assert pitstop_info.lap_var == 1

class TestGetPitStop:

    def test_get_pitstop(self, pitstopinfo_soft_to_hard):
        pitstop = pitstopinfo_soft_to_hard.get_pitstop()

        assert pitstop.lap_number == 4
        assert pitstop.tyre == pitstopinfo_soft_to_hard.tyre

class TestPitStop:

    def test_valid_arguments(self, soft_tyre_type):
        pitstop = PitStop(10, soft_tyre_type)

        assert pitstop.lap_number == 10
        assert pitstop.tyre == soft_tyre_type
