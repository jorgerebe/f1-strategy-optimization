"""
    _summary_

_extended_summary_
"""

from abc import ABC, abstractmethod

from racesim.overtake import OvertakeModel

class DriverState(ABC):

    """
     _summary_

    _extended_summary_
    """

    def __init__(self, driver) -> None:
        super().__init__()

        self.driver = driver

    @abstractmethod
    def drive(self, time_to_elapse:float, overtake_model:OvertakeModel):
        self.driver.time += time_to_elapse
        self.driver.current_lap_time += time_to_elapse

    @abstractmethod
    def get_time_to_percentage(self, target:float):
        if target < 0 or target > 1:
            raise ValueError("Target percentage must be greater than or equal to 0 " +
                             "and less than or equal to 1")

    def get_advance(self, time_to_elapse:float, overtake_model:OvertakeModel):
        """
        Given the time to elapse, returns 

        Arguments:
            time_to_elapse -- _description_

        Returns:
            _description_
        """
        percentage, ahead = overtake_model.get_percentage_to_advance(self.driver, time_to_elapse)

        if ahead is not None:
            plt = round(time_to_elapse / max(0.0000000001,percentage), 10)
        else:
            plt = self.driver.get_potential_lap_time()

        return percentage, plt

class RaceMode(DriverState):

    """
     _summary_

    _extended_summary_
    """

    def __init__(self, driver) -> None:
        self.priority = 2
        self.driver = driver
        super().__init__(driver)

    def drive(self, time_to_elapse:float, overtake_model:OvertakeModel):
        """
        Advances time for the driver

        Arguments:
            time_to_elapse -- Time to advance
        """

        if time_to_elapse == 0:
            raise DriveTimeZeroException()

        if overtake_model is None:
            raise NoOvertakeModelException()

        percentage = self.driver.percentage_of_lap_completed

        #initially we assume driver has clean air
        has_clean_air = True

        #we get percentage to advance and potential lap time updated,
        #taking other cars ahead into account
        percentage_to_advance, plt = super().get_advance(time_to_elapse, overtake_model)

        #if new plt is greater than the out optimal lap time,
        #then driver has not clean air
        if plt > self.driver.get_potential_lap_time():
            has_clean_air = False

        time = self.driver.time

        if round(percentage + percentage_to_advance, 10) >= 1:
            #driver is going to complete the lap
            time_to_lap_completed = round((1-percentage) * plt, 10)
            #progress is added
            self.driver.add_lap_progress(self.driver.laps_to_go-1, percentage, time,
                                     1, self.driver.time + time_to_lap_completed, plt)

            super().drive(time_to_lap_completed, overtake_model)

            time = self.driver.time

            #lap ended, tyre degrades a lap and fuel is consumed
            self.driver.end_lap()
            self.driver.degrade_tyre()
            self.driver.consume_fuel()

            percentage = self.driver.percentage_of_lap_completed

            #if driver has clean air, we get the potential lap time
            #for the new lap (plt updated with tyre and fuel degradation)
            if has_clean_air:
                plt = self.driver.get_potential_lap_time()

            time_to_elapse = round(time_to_elapse - time_to_lap_completed, 10)

        if time_to_elapse == 0:
            return

        self.driver.percentage_of_lap_completed = round(percentage + (time_to_elapse/plt), 10)

        self.driver.add_lap_progress(self.driver.laps_to_go-1, percentage, time,
                                self.driver.percentage_of_lap_completed, time + time_to_elapse, plt)

        super().drive(time_to_elapse, overtake_model)

    def get_time_to_percentage(self, target:float):
        """
        Calculates time needed to get to a certain percentage of the lap

        Arguments:
            target -- Percentage target

        Returns:
            Time needed to get to the target percentage
        """

        super().get_time_to_percentage(target)

        time = 0
        current_percentage = self.driver.percentage_of_lap_completed

        if current_percentage >= target:
            #if current percentage is greater than or equal to target,
            #means that the target is in the next lap
            percentage_to_go = 1 - current_percentage
            time += percentage_to_go * self.driver.get_potential_lap_time()
            time += target * self.driver.get_potential_lap_time(1, 1)
        else:
            time = (target-current_percentage) * self.driver.get_potential_lap_time()

        return round(time, 10)


class PitStopMode(DriverState):

    """
     _summary_

    _extended_summary_
    """

    def __init__(self, driver, total_time:float) -> None:

        if total_time <= 0:
            raise ValueError("Total time must be greater than 0")

        if driver.percentage_of_lap_completed != driver.pit_entry:
            raise DriverNotInPitEntryException()


        self.priority = 1
        self.driver = driver
        self.total_time = total_time
        self.percentage_left = round((self.driver.pit_exit+1)-self.driver.pit_entry, 10)
        self.plt = round(total_time / self.percentage_left, 10)

        self.driver.is_in_pits = True

        super().__init__(driver)

    def drive(self, time_to_elapse:float, overtake_model:OvertakeModel):

        if time_to_elapse == 0:
            raise DriveTimeZeroException()

        percentage = self.driver.percentage_of_lap_completed

        percentage_to_advance = round(time_to_elapse/self.plt, 10)

        time = self.driver.time

        if percentage + percentage_to_advance >= 1:
            time_to_lap_completed = round((1-percentage) * self.plt, 10)

            self.driver.add_lap_progress(self.driver.laps_to_go-1, percentage, time,
                                     1, time + time_to_lap_completed, self.plt)

            super().drive(time_to_lap_completed, overtake_model)

            time = self.driver.time

            self.driver.end_lap()
            self.driver.consume_fuel()

            percentage = self.driver.percentage_of_lap_completed
            self.percentage_left = self.driver.pit_exit
            time_to_elapse = round(time_to_elapse - time_to_lap_completed, 10)

        if time_to_elapse == 0:
            return

        time_until_exit = round(self.plt * self.percentage_left, 10)

        time_to_advance_in_pits = min(time_to_elapse, time_until_exit)

        percentage_diff = round(time_to_advance_in_pits/self.plt, 10)

        self.percentage_left = round(self.percentage_left - percentage_diff, 10)
        self.driver.percentage_of_lap_completed = round(self.driver.percentage_of_lap_completed +
                                                        percentage_diff, 10)

        self.driver.add_lap_progress(self.driver.laps_to_go-1, percentage, time,
                                     self.driver.percentage_of_lap_completed,
                                     time+time_to_advance_in_pits, self.plt)

        super().drive(time_to_advance_in_pits, overtake_model)

        if self.percentage_left == 0:
            self.on_complete()

            additional_time = round(time_to_elapse - time_until_exit, 10)

            if additional_time > 0:
                self.driver.advance_time(additional_time, overtake_model)

    def on_complete(self):
        self.driver.pop_mode()
        self.driver.is_in_pits = False

    def get_time_to_percentage(self, target:float):

        super().get_time_to_percentage(target)

        time = 0
        current_percentage = self.driver.percentage_of_lap_completed

        #if drivers is gonna be in pits after getting to the target percentage

        diff_percentage = target - current_percentage

        if diff_percentage <= 0:
            diff_percentage += 1

        if diff_percentage < self.percentage_left:
            #if the difference is less than the percentage left to get to the pit exit
            time = diff_percentage * self.plt
            return round(time, 10)

        time = self.percentage_left * self.plt
        current_percentage = self.driver.pit_exit

        time += (target-current_percentage) * self.driver.get_potential_lap_time(0, 1)

        return round(time, 10)

class DriveTimeZeroException(ValueError):
    """
    Exception raised when driver is trying to drive for zero time

    Arguments:
        ValueError -- Base exception class
    """
    def __init__(self) -> None:
        super().__init__("Time to drive is zero")

class NoOvertakeModelException(TypeError):
    """
    Exception raised when driver is using race mode,
    and trying to drive without an overtake model

    Arguments:
        Exception -- Base exception class
    """
    def __init__(self) -> None:
        super().__init__("No overtake model")

class DriverNotInPitEntryException(Exception):
    """
    Exception raised when driver is not in pit entry
    and a pitstop mode is created for hym

    Arguments:
        Exception -- Base exception class
    """
    def __init__(self) -> None:
        super().__init__("Driver is not in pit entry")
