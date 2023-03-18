import numpy as np
from ..utils import (geometry as geom,
                     thermo,
                     arrays as arr)


class Stage:
    def __init__(self,
                 is_compressor_stage,
                 is_low_pressure,
                 number,
                 flow_coeff,
                 work_coeff,
                 axial_velocity,
                 angular_velocity,
                 hub_diameter,
                 tip_diameter,
                 reaction_mean=0.5,
                 reaction_hub=0.5,
                 reaction_tip=0.5,
                 cooling=None,
                 stag_temp=None,
                 diffusion_factor=None,
                 lift_coeff=None,
                 disk_depth=None,
                 blade_density=None,
                 poissons_ratio=None,
                 yield_strength_dict=None,
                 SPEC_HEAT_RATIO=1.4,
                 GAS_CONST=287,):
        self.number = number
        self.is_compressor_stage = is_compressor_stage
        self.is_low_pressure = is_low_pressure
        self.lift_coeff = lift_coeff if lift_coeff else None
        self.diffusion_factor = diffusion_factor if diffusion_factor else None
        self.flow_coeff = {}
        self.flow_coeff['mean'] = flow_coeff
        self.work_coeff = {}
        self.work_coeff['mean'] = work_coeff
        self.angular_velocity = angular_velocity
        self.hub_diameter = hub_diameter
        self.tip_diameter = tip_diameter
        self.axial_velocity = axial_velocity
        self.reaction = {'mean': reaction_mean,
                         'hub': reaction_hub,
                         'tip': reaction_tip}
        self.mean_radius = 0.25 * (tip_diameter + hub_diameter)
        self.blade_height = 0.5 * (tip_diameter - hub_diameter)
        self.mean_tangential_speed = geom.get_tangential_speed(
            angular_velocity, self.mean_radius * 2)
        self.d_stag_enthalpy = work_coeff * self.mean_tangential_speed**2
        self.blade_angles_rad = {'mean': {}, 'hub': {}, 'tip': {}}
        # NOTE: consider setting first and last stage inlet/exit angles to 0
        self.blade_angles_rad['mean'] = self.get_blade_angles_at_mean_radius()
        self.get_blade_angles_at_radius()

        self.blade_angles_deg = {}
        self.blade_angles_deg['mean'] = {key: np.rad2deg(
            val) for key, val in self.blade_angles_rad['mean'].items()}
        self.blade_angles_deg['hub'] = {key: np.rad2deg(
            val) for key, val in self.blade_angles_rad['hub'].items()}
        self.blade_angles_deg['tip'] = {key: np.rad2deg(
            val) for key, val in self.blade_angles_rad['tip'].items()}
        self.solidity = self.get_solidity()
        self.rotor_aspect_ratio = self.get_aspect_ratio('rotor')
        self.rotor_chord_length = self.blade_height / self.rotor_aspect_ratio
        self.rotor_thickness = 0.15 * self.rotor_chord_length
        self.stator_aspect_ratio = self.get_aspect_ratio('stator')
        self.stator_chord_length = self.blade_height / self.stator_aspect_ratio
        self.stator_thickness = 0.15 * self.stator_chord_length
        self.no_of_blades = self.get_no_of_blades()

        # if HPT stage:
        if not self.is_compressor_stage and not self.is_low_pressure:
            self.stag_temp = stag_temp if stag_temp else None
            self.temp = thermo.get_static_temp(
                stag_temp, axial_velocity, SPEC_HEAT_RATIO, GAS_CONST)
            self.density = blade_density if blade_density else None
            self.disk_internal_radius = hub_diameter / 2 - \
                disk_depth if disk_depth else None
            self.poissons_ratio = poissons_ratio if poissons_ratio else None
            self.r = np.arange(self.disk_internal_radius, self.hub_diameter /
                               2, 0.01) if self.disk_internal_radius else None
            self.surface_temp = self.temp + cooling
            self.yield_strength = self.get_yield_strength(
                yield_strength_dict, self.surface_temp) if yield_strength_dict else None
            self.disk_thickness_estimate = self.rotor_chord_length * 2
            self.force_at_rim = self.get_force_at_rim()
            self.radial_stress, self.hoop_stress = self.get_radial_and_hoop_stresses()
            self.von_misses_stress = self.get_von_misses_stress()
            self.stress_safety_factor = self.get_stress_safety_factor()
            self.disk_thickness = self.get_disk_thickness()

        self.is_valid = self.__check_validity()

    def get_aspect_ratio(self, blade_type='stator'):
        if blade_type == 'stator':
            if self.is_compressor_stage:
                # if lpc stage
                if self.is_low_pressure:
                    return 1.75
                # if hpc stage
                else:
                    return 1.75
            else:
                # if lpt stage
                if self.is_low_pressure:
                    return 2.5
                # if hpt stage
                else:
                    return 1.5
        # if rotor
        else:
            if self.is_compressor_stage:
                # if lpc stage
                if self.is_low_pressure:
                    return 1.75
                # if hpc stage
                else:
                    return 1.75
            else:
                # if lpt stage
                if self.is_low_pressure:
                    return 3
                # if hpt stage
                else:
                    return 2.5

    def get_yield_strength(self, yield_strength_dict, surface_temp):
        return arr.interpolate_stress(yield_strength_dict, surface_temp)

    def get_blade_angles_at_mean_radius(self):
        # make phi and si negative if compressor.
        flow_coeff = self.flow_coeff['mean']
        work_coeff = self.work_coeff['mean']
        reaction = self.reaction['mean']
        term_1 = (work_coeff + 2 * reaction) / (2 * flow_coeff)
        term_2 = (work_coeff - 2 * reaction) / (2 * flow_coeff)
        if self.is_compressor_stage:
            return {
                'alpha_1': np.arctan((1 / flow_coeff) - term_1),
                'alpha_2': np.arctan((1 / flow_coeff) + term_2),
                'beta_1': np.arctan(term_1),
                'beta_2': np.arctan(-term_2)
            }
        return {
            'alpha_2': np.arctan((1 / flow_coeff) + term_2),
            'alpha_3': np.arctan((1 / flow_coeff) - term_1),
            'beta_2': np.arctan(term_2),
            'beta_3': np.arctan(-term_1)
        }

    def get_blade_angles_at_radius(self):
        locations = ['hub', 'tip']
        r_m = self.mean_radius
        for location in locations:
            r = self.tip_diameter / 2 if location == 'tip' else self.hub_diameter / 2
            u = self.angular_velocity * r
            for key, val in self.blade_angles_rad['mean'].items():
                if key.startswith('alpha'):
                    self.blade_angles_rad[location][key] = np.arctan(
                        (r_m / r) * np.tan(val))
                else:
                    suffix = key.split('_')[1]
                    alpha = self.blade_angles_rad[location][f'alpha_{suffix}']
                    term_1 = u/self.axial_velocity if self.is_compressor_stage else -u/self.axial_velocity
                    term_2 = - \
                        np.tan(alpha) if self.is_compressor_stage else np.tan(
                            alpha)
                    self.blade_angles_rad[location][key] = np.arctan(
                        term_1 + term_2)

    def get_work_coeff_at_location(self, location):
        alpha_3_r = self.blade_angles_rad[location]['alpha_3']
        alpha_2_r = self.blade_angles_rad[location]['alpha_2']
        return self.flow_coeff * (np.tan(alpha_3_r) - np.tan(alpha_2_r))

    def get_solidity(self):
        inlet = 'alpha_1' if self.is_compressor_stage else 'alpha_2'
        outlet = 'alpha_2' if self.is_compressor_stage else 'alpha_3'
        alpha_in = self.blade_angles_rad['mean'][inlet]
        alpha_out = self.blade_angles_rad['mean'][outlet]
        c1 = np.cos(alpha_in)
        c2 = np.cos(alpha_out)
        t2 = np.tan(alpha_out)
        t1 = np.tan(alpha_in)
        if self.is_compressor_stage:
            df = self.diffusion_factor
            return c2 * (t2 - t1) / (2 * c1 * (df * c2 - c2 + c1))
        z = self.lift_coeff
        # Note this only works for 50% reaction because 3 === 1 for 50% reaction
        return np.abs((2 / z) * c1**2 * (t2 - t1))

    def get_no_of_blades(self):
        return 2 * np.pi * self.mean_radius * self.solidity * self.rotor_aspect_ratio / self.blade_height

    def get_force_at_rim(self):
        rho = self.density
        c = self.rotor_chord_length
        t = self.rotor_thickness
        w = self.angular_velocity
        r0 = self.hub_diameter / 2
        h = self.blade_height
        return rho * c * t * h * w**2 * (r0 + h / 2)

    def get_radial_and_hoop_stresses(self):
        v = self.poissons_ratio
        p = self.density
        w = self.angular_velocity
        r_i = self.disk_internal_radius
        r_o = self.hub_diameter / 2
        r = self.r
        n = self.no_of_blades
        pi = np.pi
        f_rim = self.force_at_rim
        h = self.disk_thickness_estimate
        term_1 = p * w**2 * (3 + v) / 8
        term_2 = r_i**2 + r_o**2
        term_3 = r_i**2 * r_o**2 / r**2
        term_4 = r**2 * (1 + 3*v) / (3 + v)
        term_5 = n * f_rim * r_o / (2 * pi * h * (r_o**2 - r_i**2))
        term_6 = (r_i / r)**2
        radial_stress = term_1 * \
            (term_2 - term_3 - r**2) + term_5 * (1 - term_6)
        hoop_stress = term_1 * \
            (term_2 + term_3 - term_4) + term_5 * (1 + term_6)
        return radial_stress, hoop_stress

    def get_von_misses_stress(self):
        radial_stress, hoop_stress = self.get_radial_and_hoop_stresses()
        return np.sqrt(radial_stress**2 + hoop_stress**2 - radial_stress*hoop_stress)

    def get_stress_safety_factor(self):
        return self.yield_strength / max(self.von_misses_stress)

    def get_disk_thickness(self):
        p = self.density
        w = self.angular_velocity
        s = max(self.von_misses_stress)
        r_o = self.hub_diameter / 2
        r = self.r
        B = p * w**2 / (2 * s)
        return self.disk_thickness_estimate * np.exp(B * (r_o**2 - r**2))

    def __check_validity(self):
        # blade heights cannot be below 10mm
        if self.blade_height < 0.01:
            return False
        # a1 and a3=0 for first stage of lpc and last stage of hpc respectively

        # if a compressor stage:
        if self.is_compressor_stage:
            # abs(b2) has to be less that abs(b1):
            if np.abs(self.blade_angles_deg['mean']['beta_2']) > np.abs(self.blade_angles_deg['mean']['beta_1']):
                return False
            # b1-b2<45 for compressors
            if np.abs(self.blade_angles_deg['mean']['beta_1'] - self.blade_angles_deg['mean']['beta_2']) > 45:
                return False
            # solidity for compressors between 0.67 and 1.33
            if not 0.67 <= self.solidity <= 1.33:
                return False
            # Diffusion factor for compressors to be max 0.5
            if self.diffusion_factor > 0.5:
                return False
        # if a turbine stage:
        else:
            # # 90<a1-a2<120 for turbine (flow deflection)
            if not 75 < abs(self.blade_angles_deg['mean']['alpha_2'] - self.blade_angles_deg['mean']['alpha_3']) < 120:
                return False
            # # solidity for turbines is between 1 and 2
            if not 1 <= self.solidity <= 2:
                return False
            # lift coefficient for turbines to be about 0.8
            if not 0.7 <= self.lift_coeff <= 0.9:
                return False
        # Safety factor on turbine blades to be atleast 1.5-2?
            # NOTE: idk if this can be checked
        return True
