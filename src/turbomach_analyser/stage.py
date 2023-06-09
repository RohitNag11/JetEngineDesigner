import numpy as np
from ..utils import (geometry as geom,
                     thermo,
                     arrays as arr)


class Stage:
    def __init__(self,
                 is_compressor_stage,
                 is_low_pressure,
                 number,
                 work_coeff,
                 axial_velocity,
                 angular_velocity,
                 hub_diameter,
                 tip_diameter,
                 reaction_mean=0.5,
                 cooling=None,
                 stag_temp=None,
                 diffusion_factor=None,
                 lift_coeff=None,
                 disk_depth=None,
                 blade_density=None,
                 poissons_ratio=None,
                 yield_strength_dict=None,
                 check_dp=5,
                 SPEC_HEAT_RATIO=1.4,
                 GAS_CONST=287,):
        self.number = number
        self.is_compressor_stage = is_compressor_stage
        self.is_low_pressure = is_low_pressure
        if lift_coeff:
            self.lift_coeff = {'mean': lift_coeff}
        if diffusion_factor:
            self.diffusion_factor = {'mean': diffusion_factor}
        self.mean_radius = 0.25 * (tip_diameter + hub_diameter)
        self.blade_height = 0.5 * (tip_diameter - hub_diameter)
        self.angular_velocity = angular_velocity
        self.mean_tangential_speed = geom.get_tangential_speed(
            angular_velocity, self.mean_radius * 2)
        self.hub_diameter = hub_diameter
        self.tip_diameter = tip_diameter
        self.axial_velocity = axial_velocity
        self.work_coeff = {'mean': work_coeff}
        self.flow_coeff = self.get_flow_coeffs()
        self.reaction = {'mean': reaction_mean}
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
        self.populate_work_coeffs_and_reactions()
        self.populate_diffusion_factor()
        self.populate_lift_coeff()
        self.d_stag_enthalpy = self.get_d_stag_enthalpy()
        self.rotor_aspect_ratio = self.get_aspect_ratio('rotor')
        self.rotor_chord_length = self.blade_height / self.rotor_aspect_ratio
        self.rotor_thickness = 1.2 * self.rotor_chord_length
        self.stator_aspect_ratio = self.get_aspect_ratio('stator')
        self.stator_chord_length = self.blade_height / self.stator_aspect_ratio
        self.stator_thickness = 1.2 * self.stator_chord_length
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
        self.is_valid = self.__check_validity(check_dp)

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
                # 'beta_1': np.arctan(term_1),
                # 'beta_2': np.arctan(-term_2),
                'beta_1': np.arctan(-term_1),
                'beta_2': np.arctan(term_2)
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
            flow_coeff = self.flow_coeff[location]
            for key, val in self.blade_angles_rad['mean'].items():
                if key.startswith('alpha'):
                    self.blade_angles_rad[location][key] = np.arctan(
                        (r_m / r) * np.tan(val))
                else:
                    suffix = key.split('_')[1]
                    alpha = self.blade_angles_rad[location][f'alpha_{suffix}']
                    # term_1 = 1/flow_coeff if self.is_compressor_stage else -1/flow_coeff
                    # term_2 = - \
                    #     np.tan(alpha) if self.is_compressor_stage else np.tan(
                    #         alpha)
                    term_1 = -1/flow_coeff
                    term_2 = np.tan(alpha)
                    self.blade_angles_rad[location][key] = np.arctan(
                        term_1 + term_2)

    def get_flow_coeffs(self):
        flow_coeff = {'mean': self.axial_velocity /
                      (self.angular_velocity * self.mean_radius)}
        locations = ['hub', 'tip']
        for location in locations:
            r = self.tip_diameter / 2 if location == 'tip' else self.hub_diameter / 2
            u = self.angular_velocity * r
            flow_coeff[location] = self.axial_velocity / u
        return flow_coeff

    def populate_work_coeffs_and_reactions(self):
        for location in ['hub', 'tip']:
            alpha_2 = self.blade_angles_rad[location]['alpha_2']
            flow_coeff = self.flow_coeff[location]
            if self.is_compressor_stage:
                alpha_1 = self.blade_angles_rad[location]['alpha_1']
                # self.work_coeff[location] = flow_coeff * \
                #     (np.tan(alpha_2) - np.tan(alpha_1))
                self.work_coeff[location] = flow_coeff * \
                    (np.tan(alpha_2) - np.tan(alpha_1))
                self.reaction[location] = 1 - 0.5 * \
                    flow_coeff * (np.tan(alpha_2) + np.tan(alpha_1))
            else:
                alpha_3 = self.blade_angles_rad[location]['alpha_3']
                self.work_coeff[location] = flow_coeff * \
                    (np.tan(alpha_2) - np.tan(alpha_3))
                self.reaction[location] = 1 - 0.5 * \
                    flow_coeff * (np.tan(alpha_2) + np.tan(alpha_3))

    def populate_diffusion_factor(self):
        if self.is_compressor_stage:
            for location in ['hub', 'tip']:
                a_1 = self.blade_angles_rad[location]['alpha_1']
                a_2 = self.blade_angles_rad[location]['alpha_2']
                t2 = np.tan(a_2)
                t1 = np.tan(a_1)
                c1 = np.cos(a_1)
                c2 = np.cos(a_2)
                s = self.solidity
                self.diffusion_factor[location] = (
                    t2 - t1) / (2 * c1 * s) - c1 / c2 + 1

    def populate_lift_coeff(self):
        if not self.is_compressor_stage:
            for location in ['hub', 'tip']:
                a_1 = self.blade_angles_rad[location]['alpha_2']
                a_2 = self.blade_angles_rad[location]['alpha_3']
                c1 = np.cos(a_1)
                t2 = np.tan(a_2)
                t1 = np.tan(a_1)
                s = self.solidity
                self.lift_coeff[location] = np.abs(2 * c1**2 * (t2 - t1) / s)

    def get_d_stag_enthalpy(self):
        d_stage_enthalpy = {}
        locations = ['mean', 'hub', 'tip']
        for location in locations:
            r = self.tip_diameter / 2 if location == 'tip' else self.hub_diameter / 2
            r = self.mean_radius if location == 'mean' else r
            u = self.angular_velocity * r
            work_coeff = self.work_coeff[location]
            d_stage_enthalpy[location] = work_coeff * u**2
        return d_stage_enthalpy

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
            df = self.diffusion_factor['mean']
            return c2 * (t2 - t1) / (2 * c1 * (df * c2 - c2 + c1))
        z = self.lift_coeff['mean']
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

    def __check_validity(self, check_dp):
        # blade heights cannot be below 10mm
        if self.blade_height < 0.01:
            return False
        # a1 and a3=0 for first stage of lpc and last stage of hpc respectively

        # stagnation enthalpy change stays constant for any location
        if not len(set(round(v, check_dp) for v in self.d_stag_enthalpy.values())) == 1:
            return False

        # if a compressor stage:
        if self.is_compressor_stage:
            for location in ['mean', 'hub', 'tip']:
                # abs(b2) has to be less that abs(b1):
                if np.abs(self.blade_angles_deg[location]['beta_2']) > np.abs(self.blade_angles_deg[location]['beta_1']):
                    return False
                # b1-b2<45 for compressors
                if np.abs(self.blade_angles_deg[location]['beta_1'] - self.blade_angles_deg[location]['beta_2']) > 45:
                    return False
                # a1 and a2 have to be positive:
                if self.blade_angles_deg[location]['alpha_1'] <= 0 or self.blade_angles_deg[location]['alpha_2'] <= 0:
                    return False
                # Diffusion factor for compressors to be max 0.5
                if self.diffusion_factor[location] > 0.5:
                    return False
            if not 0.67 <= self.solidity <= 1.33:
                return False
        # if a turbine stage:
        else:
            for location in ['mean', 'hub', 'tip']:
                # # 75<a1-a2<120 for turbine (flow deflection)
                if not 75 < abs(self.blade_angles_deg[location]['alpha_2'] - self.blade_angles_deg[location]['alpha_3']) < 120:
                    return False
                # lift coefficient for turbines to be about 0.8
                if not 0.7 <= self.lift_coeff[location] <= 0.9:
                    return False

            # reaction has to be greater than 0 at hub for turbines
            if self.reaction['hub'] < 0:
                return False
            # reaction has to be less than 1 at tip for turbines
            if self.reaction['tip'] > 1:
                return False
            # # solidity for turbines is between 1 and 2
            if not 1 <= self.solidity <= 2:
                return False
            # Safety factor on turbine blades to be atleast 1.5-2
            if not self.is_low_pressure:
                if self.stress_safety_factor < 1.5:
                    return False

        return True
