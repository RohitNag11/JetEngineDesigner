import numpy as np
from ..utils import (geometry as geom,
                     thermo)


class Phase:
    def __init__(self, SPEC_HEAT_RATIO, GAS_CONST, DENSITY_SEA, TEMP_SEA, PRESSURE_SEA, **kwargs):
        self.mach_no = kwargs['mach_no'] if 'mach_no' in kwargs else thermo.get_mach_no_from_velocity(
            kwargs['velocity_freestream'], TEMP_SEA, SPEC_HEAT_RATIO, GAS_CONST)
        self.velocity_freestream = kwargs['velocity_freestream'] if 'velocity_freestream' in kwargs else thermo.get_velocity_from_mach_no(
            kwargs['mach_no'], TEMP_SEA, SPEC_HEAT_RATIO, GAS_CONST)
        self.coeff = kwargs['coeff'] if 'coeff' in kwargs else 1
        self.temp_ratio = kwargs['temp_ratio'] if 'temp_ratio' in kwargs else 1
        self.pressure_ratio = kwargs['pressure_ratio'] if 'pressure_ratio' in kwargs else 1
        self.density_ratio = kwargs['density_ratio'] if 'density_ratio' in kwargs else 1

        self.required_thrust = kwargs['required_thrust']
        self.specific_thrust = kwargs['specific_thrust']

        self.temp_freestream = self.__get_param_freestream(
            TEMP_SEA, self.temp_ratio)
        self.pressure_freestream = self.__get_param_freestream(
            PRESSURE_SEA, self.pressure_ratio)
        self.density_freestream = self.__get_param_freestream(
            DENSITY_SEA, self.density_ratio)

        self.mach_no_intake = self.mach_no * self.coeff
        self.temp_intake = self.__get_temp_intake(
            self.temp_freestream, self.mach_no_intake, SPEC_HEAT_RATIO)
        self.pressure_intake = self.__get_pressure_intake(
            self.pressure_freestream, self.mach_no_intake, SPEC_HEAT_RATIO)
        self.density_intake = self.__get_density_intake(
            self.density_freestream, self.mach_no_intake, SPEC_HEAT_RATIO)
        self.velocity_intake = thermo.get_velocity_from_mach_no(
            self.mach_no_intake, self.temp_intake, SPEC_HEAT_RATIO, GAS_CONST)

        if 'diameter' in kwargs:
            self.diameter = kwargs['diameter']
            self.area = geom.get_area_from_diameter(self.diameter)
            self.mass_flow = thermo.get_mass_flow(
                self.area, self.velocity_intake, self.density_intake)
            self.mass_flow_corrected = thermo.get_corrected_mass_flow(
                self.mass_flow, self.pressure_intake, self.temp_intake, PRESSURE_SEA, TEMP_SEA)

        else:
            self.diameter, self.area, self.mass_flow, self.mass_flow_corrected = self.__get_min_engine_size(
                PRESSURE_SEA, TEMP_SEA)

    def __get_param_freestream(self, param_sea, param_ratio):
        return param_sea * param_ratio

    def __get_temp_intake(self, temp_freestream, mach_no_intake, spec_heat_ratio):
        return temp_freestream / (1 + 0.5 * (spec_heat_ratio - 1) * mach_no_intake**2)

    def __get_pressure_intake(self, pressure_freestream, mach_no_intake, spec_heat_ratio):
        return pressure_freestream / ((1 + 0.5 * (spec_heat_ratio - 1) * mach_no_intake**2)**(spec_heat_ratio / (spec_heat_ratio - 1)))

    def __get_density_intake(self, density_freestream, mach_no_intake, spec_heat_ratio):
        return density_freestream / (1 + 0.5 * (spec_heat_ratio - 1) * mach_no_intake**2)**(1 / (spec_heat_ratio - 1))

    def __get_min_engine_size(self, PRESSURE_SEA, TEMP_SEA):
        min_mass_flow = self.required_thrust / self.specific_thrust
        min_area = min_mass_flow / (self.density_intake * self.velocity_intake)
        min_diameter = geom.get_diameter_from_area(min_area)
        min_mass_flow_corrected = thermo.get_corrected_mass_flow(
            min_mass_flow, self.pressure_intake, self.temp_intake, PRESSURE_SEA, TEMP_SEA)
        return min_diameter, min_area, min_mass_flow, min_mass_flow_corrected
