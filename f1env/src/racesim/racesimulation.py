import pandas as pd
import numpy as np

from racesim.config import Config

from racesim.drivermodetype import PitStopMode
from racesim.drivermodetype import RaceMode

from racesim.overtake import OvertakeModel

class RaceSimulation:
    def __init__(self, config: Config, driver_being_controlled, control_driver=True,
                 randomness=0) -> None:

        self.config = config
        self.rand_generator = self.config.rand_generator

        self.driver_controlled_id = driver_being_controlled
        self.control_driver = control_driver
        self.randomness=randomness

        self.reset()

    def reset(self):
        self.current_race_params = self.config.get_circuit_config()

        self.n_drivers = self.current_race_params.n_drivers
        self.n_laps = self.current_race_params.n_laps

        self.pitstop_time = self.current_race_params.pit["pitstop_time"]
        self.pitstop_percentage_entry = self.current_race_params.pit["pit_entry"]
        self.pitstop_percentage_end = self.current_race_params.pit["pit_exit"]
        self.max_stops = self.current_race_params.pit["max_stops"]
        self.drivers = self.current_race_params.get_drivers(randomness=self.randomness)
        self.drivers_for_obs = sorted(self.drivers, key=lambda x: x.identifier)

        self.overtake_model = OvertakeModel(self.rand_generator,
                                            self.drivers,
                                            self.current_race_params.overtake_chance)


        self.driver_being_controlled = self.get_driver_by_id(self.driver_controlled_id)

        list(map(lambda x:
                 x.fit_start_tyre()
                 if (x is not self.driver_being_controlled or not self.control_driver)
                 else
                 self.driver_being_controlled
                 .fit_start_tyre(self.driver_being_controlled.strategy.get_start_tyre()),
                 self.drivers))
        list(map(lambda x:x.add_mode(RaceMode(x)), self.drivers))

        if self.control_driver:
            self.driver_being_controlled.strategy = None
            self.driver_being_controlled.pitstops = []
            self.driver_being_controlled.next_pitstop = None
            self.simulate_timestep(0)

    def simulate_timestep(self, action):

        if self.has_ended():
            raise RaceEndedException()

        if action == 0 or not self.control_driver:
            pass
        else:
            new_tyre = self.current_race_params.tyre_types[action-1].get_tyre()
            self.driver_being_controlled.pit(new_tyre)
            pitstopmode = PitStopMode(self.driver_being_controlled, self.pitstop_time)
            self.driver_being_controlled.add_mode(pitstopmode)

        while not self.has_ended():

            new_timestep = False

            time_to_elapse = self.get_min_timestep()

            self.drivers.sort(key=lambda x: (x.is_in_pits, x.laps_to_go,
                                           -x.percentage_of_lap_completed, x.time))

            for i, driver in enumerate(self.drivers):
                driver.position = i+1

            for driver in self.drivers:

                is_being_controlled = self.control_driver and (
                    driver.identifier == self.driver_being_controlled.identifier)
                driver_ended = driver.laps_to_go == 0

                if driver_ended:
                    continue

                is_close_to_pit_entry = self.advance_time(driver, time_to_elapse)

                if (is_being_controlled and
                            is_close_to_pit_entry and
                                not driver.has_crossed_pit_entry):
                    driver.has_crossed_pit_entry = True
                    if driver.laps_to_go > 1:
                        new_timestep = True
                    continue

                if is_close_to_pit_entry and not driver.has_crossed_pit_entry:
                    #decision to be made. Stop or not?
                    driver.has_crossed_pit_entry = True

                    next_pitstop = driver.next_pitstop

                    if next_pitstop is not None:
                        if (self.n_laps - driver.laps_to_go + 1) == next_pitstop.lap_number:
                            driver.pit(next_pitstop.tyre.get_tyre())
                            pitstopmode = PitStopMode(driver, self.pitstop_time)
                            driver.add_mode(pitstopmode)

            self.recalculate_intervals()

            if new_timestep:
                return

        self.end_race()

    def advance_time(self, driver, time_to_elapse):

        if driver.laps_to_go == 0:
            return False

        driver.advance_time(time_to_elapse, self.overtake_model)

        return driver.percentage_of_lap_completed == self.pitstop_percentage_entry


    def get_min_timestep(self):
        """
        Get the minimum timestep to advance the simulation

        _extended_summary_

        Returns:
            _description_
        """

        timesteps = [driver.get_min_timestep() for driver in self.drivers]
        return min(timesteps)

        #return min(driver.get_min_timestep() for driver in self.drivers)

    def recalculate_intervals(self):
        """
        recalculate_intervals Recalculates the intervals between drivers

        Recalculates the intervals between drivers
        """

        self.drivers.sort(key=lambda x: (x.laps_to_go, -x.percentage_of_lap_completed, x.time))
        gap = 0

        for i in range(self.n_drivers):

            driver = self.drivers[i]

            driver.position = i+1

            if i == 0:
                driver.interval = 0
                driver.gap = 0
                continue

            new_interval = driver.interval
            driver_ahead = self.drivers[i-1]

            if driver.laps_to_go > 0:

                if driver.percentage_of_lap_completed > 0:
                    index_diff = 1
                else:
                    index_diff = 0

                last_lap_progress = driver.laps_progress[driver.laps_to_go-index_diff][-1]

                last_lap_progresses_ahead = driver_ahead.laps_progress[driver.laps_to_go-index_diff]

                for lp in last_lap_progresses_ahead:
                    if lp.upper_limit >= last_lap_progress.upper_limit:

                        diff_percentage = lp.upper_limit - last_lap_progress.upper_limit
                        time_diff = round(diff_percentage * lp.potential_lap_time, 10)

                        new_interval = (last_lap_progress.time_at_upper_limit
                                        -(lp.time_at_upper_limit-time_diff))
                        break
            else:
                new_interval = driver.time - driver_ahead.time

            if new_interval < 0:
                raise NegativeIntervalException()

            driver.interval = new_interval
            gap += new_interval
            driver.gap = gap

    def get_driver_by_id(self, identifier):
        """
        get_driver_by_id Gets the driver with the given identifier

        Get the driver with the given identifier

        Arguments:
            identifier -- Identifier of the driver

        Returns:
            Driver with the given identifier
        """
        for driver in self.drivers:
            if driver.identifier == identifier:
                return driver
        return None

    def has_ended(self):
        """
        Check if the current race simulation has ended

        A race has ended if for each driver, the number of laps to go is 0

        Returns:
            True if the race ended, False otherwise
        """
        return self.drivers[-1].laps_to_go == 0

    def end_race(self):
        """
        At the end of the race, it is checked if any driver has not fitted the second dry tyre
        If they hasn't, their time is set to infinity (equals to disqualified)
        """
        dq_time = self.drivers[-1].time + 1
        for driver in self.drivers:
            if not driver.second_dry:
                driver.time = dq_time
        self.recalculate_intervals()


    def to_df(self):
        """
        Returns a pandas dataframe with the current state of the simulation

        Returns:
            pd.DataFrame: A pandas dataframe with the current state of the simulation
        """
        return pd.DataFrame([driver.__dict__() for driver in self.drivers])

    def to_gym_observation(self):
        """
        Gets the gym observation of the current state of the simulation

        Returns:
            obs: A numpy array with the current state of the simulation
        """

        obs = np.array([driver.to_obs() for driver in self.drivers_for_obs])

        #normalize interval with plt of each driver, 1 if is one lap behind or slower than ahead
        obs[:,0] = np.minimum(obs[:,0]/obs[:,4], 1)
        #normalize laps to go with total number of laps
        obs[:,1] /= self.n_laps
        #normalize lap time
        obs[:, 2] = (obs[:,2]/np.max(obs[:, 2]))
        #normalize position
        obs[:,3] = (obs[:,3]-1)/(self.n_drivers-1)
        #normalize potential lap time
        obs[:, 4] = (obs[:,4]/np.max(obs[:, 4]))
        #normalize used laps
        obs[:,5] /= self.n_laps
        #normalize number of stops
        obs[:,7] = np.where(obs[:,7] >= self.max_stops, 1, obs[:,7]/self.max_stops)

        return obs.flatten()

class RaceEndedException(Exception):
    """
    Exception raised when race has been ended and an action is trying to be performed

    Arguments:
        Exception -- Base exception class
    """
    def __init__(self) -> None:
        super().__init__("Race has ended")

class NegativeIntervalException(Exception):
    """
    Exception raised when a calculated interval is negative

    Arguments:
        Exception -- Base exception class
    """
    def __init__(self) -> None:
        super().__init__("Interval is negative")
