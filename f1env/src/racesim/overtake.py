class OvertakeModel():
    def __init__(self, rand_generator, drivers, probabiliy_overtake):
        self.rand_generator = rand_generator
        self.drivers = drivers
        self.probability_overtake = probabiliy_overtake

    def get_percentage_to_advance(self, current, time_to_elapse):
        """
        Given a driver and the time to elapse, calculates the percentage of the lap that the driver
        will advance. If the driver has the potential to overtake the driver ahead, it is
        calculated if the overtake will happen.

        If the overtake doesn't happen, the percentage to advance is adjusted to stay behind.
        Only one overtake may happen at a time.

        Arguments:
            current -- Current driver that has to advance
            time_to_elapse -- Time to advance

        Returns:
            Percentage to advance of the current driver
        """
        ahead = self.get_driver_ahead(current)

        if ahead is not None:
            #if there is a driver ahead of current, we calculate the time needed to
            #catch they up
            time_to_catch_up = self.get_time_to_catch_up(current, ahead)

            if time_to_catch_up < time_to_elapse:
                # Current driver goes faster than driver's ahead, and has potential to overtake
                if self.rand_generator.random() >= (1-self.probability_overtake) and (
                        not current.is_in_first_lap):
                    #overtake of just one car
                    #check if there is a car ahead
                    ahead_ahead = self.get_driver_ahead(ahead)
                    if ahead_ahead is not None:
                        #if there is, check if current driver has the pace of overtaking it.
                        #If it does, stay behind it
                        time_to_catch_up_ahead = self.get_time_to_catch_up(current, ahead_ahead)
                        if time_to_catch_up_ahead < time_to_elapse:
                            #if has potential to overtake also next driver, stay behind
                            time_to_elapse=round((time_to_catch_up+time_to_catch_up_ahead)/2, 10)
                else:
                    time_to_elapse = round(time_to_catch_up - 0.3, 10)

        percentage = self.get_max_percentage(current, time_to_elapse)

        return percentage, ahead


    def get_driver_ahead(self, current):
        """
        Given a driver, gets the driver ahead of they, if any.
        Drivers that are in the pits are not considered to be ahead

        Arguments:
            current -- Current driver

        Returns:
            Driver ahead of current, None if there is not one.
        """
        ahead = None
        ahead_index = current.position-2

        while ahead is None and ahead_index >= 0:
            ahead = self.drivers[ahead_index]

            if ahead.is_in_pits or ahead.laps_to_go == 0:
                ahead = None

            ahead_index -= 1

        return ahead


    def get_time_to_catch_up(self, current, ahead):
        """
        Gets the time needed to catch the driver ahead of the current driver.

        Arguments:
            current -- Current driver
            ahead -- Driver to catch

        Returns:
            Time needed to catch up driver ahead
        """
        diff_laps = current.laps_to_go - ahead.laps_to_go

        current_percentage = current.percentage_of_lap_completed

        #diff percentage is the distance between ahead and current
        diff_percentage = (diff_laps + ahead.percentage_of_lap_completed) - current_percentage

        added_percentage = (current_percentage + diff_percentage) - 1

        if added_percentage >= 1:
            time = round((1-current_percentage) * current.get_potential_lap_time(), 10)
            time += round(added_percentage * current.get_potential_lap_time(1, 1), 10)
        else:
            time = round(diff_percentage * current.get_potential_lap_time(), 10)

        return time

    def get_max_percentage(self, current, time_to_elapse):
        """
        Given a driver and the time to elapse, calculates the maximum percentage of the lap
        """
        percentage_to_advance = round(time_to_elapse/current.get_potential_lap_time(), 10)

        added_percentage = current.percentage_of_lap_completed + percentage_to_advance

        if added_percentage >= 1:
            percentage_until_next = round(1-current.percentage_of_lap_completed, 10)
            time_to_elapse -= round(percentage_until_next * current.get_potential_lap_time(), 10)
            percentage_to_advance = round(
                percentage_until_next + time_to_elapse/current.get_potential_lap_time(1, 1), 10)

        return percentage_to_advance

    def overtake(self, current, ahead):
        """
        Given two drivers, swaps their positions
        """
        current_position_pre = current.position
        ahead_position_pre = ahead.position

        current.position = ahead_position_pre
        ahead.position = current_position_pre

        self.drivers[current.position-1] = current
        self.drivers[ahead.position-1] = ahead
