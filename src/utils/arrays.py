import numpy as np


def interpolate_stress(temperature_dict, input_temperature):
    # Ensure the dictionary is sorted by temperature
    sorted_temperature_dict = dict(sorted(temperature_dict.items()))

    # Find the temperature range in which the input_temperature falls
    lower_temperature = None
    upper_temperature = None

    for temperature, stress in sorted_temperature_dict.items():
        if temperature <= input_temperature:
            lower_temperature = temperature
        elif temperature > input_temperature:
            upper_temperature = temperature
            break

    # Check if input_temperature falls outside the given temperature range
    if lower_temperature is None or upper_temperature is None:
        raise ValueError(
            "Input temperature is outside the provided temperature range.")

    # Linear interpolation of stress values
    lower_stress = sorted_temperature_dict[lower_temperature]
    upper_stress = sorted_temperature_dict[upper_temperature]

    interpolated_stress = lower_stress + (input_temperature - lower_temperature) * (
        upper_stress - lower_stress) / (upper_temperature - lower_temperature)

    return interpolated_stress
