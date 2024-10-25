"""
    _summary_

_extended_summary_
"""

from  dataclasses import dataclass

from queue import PriorityQueue

import numpy as np

from racesim.drivermodetype import DriverState

class Driver:
    """
     _summary_

    _extended_summary_
    """

    def __init__(self, identifier, strategy, fuel, n_laps, position, interval, pit) -> None:

        self.identifier = identifier
        self.pit_entry = pit["pit_entry"]
        self.pit_exit = pit["pit_exit"]
        self.n_tyres = pit["n_tyres"]
        self.max_stops = pit["max_stops"]

        self.percentage_of_lap_completed = 0
        self.has_crossed_pit_entry = False
        self.second_dry = False
        self.next_pitstop = None
        self.tyre = None
        self.is_in_first_lap = True
        self.last_lap_time = 1
        self.current_lap_time = 0
        self.gap = 0
        self.n_stops = 0

        self.reset(strategy, fuel, n_laps, position, interval)

    def advance_time(self, time, overtake_model):

        if time == 0:
            raise AdvanceTimeZeroException()

        if self.laps_to_go == 0:
            raise RaceAlreadyEndedException()

        mode = self.get_mode(0)

        if mode is None:
            raise NoModeToAdvanceException()

        self.get_mode(0).drive(time, overtake_model)

    def end_lap(self):

        if self.laps_to_go == 0:
            raise RaceAlreadyEndedException()

        self.percentage_of_lap_completed = 0
        self.has_crossed_pit_entry = False
        self.laps_to_go -= 1
        self.last_lap_time = self.current_lap_time
        self.current_lap_time = 0
        self.is_in_first_lap = False

    def degrade_tyre(self):
        self.tyre.degrade()

    def consume_fuel(self):
        self.fuel.consume_fuel()

    def get_time_to_pits(self):
        return self.get_mode(0).get_time_to_percentage(self.pit_entry)

    def get_time_to_next_lap(self):
        return self.get_mode(0).get_time_to_percentage(1)

    def get_time_to_pit_exit(self):
        return self.get_mode(0).get_time_to_percentage(self.pit_exit)

    def get_potential_lap_time(self, tyre_lap=0, fuel_lap=0):

        tyre_lap = self.tyre.used_laps + tyre_lap
        fuel_lap = self.fuel.consumed_laps + fuel_lap

        return self.tyre.get_lap_time(tyre_lap) + self.fuel.get_lap_time_effect(fuel_lap)

    def fit_start_tyre(self, tyre=None):

        if self.strategy is None and tyre is None:
            raise ValueError("Cannot fit start tyre without strategy or tyre")

        if self.time > 0:
            raise ValueError("Cannot fit start tyre after race has started")

        if tyre is not None:
            self.tyre = tyre
        else:
            self.tyre = self.strategy.get_start_tyre()

        time_to_leader = -self.interval*(self.position-1)
        self.gap = -time_to_leader
        self.percentage_of_lap_completed = time_to_leader/self.get_potential_lap_time()

    def get_next_pitstop(self):
        if self.pitstop_index < len(self.pitstops):
            return self.pitstops[self.pitstop_index]
        return None

    def pit(self, tyre):
        #as there are typically two mandatory tyres for the race,
        #when the driver pits and the new compound is not the same
        #as the current one, then the driver is complying with
        #the two dry tyre rule
        if self.tyre.compound != tyre.compound:
            self.second_dry = True
        self.tyre = tyre
        self.pitstop_index += 1
        self.next_pitstop = self.get_next_pitstop()
        self.n_stops += 1


    def get_min_timestep(self):
        """
        Get the minimum timestep to advance the simulation

        _extended_summary_

        Returns:
            _description_
        """

        if self.laps_to_go == 0:
            min_timestep = float('inf')
        elif self.laps_to_go == 1:
            min_timestep = self.get_time_to_next_lap()
        elif self.is_in_pits:
            min_timestep = self.get_time_to_pit_exit()
        else:
            min_timestep = self.get_time_to_pits()

        return min_timestep

    def add_lap_progress(self, lap, lower_limit, lower_limit_time,
                         upper_limit, upper_limit_time, potential_lap_time):
        lower_limit = round(lower_limit, 10)
        lower_limit_time = round(lower_limit_time, 10)
        upper_limit = round(upper_limit, 10)
        upper_limit_time = round(upper_limit_time, 10)
        lap_progress = LapProgress(lower_limit, lower_limit_time,
                        upper_limit, upper_limit_time, potential_lap_time)

        self.laps_progress[lap].append(lap_progress)


    def add_mode(self, mode: DriverState):
        self.modes.put((mode.priority, mode))

    def get_mode(self, n=0):
        if self.modes.empty() or len(self.modes.queue) < n+1:
            return None

        return self.modes.queue[n][1]

    def pop_mode(self):
        self.modes.get()


    def reset(self, strategy, fuel, n_laps, position, interval):
        self.strategy = strategy
        self.pitstop_index = 0
        self.n_stops = 0
        self.pitstops = []

        if self.strategy is not None:
            self.pitstops = strategy.get_pitstops()
            self.next_pitstop = self.get_next_pitstop()

        self.fuel = fuel
        self.laps_to_go = n_laps
        self.position = position

        if self.position > 1:
            self.interval = interval
            self.gap = self.interval*(self.position-1)
        else:
            self.interval = 0
            self.gap = 0

        self.has_crossed_pit_entry = False
        self.second_dry = False
        self.is_in_first_lap = True

        self.last_lap_time = 1
        self.current_lap_time = 0
        self.time = 0

        self.is_in_pits = False

        self.tyre = None
        self.percentage_of_lap_completed = 0

        self.modes = PriorityQueue()

        self.laps_progress = np.frompyfunc(list, 0, 1)(np.empty((self.laps_to_go), dtype=object))


    def to_obs(self):

        plt = self.get_potential_lap_time()
        used_laps = self.tyre.used_laps
        last_lap_time = self.last_lap_time
        compound = self.tyre.compound
        one_hot_compound = np.eye(self.n_tyres)[compound]

        return np.concatenate([np.array([self.interval, self.laps_to_go, last_lap_time,
                         self.position, plt, used_laps, self.second_dry, self.n_stops]),
                         one_hot_compound], dtype=np.float32)


    def __dict__(self):

        if self.tyre is None:
            plt = 0
            compound = -1
            used_laps = 0
        else:
            plt = self.get_potential_lap_time()
            compound = self.tyre.compound
            used_laps = self.tyre.used_laps

        return {
            "id": self.identifier,
            "interval": self.interval,
            "percentage": self.percentage_of_lap_completed,
            "gap": self.gap,
            "lapsToGo": self.laps_to_go,
            "lastLapTime": self.last_lap_time,
            "position": self.position,
            "potentialLapTime": plt,
            "compound": compound,
            "usedLaps": used_laps,
            "secondDry": self.second_dry,
            "nStops": self.n_stops
        }


@dataclass
class LapProgress():
    lower_limit: float
    time_at_low_limit: float
    upper_limit: float
    time_at_upper_limit: float
    potential_lap_time: float


class AdvanceTimeZeroException(ValueError):
    """
    Exception raised when driver is trying to drive for zero time

    Arguments:
        ValueError -- Base exception class
    """
    def __init__(self) -> None:
        super().__init__("Time to advance is zero")

class RaceAlreadyEndedException(Exception):
    """
    Exception raised when driver is trying to drive for zero time

    Arguments:
        ValueError -- Base exception class
    """
    def __init__(self) -> None:
        super().__init__("Can't end lap because race for this driver is already finished")



class NoModeToAdvanceException(Exception):
    """
    Exception raised when driver is trying to drive for zero time

    Arguments:
        ValueError -- Base exception class
    """
    def __init__(self) -> None:
        super().__init__("Driver can't advance because she has no race mode available to use")
