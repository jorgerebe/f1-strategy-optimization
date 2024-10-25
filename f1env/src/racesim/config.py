from abc import ABC, abstractmethod

import json
from pathlib import Path

from copy import deepcopy

import numpy as np

from racesim.tyre import TyreType
from racesim.tyre import Strategy
from racesim.tyre import PitStopInfo
from racesim.fuel import Fuel

from racesim.driver import Driver

class GridConfig(ABC):
    @abstractmethod
    def get_starting_grid_order(self, drivers, rand_generator):
        pass

class GridConfigMixed(GridConfig):
    def get_starting_grid_order(self, drivers, rand_generator):
        drivers_mixed = drivers.copy()
        rand_generator.shuffle(drivers_mixed)
        return drivers_mixed

class GridConfigSortedById(GridConfig):
    def get_starting_grid_order(self, drivers, rand_generator):
        return sorted(drivers, key=lambda x: x.identifier)

class Config():
    def __init__(self, rand_generator, route="./configs/config.json",
                 grid_config:GridConfig=None, control_driver=True):

        route = Path(__file__).parent / route

        self.rand_generator = rand_generator
        if grid_config is None:
            grid_config = GridConfigMixed()

        config = {}

        with open(route, "r", encoding="utf-8") as f:
            data = f.read()
            config = json.loads(data)

        self.n_drivers = config["n_drivers"]
        self.driver_being_controlled_id = config["driver_to_control"]
        self.max_laps = config["max_laps"]

        self.circuit_configs = []

        circuits = config["circuits"]

        for circuit in circuits:
            self.circuit_configs.append(
                RaceParameters(circuit,
                               self.rand_generator,
                               self.n_drivers,
                               self.driver_being_controlled_id,
                               grid_config,
                               control_driver))

    def get_circuit_config(self):
        return self.rand_generator.choice(self.circuit_configs)


class RaceParameters():
    def __init__(self, circuit_config, rand_generator, n_drivers, driver_to_control,
                 grid_config, control_driver):
        parameters = circuit_config["parameters"]

        self.n_laps = parameters["n_laps"]
        self.n_drivers = n_drivers
        self.driver_being_controlled_id = driver_to_control
        self.control_driver = control_driver
        self.grid_config = grid_config
        self.start_interval = parameters["start_interval"]
        self.rand_generator = rand_generator
        base_time = parameters["base_time"]
        self.overtake_chance = parameters["overtake_chance"]
        self.pit = parameters["pit"]
        self.fuel = parameters["fuel"]

        self.tyre_type_to_id = {}

        self.tyre_types = np.empty(shape=len(parameters["tyre_types"]), dtype=object)
        for tyre in parameters["tyre_types"]:
            tyre_type = parameters["tyre_types"][tyre]
            type_id = tyre_type["id"]
            self.tyre_types[type_id] = TyreType(self.rand_generator,
                                                type_id,
                                                tyre,
                                                tyre_type["added_time"] + base_time,
                                                tyre_type["squared_deg"],
                                                tyre_type["linear_deg"],
                                                tyre_type["perf_var"],
                                                tyre_type["deg_var"])

            self.tyre_type_to_id[tyre] = type_id

        #strategies parsing
        strategies = circuit_config["strategies"]
        self.strategies = []

        for strategy in strategies:
            pitstops = [PitStopInfo(self.rand_generator,
                                    pitstop["lap_number"],
                                    self.tyre_types[self.tyre_type_to_id[pitstop["tyre"]]],
                                    pitstop["lap_var"])
                                        for pitstop in strategy["pitStops"]]

            self.strategies.append(Strategy(strategy["name"],
                                            self.tyre_types[self.tyre_type_to_id
                                                            [strategy["start_tyre"]]],
                                            pitstops,
                                            strategy["probability"]))

        self.drivers = [Driver(i, None,
                               self.get_min_fuel_to_complete_race(),
                               self.n_laps, i+1, self.start_interval,
                               self.pit) for i in range(self.n_drivers)]


        self.driver_being_controlled = self.drivers[self.driver_being_controlled_id]

        self.drivers = self.get_drivers()

    def get_drivers(self, randomness=0):
        self.drivers = self.grid_config.get_starting_grid_order(self.drivers, self.rand_generator)

        strategies = self.get_strategies()
        strategy_index = 0

        for position, driver in enumerate(self.drivers, start=1):
            strategy = strategies[strategy_index]
            strategy_index += 1

            if driver is self.driver_being_controlled and not self.control_driver:
                if randomness == 0:
                    pass
                else:
                    if randomness == 1:
                        first_lap_to_pit = self.n_laps//3
                        last_lap_to_pit = (self.n_laps*2)//3
                    elif randomness == 2:
                        first_lap_to_pit = 1
                        last_lap_to_pit = self.n_laps-1
                    strategy = self.get_strategy_with_random_pitstops(strategy,
                                                                      first_lap_to_pit,
                                                                      last_lap_to_pit)

            driver.reset(strategy,
                         self.get_min_fuel_to_complete_race(),
                         self.n_laps,
                         position,
                         self.start_interval)

        return self.drivers.copy()

    def get_strategies(self):
        probabilities = [strategy.probability for strategy in self.strategies]
        strategies = self.rand_generator.choice(self.strategies,
                                                size=self.n_drivers,
                                                p=probabilities)

        return strategies

    def get_strategy_with_random_pitstops(self, strategy, first_lap_to_pit, last_lap_to_pit):

        def get_random_tyre_except_types(exclude_list):

            if len(exclude_list) > 1:
                rand_tyre = self.rand_generator.integers(low=0, high=len(self.tyre_types))
                return self.tyre_types[rand_tyre]

            while True:
                rand_tyre = self.rand_generator.integers(low=0, high=len(self.tyre_types))
                if rand_tyre not in exclude_list:
                    return self.tyre_types[rand_tyre]
                
        strategy = deepcopy(strategy)

        used_tyres = [strategy.start_tyre.type_id]

        pitstops = []

        n_pitstops = self.rand_generator.integers(low=1, high=3+1)

        pit_laps = set()
        while len(pit_laps) < n_pitstops:
            pit_lap = self.rand_generator.integers(first_lap_to_pit, last_lap_to_pit+1)
            pit_laps.add(pit_lap)

        for pit_lap in sorted(pit_laps):
            tyre_type = get_random_tyre_except_types(used_tyres)
            used_tyres.append(tyre_type.type_id)
            pitstops.append(PitStopInfo(self.rand_generator, pit_lap, tyre_type, 0))

        strategy.pitstops = pitstops
        return strategy

    def get_min_fuel_to_complete_race(self):
        return Fuel(self.n_laps*self.fuel["consumption_per_lap_inKg"],
                        self.fuel["mass_effect"],
                        self.fuel["consumption_per_lap_inKg"])

    def get_random_tyre(self):
        return self.rand_generator.choice(self.tyre_types).get_tyre()
