import pytest

from racesim.driver import Driver, RaceAlreadyEndedException, AdvanceTimeZeroException, NoModeToAdvanceException

class TestConstructorDriver():

    def test_valid_arguments(self, soft_hard_strategy, pit_info, fuel_fixture, hard_tyre_type):
        #Arrange, Act
        driver = Driver(1, soft_hard_strategy, fuel_fixture, 10, 1, 0.4, pit_info)

        #Assert
        assert driver.identifier == 1
        assert driver.pit_entry == 0.98
        assert driver.pit_exit == 0.02
        assert driver.max_stops == 5

        assert driver.percentage_of_lap_completed == 0
        assert not driver.has_crossed_pit_entry
        assert not driver.second_dry
        assert driver.is_in_first_lap
        assert driver.tyre is None
        assert driver.last_lap_time == 1
        assert driver.current_lap_time == 0

        assert driver.strategy == soft_hard_strategy
        assert driver.pitstop_index == 0
        next_pitstop = driver.next_pitstop
        assert next_pitstop.lap_number == 4
        assert next_pitstop.tyre.type_id == hard_tyre_type.type_id
        assert driver.position == 1
        assert driver.interval == 0
        assert driver.laps_to_go == 10
        assert driver.fuel == fuel_fixture
        assert len(driver.laps_progress) == 10
        assert all(len(lap) == 0 for lap in driver.laps_progress)

        assert driver.modes.qsize() == 0

    def test_valid_no_strategy_second_position(self, pit_info, fuel_fixture):
        #Arrange, Act
        driver = Driver(1, None, fuel_fixture, 10, 2, 0.4, pit_info)

        #Assert
        assert driver.identifier == 1
        assert driver.pit_entry == 0.98
        assert driver.pit_exit == 0.02
        assert driver.max_stops == 5

        assert driver.percentage_of_lap_completed == 0
        assert not driver.has_crossed_pit_entry
        assert not driver.second_dry
        assert driver.is_in_first_lap
        assert driver.tyre is None
        assert driver.last_lap_time == 1
        assert driver.current_lap_time == 0

        assert driver.strategy is None
        assert driver.next_pitstop is None
        assert driver.pitstop_index == 0
        assert driver.position == 2
        assert driver.interval == 0.4
        assert driver.laps_to_go == 10
        assert driver.fuel == fuel_fixture
        assert len(driver.laps_progress) == 10
        assert all(len(lap) == 0 for lap in driver.laps_progress)

        assert driver.modes.qsize() == 0


class TestAdvanceTime():

    def test_advance_zero_should_raise_exception(self,
                                                 get_driver_1,
                                                 overtake_model_no_overtake):

        #Arrange
        overtake_model = overtake_model_no_overtake(get_driver_1)

        #Act
        with pytest.raises(AdvanceTimeZeroException) as excinfo:
            get_driver_1.advance_time(0, overtake_model)

        #Assert
        assert "Time to advance is zero" in str(excinfo.value)

    def test_advance_race_ended_should_raise_exception(self,
                                                       soft_hard_strategy,
                                                       fuel_fixture,
                                                       pit_info,
                                                       overtake_model_no_overtake):

        #Arrange
        driver = Driver(1, soft_hard_strategy, fuel_fixture, 0, 1, 0.4, pit_info)
        overtake_model = overtake_model_no_overtake(driver)

        #Act
        with pytest.raises(RaceAlreadyEndedException) as excinfo:
            driver.advance_time(1, overtake_model)

        #Assert
        assert "Can't end lap because race for " + \
            "this driver is already finished" in str(excinfo.value)


    def test_advance_race_no_mode_should_raise_exception(self,
                                                         get_driver_1,
                                                         overtake_model_no_overtake):

        #Arrange
        overtake_model = overtake_model_no_overtake(get_driver_1)

        #Act
        with pytest.raises(NoModeToAdvanceException) as excinfo:
            get_driver_1.advance_time(1, overtake_model)

        #Assert
        assert "Driver can't advance because she has " + \
            "no race mode available to use" in str(excinfo.value)


    def test_drive_race_not_ended(self, get_driver_1, get_racemode, overtake_model_no_overtake):
        ##Arrange
        get_driver_1.add_mode(get_racemode(get_driver_1))
        overtake_model = overtake_model_no_overtake(get_driver_1)
        get_driver_1.fit_start_tyre()

        #Act
        get_driver_1.advance_time(1, overtake_model)

        #Assert
        assert get_driver_1.time == 1
        assert get_driver_1.current_lap_time == 1

        assert get_driver_1.get_potential_lap_time() == 102.05

        assert get_driver_1.percentage_of_lap_completed == round(0.009799118079372856, 10)


class TestEndLap():

    def test_end_lap_race_ended_should_throw_exception(self,
                                                        get_driver_one_lap_race,
                                                        overtake_model_no_overtake):
        #Arrange
        overtake_model = overtake_model_no_overtake(get_driver_one_lap_race)
        get_driver_one_lap_race.advance_time(102.05, overtake_model)

        #Act
        with pytest.raises(RaceAlreadyEndedException) as excinfo:
            get_driver_one_lap_race.end_lap()

        #Assert
        assert "Can't end lap because race for this "\
                "driver is already finished""" in str(excinfo.value)

    def test_end_lap(self,
                      get_driver_one_lap_race):
        #Arrange, Act
        get_driver_one_lap_race.end_lap()

        #Assert
        assert get_driver_one_lap_race.laps_to_go == 0
        assert get_driver_one_lap_race.has_crossed_pit_entry is False
        assert get_driver_one_lap_race.last_lap_time == 0
        assert get_driver_one_lap_race.current_lap_time == 0
        assert get_driver_one_lap_race.is_in_first_lap is False


class TestDegradeTyre():

    def test_degrade_tyre(self,
                          get_driver_one_lap_race):
        #Arrange, Act
        get_driver_one_lap_race.degrade_tyre()

        #Assert
        assert get_driver_one_lap_race.tyre.used_laps == 1
        assert get_driver_one_lap_race.tyre.get_lap_time(1) == 92.25


class TestConsumeFuel():

    def test_consume_fuel(self,
                          get_driver_one_lap_race):
        #Arrange, Act
        get_driver_one_lap_race.consume_fuel()

        #Assert
        assert get_driver_one_lap_race.fuel.consumed_laps == 1
        assert get_driver_one_lap_race.fuel.get_lap_time_effect(1) == 9.9     


class TestGetTimeToPits():

    def test_get_time_to_pits(self,
                              get_driver_one_lap_race):
        #Arrange, Act
        time_to_pits = get_driver_one_lap_race.get_time_to_pits()

        #Assert
        assert time_to_pits == 100.009



class TestGetTimeToNextLap():

    def test_get_time_to_next_lap(self,
                                  get_driver_one_lap_race):
        #Arrange, Act
        time_to_next_lap = get_driver_one_lap_race.get_time_to_next_lap()

        #Assert
        assert time_to_next_lap == 102.05


class TestGetTimeToPitExit():

    def test_get_time_to_pit_exit(self,
                                  get_driver_one_lap_race):
        #Arrange, Act
        time_to_pit_exit = get_driver_one_lap_race.get_time_to_pit_exit()

        #Assert
        assert time_to_pit_exit == 2.041


class TestGetPotentialLapTime():

    def test_get_time_to_pit_exit(self,
                                  get_driver_one_lap_race):
        #Arrange, Act
        plt = get_driver_one_lap_race.get_potential_lap_time()

        #Assert
        assert plt == 102.05

class TestFitStartTyre():

    def test_fit_start_tyre_no_strategy_no_tyre_should_throw_exception(self,
                                                                       get_driver_without_strategy):
        #Arrange, Act
        with pytest.raises(ValueError) as excinfo:
            get_driver_without_strategy.fit_start_tyre(None)

        #Assert
        assert "Cannot fit start tyre without strategy or tyre" in str(excinfo.value)


    def test_fit_start_tyre_race_started_should_throw_exception(self,
                                                                get_driver_1,
                                                                get_racemode,
                                                                overtake_model_no_overtake):
        #Arrange
        get_driver_1.add_mode(get_racemode(get_driver_1))
        overtake_model = overtake_model_no_overtake(get_driver_1)
        get_driver_1.fit_start_tyre()
        get_driver_1.advance_time(1, overtake_model)

        #Arrange, Act
        with pytest.raises(ValueError) as excinfo:
            get_driver_1.fit_start_tyre(None)

        #Assert
        assert "Cannot fit start tyre after race has started" in str(excinfo.value)

