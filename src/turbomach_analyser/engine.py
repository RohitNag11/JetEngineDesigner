import numpy as np
from .compressor import Compressor
from .turbine import Turbine
from .fan import Fan
from ..utils import (activation as act)


class Engine:
    def __init__(self,
                 mass_flow,
                 engine_diameter=2.6,
                 bypass_ratio=7,
                 overall_pressure_ratio=40,
                 fan_hub_tip_ratio=0.35,
                 fan_tip_mach_no=1.3,
                 inner_fan_pressure_ratio=1.8,
                 outer_fan_pressure_ratio=2.5,
                 comp_axial_velocity=190,
                 turbine_axial_velocity=150,
                 lpc_pressure_ratio=2.5,
                 per_stage_pressure_ratio=1.3,
                 lpt_work_coefficient=2,
                 hpt_work_coefficient=1.95,
                 hpt_angular_velocity=900,
                 hpt_min_blade_length=0.02,
                 turbine_isentropic_efficiency=0.9,
                 P_025=91802,
                 T_025=331.86,
                 P_03=1468830,
                 T_03=758.17,
                 P_041=1424765,
                 T_041=1677.70,
                 P_044=410468,
                 T_044=1268.72,
                 P_045=402258,
                 T_045=1268.72,
                 P_05=82688,
                 T_05=892.91,
                 min_blade_length=0.01,
                 lpt_min_blade_length=0.012,
                 lpc_reaction_mean=0.5,
                 hpc_reaction_mean=0.5,
                 turbine_reaction_mean=0.5,
                 lpc_diffusion_factor=0.45,
                 hpc_diffusion_factor=0.45,
                 lpt_lift_coeff=1,
                 hpt_lift_coeff=1,
                 hpt_disk_depth=0.01,
                 hpt_blade_density=2700,
                 hpt_poissons_ratio=0.27,
                 hpt_yield_strength_dict={20: 1100,
                                          540: 982,
                                          600: 960,
                                          650: 894,
                                          700: 760,
                                          760: 555,
                                          820: 408},
                 GAS_CONST=1.4,
                 SPEC_HEAT_RATIO=287,
                 TEMP_SEA=288.15,
                 SPEC_HEAT_CAPACITY=1005,
                 check_dp=5):
        self.mass_flow = mass_flow
        self.diameter = engine_diameter
        self.bypass_ratio = bypass_ratio
        self.overall_pressure_ratio = overall_pressure_ratio
        self.fan = Fan(engine_diameter=engine_diameter,
                       tip_mach_no=fan_tip_mach_no,
                       hub_tip_ratio=fan_hub_tip_ratio,
                       inner_fan_pressure_ratio=inner_fan_pressure_ratio,
                       outer_fan_pressure_ratio=outer_fan_pressure_ratio,
                       bypass_ratio=bypass_ratio,
                       SPEC_HEAT_RATIO=SPEC_HEAT_RATIO,
                       GAS_CONST=GAS_CONST,
                       TEMP_SEA=TEMP_SEA)
        self.hpt = Turbine(is_low_pressure=False,
                           mass_flow=self.mass_flow,
                           axial_velocity=turbine_axial_velocity,
                           pressure_ratio=P_044/P_041,
                           P0_exit=P_044,
                           T0_exit=T_044,
                           T0_inlet=T_041,
                           angular_velocity=hpt_angular_velocity,
                           isentropic_efficiency=turbine_isentropic_efficiency,
                           work_coefficient=hpt_work_coefficient,
                           min_blade_length=hpt_min_blade_length,
                           reaction_mean=turbine_reaction_mean,
                           lift_coeff=hpt_lift_coeff,
                           disk_depth=hpt_disk_depth,
                           blade_density=hpt_blade_density,
                           poissons_ratio=hpt_poissons_ratio,
                           yield_strength_dict=hpt_yield_strength_dict,
                           SPEC_HEAT_RATIO=SPEC_HEAT_RATIO,
                           GAS_CONST=GAS_CONST,
                           SPEC_HEAT_CAPACITY=SPEC_HEAT_CAPACITY,
                           check_dp=5)
        self.lpt = Turbine(is_low_pressure=True,
                           mass_flow=self.mass_flow,
                           axial_velocity=turbine_axial_velocity,
                           pressure_ratio=P_05/P_045,
                           P0_exit=P_05,
                           T0_exit=T_05,
                           T0_inlet=T_045,
                           angular_velocity=self.fan.angular_velocity,
                           isentropic_efficiency=turbine_isentropic_efficiency,
                           work_coefficient=lpt_work_coefficient,
                           min_blade_length=lpt_min_blade_length,
                           reaction_mean=turbine_reaction_mean,
                           lift_coeff=lpt_lift_coeff,
                           SPEC_HEAT_RATIO=SPEC_HEAT_RATIO,
                           GAS_CONST=GAS_CONST,
                           SPEC_HEAT_CAPACITY=SPEC_HEAT_CAPACITY,
                           check_dp=check_dp)
        self.lpc = Compressor(is_low_pressure=True,
                              mass_flow=self.mass_flow,
                              axial_velocity=comp_axial_velocity,
                              pressure_ratio=lpc_pressure_ratio/inner_fan_pressure_ratio,
                              P0_exit=P_025,
                              T0_exit=T_025,
                              T0_inlet=self.__get_T_021(),
                              angular_velocity=self.fan.angular_velocity,
                              mean_radius=self.fan.inner_fan_mean_radius,
                              per_stage_pressure_ratio=per_stage_pressure_ratio,
                              reaction_mean=lpc_reaction_mean,
                              diffusion_factor=lpc_diffusion_factor,
                              SPEC_HEAT_RATIO=SPEC_HEAT_RATIO,
                              GAS_CONST=GAS_CONST,
                              SPEC_HEAT_CAPACITY=SPEC_HEAT_CAPACITY,
                              check_dp=check_dp)
        self.hpc = Compressor(is_low_pressure=False,
                              mass_flow=self.mass_flow,
                              axial_velocity=comp_axial_velocity,
                              pressure_ratio=overall_pressure_ratio/lpc_pressure_ratio,
                              P0_exit=P_03,
                              T0_exit=T_03,
                              T0_inlet=T_025,
                              angular_velocity=hpt_angular_velocity,
                              final_blade_length=min_blade_length,
                              per_stage_pressure_ratio=per_stage_pressure_ratio,
                              reaction_mean=hpc_reaction_mean,
                              diffusion_factor=hpc_diffusion_factor,
                              SPEC_HEAT_RATIO=SPEC_HEAT_RATIO,
                              GAS_CONST=GAS_CONST,
                              SPEC_HEAT_CAPACITY=SPEC_HEAT_CAPACITY,
                              check_dp=check_dp)
        self.is_valid = self.__check_validity()
        self.score = self.__get_score()
        return

    def __get_T_021(self):
        # TODO
        # thermo.get_static_temp
        return 260.73

    def __check_validity(self):
        # TODO
        compressors = [self.lpc, self.hpc]
        turbines = [self.lpt, self.hpt]
        turbo_machines = compressors + turbines
        check_dp = 5
        # engine must have at least 0.5m clearance from ground
        # NOTE: this means engine diameter can't be more than 3.5m
        if self.diameter > 3.5:
            return False
        # Bypass ratio is 7
        if self.bypass_ratio != 7:
            return False
        # Mean radius of lpc can't be more than 30% higher than inner fan
            # NOTE:(idk about the 30% but let's just say it is)
        if self.lpt.mean_radius > 1.3 * self.fan.inner_fan_mean_radius:
            return False
        # Mean radius of lpt can't be less than mean radius of hpt
        if self.lpt.mean_radius < self.hpt.mean_radius:
            return False
        # Mean radius of lpc can't be less than mean radius of hpc
        if self.lpc.mean_radius < self.hpc.mean_radius:
            return False
        # Mean radius of lpc can't be more than 20% higher than inner fan
            # NOTE:(idk about the 20% but let's just say it is)
        if self.lpc.mean_radius > 1.2 * self.fan.inner_fan_mean_radius:
            return False
        # OPR and turbine pressure ratio should roughly match
        turbine_pressure_ratios = np.prod(
            np.array([t.pressure_ratio for t in turbines]))
        higher_pressure_ratio = max(
            turbine_pressure_ratios, self.overall_pressure_ratio)
        lower_pressure_ratio = min(
            turbine_pressure_ratios, self.overall_pressure_ratio)
        if lower_pressure_ratio / higher_pressure_ratio < 0.9:
            return False
        # All turbo machines should be valid:
        if not all([t.is_valid for t in turbo_machines]):
            return False
        return True

    def __get_score(self):
        compressors = [self.lpc, self.hpc]
        turbines = [self.lpt, self.hpt]
        turbo_machines = compressors + turbines
        # TODO
        score = 0
        # Award points for fewer stages:
        score += act.smooth_step_down(len(self.lpc.stages),
                                      start=1,
                                      end=4,
                                      min_y=0,
                                      max_y=1)
        score += act.smooth_step_down(len(self.hpc.stages),
                                      start=9,
                                      end=14,
                                      min_y=0,
                                      max_y=3)
        score += act.smooth_step_down(len(self.hpt.stages),
                                      start=0,
                                      end=3,
                                      min_y=-10,
                                      max_y=10)
        score += act.smooth_step_down(len(self.lpt.stages),
                                      start=3,
                                      end=6,
                                      min_y=0,
                                      max_y=1)
        # Award points for similar hpc and hpt mean radii:
        score += act.smooth_step_down(abs(self.hpc.mean_radius - self.hpt.mean_radius),
                                      start=0,
                                      end=self.diameter / 10,
                                      min_y=0,
                                      max_y=20)
        # Award points for high mean tip mach number:
        mean_tip_mach_nos = np.mean(
            np.array([self.fan.tip_mach_no, max(self.lpt.tip_mach_nos), max(self.hpt.tip_mach_nos)]))
        score += act.smooth_step_up(mean_tip_mach_nos,
                                    start=0.6,
                                    end=1.2,
                                    min_y=0,
                                    max_y=1)
        # Award points fot similar OPR and turbine pressure ratio:
        turbine_pressure_ratios = np.prod(
            np.array([t.pressure_ratio for t in turbines]))
        higher_pressure_ratio = max(
            turbine_pressure_ratios, self.overall_pressure_ratio)
        lower_pressure_ratio = min(
            turbine_pressure_ratios, self.overall_pressure_ratio)
        score += act.smooth_step_down(lower_pressure_ratio / higher_pressure_ratio,
                                      start=0.9,
                                      end=1,
                                      min_y=-20,
                                      max_y=20)
        # Award points for low average work coefficients and flow coefficients:
        for t in turbines:
            if t.is_low_pressure:
                optimal_work_coeff_range = (0.8, 1.8)
                optimal_flow_coeff_range = (0.5, 0.65)
            else:
                optimal_work_coeff_range = (1, 2.4)
                optimal_flow_coeff_range = (0.7, 11)
            for stage in t.stages:
                for location in ['mean', 'hub', 'tip']:
                    score += act.smooth_step_down(stage.work_coeff[location],
                                                  start=optimal_work_coeff_range[0],
                                                  end=optimal_work_coeff_range[1],
                                                  min_y=0,
                                                  max_y=0.1)
                    score += act.smooth_step_down(stage.flow_coeff[location],
                                                  start=optimal_flow_coeff_range[0],
                                                  end=optimal_flow_coeff_range[1],
                                                  min_y=0,
                                                  max_y=0.1)

        return score
