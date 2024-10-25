"""
    _summary_

_extended_summary_
"""

class Fuel():
    """
    Fuel _summary_

    _extended_summary_
    """
    def __init__(self, fuel_mass, mass_effect, consumption_per_lap) -> None:
        self.fuel_mass = fuel_mass
        self.mass_effect = mass_effect
        self.consumption_per_lap = consumption_per_lap
        self.consumed_laps = 0

    def consume_fuel(self):
        self.consumed_laps += 1

    def get_lap_time_effect(self, laps_consumed):

        fuel_mass = round(self.fuel_mass - self.consumption_per_lap * laps_consumed, 5)

        return self.mass_effect * fuel_mass
