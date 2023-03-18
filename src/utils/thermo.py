def get_stag_density(stag_pressure, stag_temp, GAS_CONST):
    return stag_pressure / (GAS_CONST * stag_temp)


def get_mach_no_from_velocity(velocity, T, SPEC_HEAT_RATIO, GAS_CONST):
    return velocity / (SPEC_HEAT_RATIO * GAS_CONST * T)**0.5


def get_velocity_from_mach_no(mach_no, T, SPEC_HEAT_RATIO, GAS_CONST):
    return mach_no * (SPEC_HEAT_RATIO * GAS_CONST * T)**0.5


def get_static_density(stag_density, mach_no, SPEC_HEAT_RATIO):
    return stag_density * (1 + (SPEC_HEAT_RATIO - 1) / 2 * mach_no**2)**(-1 / (SPEC_HEAT_RATIO - 1))


def get_mass_flow(area, velocity, density):
    return area * velocity * density


def get_delta_stag_enthalpy(d_stag_temp, SPEC_HEAT_CAPACITY):
    return SPEC_HEAT_CAPACITY * d_stag_temp


def get_corrected_mass_flow(mass_flow, pressure, temp, PRESSURE_SEA, TEMP_SEA):
    return mass_flow * (PRESSURE_SEA / pressure) * (temp / TEMP_SEA)**0.5


def get_speed_of_sound(temp, SPEC_HEAT_RATIO, GAS_CONST):
    return (SPEC_HEAT_RATIO * GAS_CONST * temp)**0.5


def get_static_temp(stag_temp, axial_velocity, SPEC_HEAT_RATIO, GAS_CONST):
    # const = stag_temp * (SPEC_HEAT_RATIO - 1) * \
    #     axial_velocity**2 / (SPEC_HEAT_RATIO * GAS_CONST)
    # static_temp = (stag_temp + (stag_temp**2 + 2*const)**0.5) / 2
    static_temp = stag_temp - \
        (axial_velocity**2 / (SPEC_HEAT_RATIO * GAS_CONST)) * \
        ((SPEC_HEAT_RATIO - 1) / 2)
    return static_temp
