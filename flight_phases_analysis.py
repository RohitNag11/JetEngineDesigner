# author: Rohit Nag
# date: 02/02/2023

import numpy as np
from src.flight_analyser import FlightAnalysis
from src.utils import formatter


def get_constants():
    SPEC_HEAT_RATIO = 1.4
    GAS_CONST = 287
    DENSITY_SEA = 1.225
    TEMP_SEA = 288.15
    PRESSURE_SEA = 101300
    return SPEC_HEAT_RATIO, GAS_CONST, DENSITY_SEA, TEMP_SEA, PRESSURE_SEA


def get_phases_data():
    return {
        'cruise': {
            'mach_no': 0.84,
            'required_thrust': 29900,
            'specific_thrust': 182,
            'density_ratio': 0.3,
            'temp_ratio': 0.75,
            'pressure_ratio': 0.22,
            'coeff': 0.6
        },
        'top_of_climb': {
            'mach_no': 0.84,
            'required_thrust': 84000,
            'specific_thrust': 185,
            'density_ratio': 0.3,
            'temp_ratio': 0.75,
            'pressure_ratio': 0.22,
            'coeff': 0.6,
            'diameter': 2.6
        },
        'take_off_normal': {
            'velocity_freestream': 70,
            'required_thrust': 116000,
            'specific_thrust': 236,
            'coeff': 1 / 0.6,
            'diameter': 2.6
        },
        'take_off_failure': {
            'velocity_freestream': 80,
            'required_thrust': 232000,
            'specific_thrust': 270,
            'coeff': 1 / 0.6,
            'diameter': 2.6
        }
    }


def main():
    flight_analysis = FlightAnalysis(*get_constants())
    for phase_name, phase_conditions in get_phases_data().items():
        flight_analysis.add_phase(phase_name, phase_conditions)
        analysed_phase = flight_analysis.phases[phase_name]
        print(f'{formatter.humanise_str(phase_name)}:')
        print(f"Mach No: {analysed_phase.mach_no}")
        print(f"Minimum Engine Diameter: {analysed_phase.diameter}")
        print(f"Mass Flowrate: {analysed_phase.mass_flow}")
        print(f"Corrected Mass Flowrate: {analysed_phase.mass_flow_corrected}")
        print('\n')


if __name__ == "__main__":
    main()
