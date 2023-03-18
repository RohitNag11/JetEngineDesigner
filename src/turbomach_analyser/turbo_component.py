from ..utils import thermo as thermo


class TurboComponent:
    def __init__(self,
                 mass_flow,
                 axial_velocity,
                 pressure_ratio,
                 P0_exit,
                 T0_exit,
                 T0_inlet,
                 SPEC_HEAT_RATIO=1.4,
                 GAS_CONST=287,):
        self.__SPEC_HEAT_RATIO = SPEC_HEAT_RATIO
        self.__GAS_CONST = GAS_CONST
        self.mass_flow = mass_flow
        self.axial_velocity = axial_velocity
        self.pressure_ratio = pressure_ratio

        self.T0_inlet = T0_inlet
        self.T0_exit = T0_exit

        self.P0_exit = P0_exit
        self.P0_inlet = P0_exit / pressure_ratio

        self.stag_density_exit = thermo.get_stag_density(self.P0_exit,
                                                         self.T0_exit,
                                                         self.__GAS_CONST,)
        self.stag_density_inlet = thermo.get_stag_density(self.P0_inlet,
                                                          self.T0_inlet,
                                                          self.__GAS_CONST)

        # NOTE: Static temp here is higher than the stagnation temp
        static_temp_exit = thermo.get_static_temp(
            self.T0_exit, self.axial_velocity, self.__SPEC_HEAT_RATIO, self.__GAS_CONST)
        static_temp_inlet = thermo.get_static_temp(
            self.T0_inlet, self.axial_velocity, self.__SPEC_HEAT_RATIO, self.__GAS_CONST)
        self.axial_mach_no_exit = thermo.get_mach_no_from_velocity(
            self.axial_velocity, static_temp_exit, self.__SPEC_HEAT_RATIO, self.__GAS_CONST)
        self.axial_mach_no_inlet = thermo.get_mach_no_from_velocity(
            self.axial_velocity, static_temp_inlet, self.__SPEC_HEAT_RATIO, self.__GAS_CONST)

        self.density_exit = thermo.get_static_density(self.stag_density_exit,
                                                      self.axial_mach_no_exit,
                                                      self.__SPEC_HEAT_RATIO)
        self.density_inlet = thermo.get_static_density(self.stag_density_inlet,
                                                       self.axial_mach_no_inlet,
                                                       self.__SPEC_HEAT_RATIO)

        self.area_exit = self.mass_flow / \
            (self.density_exit * self.axial_velocity)
        self.area_inlet = self.mass_flow / \
            (self.density_inlet * self.axial_velocity)
