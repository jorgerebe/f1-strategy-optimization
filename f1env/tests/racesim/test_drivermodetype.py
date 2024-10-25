import pytest

from racesim.drivermodetype import RaceMode, PitStopMode
from racesim.drivermodetype import DriveTimeZeroException, NoOvertakeModelException, DriverNotInPitEntryException

from racesim.driver import Driver

from racesim.overtake import OvertakeModel

class TestConstructorRaceMode(object):

    def test_valid_arguments(self, get_driver_1):
        race_mode = RaceMode(get_driver_1)
        assert race_mode.priority == 2
        assert isinstance(race_mode.driver, Driver)

class TestDriveRaceMode(object):

    def test_exception_drive_zero_time(self, get_driver_1, get_racemode, mock_random_generator):
        #Arrange
        driver = get_driver_1
        driver.fit_start_tyre()
        race_mode = get_racemode(driver)
        driver.add_mode(race_mode)
        overtake_model = OvertakeModel(mock_random_generator, [driver], 0)

        #Act
        with pytest.raises(DriveTimeZeroException) as excinfo:
            race_mode.drive(0, overtake_model)

        #Assert
        assert "Time to drive is zero" in str(excinfo.value)

    def test_exception_drive_overtakemodel_none(self, get_driver_1, get_racemode):
        #Arrange
        driver = get_driver_1
        driver.fit_start_tyre()
        race_mode = get_racemode(driver)
        driver.add_mode(race_mode)

        #Act
        with pytest.raises(NoOvertakeModelException) as excinfo:
            race_mode.drive(1, None)

        #Assert
        assert "No overtake model" in str(excinfo.value)

    def test_drive_until_half_lap(self, get_driver_1, get_racemode, mock_random_generator):
        #Arrange
        driver = get_driver_1
        driver.fit_start_tyre()
        race_mode = get_racemode(driver)
        driver.add_mode(race_mode)
        overtake_model = OvertakeModel(mock_random_generator, [driver], 0)

        #Act
        race_mode.drive(51.025, overtake_model)
        #Assert
        assert driver.percentage_of_lap_completed == 0.5
        assert driver.time == 51.025
        lap_progress = driver.laps_progress[9][-1]
        assert lap_progress.lower_limit == 0
        assert lap_progress.time_at_low_limit == 0
        assert lap_progress.upper_limit == 0.5
        assert lap_progress.time_at_upper_limit == 51.025
        assert lap_progress.potential_lap_time == 102.05


    def test_drive_until_lap_completed(self, get_driver_1, get_racemode, mock_random_generator):
        #Arrange
        driver = get_driver_1
        driver.fit_start_tyre()
        race_mode = get_racemode(driver)
        driver.add_mode(race_mode)
        overtake_model = OvertakeModel(mock_random_generator, [driver], 0)

        #Act
        race_mode.drive(102.05, overtake_model)
        #Assert
        assert driver.percentage_of_lap_completed == 0
        assert driver.laps_to_go == 9
        assert driver.last_lap_time == 102.05
        assert driver.time == 102.05

        assert driver.tyre.used_laps == 1
        assert driver.fuel.consumed_laps == 1

        lap_progress = driver.laps_progress[9][-1]
        assert lap_progress.lower_limit == 0
        assert lap_progress.time_at_low_limit == 0
        assert lap_progress.upper_limit == 1
        assert lap_progress.time_at_upper_limit == 102.05
        assert lap_progress.potential_lap_time == 102.05


    def test_drive_behind_other_driver(self,
                                       get_driver_1,
                                       get_driver_2,
                                       get_racemode,
                                       mock_random_generator):
        #Arrange
        driver_ahead = get_driver_1
        driver_behind = get_driver_2
        driver_ahead.fit_start_tyre()
        driver_behind.fit_start_tyre()

        race_mode_ahead = get_racemode(driver_ahead)
        driver_ahead.add_mode(race_mode_ahead)

        race_mode_behind = get_racemode(driver_behind)
        driver_behind.add_mode(race_mode_behind)

        overtake_model = OvertakeModel(mock_random_generator, [driver_ahead, driver_behind], 0)

        #Act
        race_mode_ahead.drive(51.025, overtake_model)
        race_mode_behind.drive(51.025, overtake_model)

        #Assert

        lap_progress_ahead = driver_ahead.laps_progress[9][-1]
        assert lap_progress_ahead.lower_limit == 0
        assert lap_progress_ahead.time_at_low_limit == 0
        assert lap_progress_ahead.upper_limit == 0.5
        assert lap_progress_ahead.time_at_upper_limit == 51.025
        assert lap_progress_ahead.potential_lap_time == 102.05

        lap_progress_behind = driver_behind.laps_progress[9][-1]
        assert lap_progress_behind.lower_limit == -0.003998001
        assert lap_progress_behind.time_at_low_limit == 0
        assert lap_progress_behind.upper_limit == 0.4970014992
        assert lap_progress_behind.time_at_upper_limit == 51.025
        assert lap_progress_behind.potential_lap_time == 101.8464089877

class TestGetTimeToPercentageRaceMode(object):

    def test_exception_get_time_to_percentage_negative(self, get_driver_1, get_racemode):
        #Arrange
        driver = get_driver_1
        driver.fit_start_tyre()
        race_mode = get_racemode(driver)
        driver.add_mode(race_mode)

        #Act
        with pytest.raises(ValueError) as excinfo:
            race_mode.get_time_to_percentage(-0.1)

        #Assert
        message ="Target percentage must be greater than or equal to 0 and less than or equal to 1"
        assert message in str(excinfo.value)

    def test_exception_get_time_to_percentage_greater_than_one(self, get_driver_1, get_racemode):
        #Arrange
        driver = get_driver_1
        driver.fit_start_tyre()
        race_mode = get_racemode(driver)
        driver.add_mode(race_mode)

        #Act
        with pytest.raises(ValueError) as excinfo:
            race_mode.get_time_to_percentage(1.1)

        #Assert
        message ="Target percentage must be greater than or equal to 0 and less than or equal to 1"
        assert message in str(excinfo.value)

    def test_get_time_to_percentage_equal_current_next_lap(self, get_driver_1, get_racemode):
        #Arrange
        driver = get_driver_1
        driver.fit_start_tyre()
        race_mode = get_racemode(driver)
        driver.add_mode(race_mode)

        #Act
        time_to_zero_percentage = race_mode.get_time_to_percentage(0)

        #Assert
        assert time_to_zero_percentage == 102.05


    def test_get_time_to_percentage_to_half_lap(self, get_driver_1, get_racemode):
        #Arrange
        driver = get_driver_1
        driver.fit_start_tyre()
        race_mode = get_racemode(driver)
        driver.add_mode(race_mode)

        #Act
        time = race_mode.get_time_to_percentage(0.5)

        #Assert
        assert time == 51.025

    def test_get_time_to_percentage_next_lap(self,
                                             get_driver_1,
                                             get_racemode,
                                             mock_random_generator):
        #Arrange
        driver = get_driver_1
        driver.fit_start_tyre()
        race_mode = get_racemode(driver)
        driver.add_mode(race_mode)
        overtake_model = OvertakeModel(mock_random_generator, [driver], 0)
        race_mode.drive(51.025, overtake_model)

        #Act
        time = race_mode.get_time_to_percentage(0.1)

        #Assert
        assert time == 61.24


class TestConstructorPitStopMode():

    def test_exception_total_pit_time_equals_zero(self, get_driver_in_pit_entry):
        #Arrange, Act
        with pytest.raises(ValueError) as excinfo:
            PitStopMode(get_driver_in_pit_entry, 0)
        #Assert
        assert "Total time must be greater than 0" in str(excinfo.value)

    def test_exception_driver_not_in_pit_entry(self, get_driver_1, get_racemode):
        #Arrange
        driver = get_driver_1
        driver.fit_start_tyre
        race_mode = get_racemode(driver)
        driver.add_mode(race_mode)
        #Act
        with pytest.raises(DriverNotInPitEntryException) as excinfo:
            PitStopMode(driver, 20)
        #Assert
        assert "Driver is not in pit entry" in str(excinfo.value)

    def test_valid_arguments(self, get_driver_in_pit_entry):
        #Arrange, Act
        driver = get_driver_in_pit_entry
        pitstop_mode = PitStopMode(driver, 20)

        #Assert
        assert driver.percentage_of_lap_completed == driver.pit_entry
        assert pitstop_mode.priority == 1
        assert isinstance(pitstop_mode.driver, Driver)
        assert pitstop_mode.total_time == 20
        assert pitstop_mode.percentage_left == 0.04
        assert pitstop_mode.plt == 500
        assert driver.is_in_pits == True

class TestDrivePitStopMode():

    def test_exception_drive_zero_time(self,
                                       get_driver_in_pit_entry,
                                       mock_random_generator,
                                       get_pitstopmode):
        #Arrange
        driver = get_driver_in_pit_entry
        overtake_model = OvertakeModel(mock_random_generator, [driver], 0)
        pitstop_mode = get_pitstopmode(driver)
        driver.add_mode(pitstop_mode)

        #Act
        with pytest.raises(DriveTimeZeroException) as excinfo:
            pitstop_mode.drive(0, overtake_model)

        #Assert
        assert "Time to drive is zero" in str(excinfo.value)

    def test_drive_still_in_pits_same_lap(self,
                                          get_driver_in_pit_entry,
                                          mock_random_generator,
                                          get_pitstopmode):
        #Arrange
        driver = get_driver_in_pit_entry
        overtake_model = OvertakeModel(mock_random_generator, [driver], 0)
        pitstop_mode = get_pitstopmode(driver)
        driver.add_mode(pitstop_mode)

        #Act
        pitstop_mode.drive(6.25, overtake_model)
        #Assert
        assert driver.percentage_of_lap_completed == 0.99
        assert driver.is_in_pits is True

    def test_drive_still_in_pits_newlap(self,
                                        get_driver_in_pit_entry,
                                        mock_random_generator,
                                        get_pitstopmode):
        #Arrange
        driver = get_driver_in_pit_entry
        overtake_model = OvertakeModel(mock_random_generator, [driver], 0)
        pitstop_mode = get_pitstopmode(driver)
        driver.add_mode(pitstop_mode)

        #Act
        pitstop_mode.drive(12.5, overtake_model)
        #Assert
        assert driver.percentage_of_lap_completed == 0
        assert driver.laps_to_go == 9
        assert driver.is_in_pits is True
        assert driver.last_lap_time == 112.509
        assert pitstop_mode.percentage_left == 0.02

    def test_drive_to_pit_exit(self,
                               get_driver_in_pit_entry,
                               mock_random_generator,
                               get_pitstopmode):
        #Arrange
        driver = get_driver_in_pit_entry
        overtake_model = OvertakeModel(mock_random_generator, [driver], 0)
        pitstop_mode = get_pitstopmode(driver)
        driver.add_mode(pitstop_mode)

        #Act
        pitstop_mode.drive(25, overtake_model)
        #Assert
        assert driver.percentage_of_lap_completed == 0.02
        assert driver.is_in_pits is False
        assert driver.get_mode(0).priority == 2

    def test_drive_to_pit_exit_and_more(self,
                                        get_driver_in_pit_entry,
                                        mock_random_generator,
                                        get_pitstopmode):
        #Arrange
        driver = get_driver_in_pit_entry
        overtake_model = OvertakeModel(mock_random_generator, [driver], 0)
        pitstop_mode = get_pitstopmode(driver)
        driver.add_mode(pitstop_mode)

        #Act0.000490436488
        pitstop_mode.drive(30, overtake_model)
        #Assert
        assert driver.percentage_of_lap_completed == 0.0690436488
        assert driver.is_in_pits is False
        assert driver.get_mode(0).priority == 2


class TestGetTimeToPercentagePitStopMode():

    def test_exception_get_time_to_percentage_negative(self,
                                                       get_driver_in_pit_entry,
                                                       get_pitstopmode):
        #Arrange
        driver = get_driver_in_pit_entry
        pitstop_mode = get_pitstopmode(driver)

        #Act
        with pytest.raises(ValueError) as excinfo:
            pitstop_mode.get_time_to_percentage(-0.1)

        #Assert
        message ="Target percentage must be greater than or equal to 0 and less than or equal to 1"
        assert message in str(excinfo.value)

    def test_exception_get_time_to_percentage_greater_than_one(self,
                                                               get_driver_in_pit_entry,
                                                               get_pitstopmode):
        #Arrange
        driver = get_driver_in_pit_entry
        pitstop_mode = get_pitstopmode(driver)

        #Act
        with pytest.raises(ValueError) as excinfo:
            pitstop_mode.get_time_to_percentage(1.1)

        #Assert
        message ="Target percentage must be greater than or equal to 0 and less than or equal to 1"
        assert message in str(excinfo.value)

    def test_get_time_to_percentage_stay_in_pits(self, get_driver_in_pit_entry, get_pitstopmode):
        #Arrange
        driver = get_driver_in_pit_entry
        pitstop_mode = get_pitstopmode(driver)

        #Act
        time_to_zero_percentage = pitstop_mode.get_time_to_percentage(0)

        #Assert
        assert time_to_zero_percentage == 12.5

    def test_get_time_to_percentage_equal_current_next_lap(self,
                                                           get_driver_in_pit_entry,
                                                           get_pitstopmode):
        #Arrange
        driver = get_driver_in_pit_entry
        pitstop_mode = get_pitstopmode(driver)

        #Act
        time_to_zero_percentage = pitstop_mode.get_time_to_percentage(0.98)

        #Assert
        assert time_to_zero_percentage == 122.872
