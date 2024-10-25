from numpy.random import Generator 

class TyreType:
    def __init__(self, rand_generator, type_id, name,
                 base_lap_time, squared_deg, linear_deg,
                 perf_var, deg_var):
        self.rand_generator = rand_generator
        self.type_id = type_id
        self.name = name
        self.base_lap_time = base_lap_time
        self.squared_deg = squared_deg
        self.linear_deg = linear_deg
        self.perf_var = perf_var
        self.deg_var = deg_var

    def get_tyre(self):
        perf_var = round(self.rand_generator.uniform(-self.perf_var, self.perf_var), 4)
        deg_var = round(self.rand_generator.uniform(-self.deg_var, self.deg_var), 5)
        base_time = round(self.base_lap_time + perf_var, 5)
        squared_deg = round(self.squared_deg + deg_var, 5)
        linear_deg = round(self.linear_deg + deg_var, 5)
        return Tyre(self.type_id, base_time, squared_deg, linear_deg)

class Tyre:
    def __init__(self, compound, base_lap_time, squared_deg, linear_deg):
        self.compound = compound
        self.base_lap_time = base_lap_time

        self.squared_deg = squared_deg
        self.linear_deg = linear_deg

        self.used_laps = 0

    def degrade(self):
        self.used_laps += 1

    def deg_effect(self,used_laps):
        return self.squared_deg*used_laps**2 + self.linear_deg * used_laps

    def get_lap_time(self, used_laps):
        return self.base_lap_time + self.deg_effect(used_laps)

class Strategy:
    def __init__(self, name, start_tyre:TyreType, pitstops, probability):
        self.name = name
        self.start_tyre = start_tyre
        self.pitstops = pitstops
        self.probability = probability

    def get_start_tyre(self):
        return self.start_tyre.get_tyre()

    def get_pitstops(self):
        return [pitstop.get_pitstop() for pitstop in self.pitstops]

class PitStopInfo:
    def __init__(self, rand_generator:Generator, lap_number:int, tyre:TyreType, lap_var:int):
        self.rand_generator = rand_generator
        self.lap_number = lap_number
        self.tyre = tyre
        self.lap_var = lap_var

    def get_pitstop(self):
        return PitStop(self.lap_number+self.rand_generator.integers(-self.lap_var, self.lap_var+1),
                       self.tyre)

class PitStop:
    def __init__(self, lap_number, tyre:TyreType):
        self.lap_number = lap_number
        self.tyre = tyre
