from ..utils import (geometry as geom,
                     thermo)


class Fan:
    def __init__(self,
                 engine_diameter,
                 tip_mach_no,
                 hub_tip_ratio,
                 inner_fan_pressure_ratio,
                 outer_fan_pressure_ratio,
                 bypass_ratio,
                 SPEC_HEAT_RATIO=1.4,
                 GAS_CONST=287,
                 TEMP_SEA=288.15):
        self.name = 'Fan'
        self.hub_tip_ratio = hub_tip_ratio
        self.tip_diameter = engine_diameter
        self.hub_diameter = self.hub_tip_ratio * self.tip_diameter
        self.inner_fan_tip_diameter = self.__get_inner_fan_tip_diameter(
            bypass_ratio)
        self.inner_fan_mean_radius = (
            self.inner_fan_tip_diameter + self.hub_diameter) / 4
        self.inner_fan_pressure_ratio = inner_fan_pressure_ratio
        self.outer_fan_pressure_ratio = outer_fan_pressure_ratio
        self.pressure_ratio = inner_fan_pressure_ratio * outer_fan_pressure_ratio
        self.tip_mach_no = tip_mach_no
        self.__SPEC_HEAT_RATIO = SPEC_HEAT_RATIO
        self.__GAS_CONST = GAS_CONST
        self.__TEMP_SEA = TEMP_SEA
        self.angular_velocity = self.__get_angular_velocity()
        self.is_valid = self.__check_validity()

    def __str__(self):
        properties = {f'Fan tip diameter: {self.tip_diameter}',
                      f'Inner Fan tip diameter:{self.inner_fan_tip_diameter}',
                      f'Fan hub diameter:{self.hub_diameter}',
                      f'Inner Fan mean radius:{self.inner_fan_mean_radius}', }
        return self.name + super().__str__() + ':' + '\n' + '\n'.join(properties)

    def __get_angular_velocity(self):
        speed_of_sound = thermo.get_speed_of_sound(
            0.75*self.__TEMP_SEA, self.__SPEC_HEAT_RATIO, self.__GAS_CONST)
        u_tip = speed_of_sound * self.tip_mach_no
        return geom.get_angular_velocity(u_tip, self.tip_diameter)

    def __get_inner_fan_tip_diameter(self, bypass_ratio):
        return self.tip_diameter * ((1 + bypass_ratio * self.hub_tip_ratio**2) / (1 + bypass_ratio))**0.5

    def __check_validity(self):
        # Inner fan pressure ratio should be less than 1.9
        if self.inner_fan_pressure_ratio > 1.9:
            return False
        # Tip mach number should be less than 1.5
        if self.tip_mach_no > 1.3:
            return False
        return True
