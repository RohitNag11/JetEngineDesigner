import numpy as np
from src.turbomach_analyser import Engine
from src.utils import plots, formatter as f


def get_constants():
    return {
        'SPEC_HEAT_RATIO': 1.4,
        'GAS_CONST': 287,
        'TEMP_SEA': 288.15,
        'SPEC_HEAT_CAPACITY': 1005
    }


def get_engine_constants():
    return {
        'mass_flow': 20.5,
        'bypass_ratio': 7,
        'overall_pressure_ratio': 40,
        'fan_hub_tip_ratio': 0.35,
        'fan_tip_mach_no': 1.3,
        'inner_fan_pressure_ratio': 1.8,
        'outer_fan_pressure_ratio': 2.5,
        'comp_axial_velocity': 190,
        'turbine_axial_velocity': 150,
        'turbine_isentropic_efficiency': 0.92,
        'lpc_pressure_ratio': 2.5,
        'per_stage_pressure_ratio': 1.3,
        'P_025': 91802,
        'T_025': 331.86,
        'P_03': 1468830,
        'T_03': 758.17,
        'P_044': 410468,
        'T_044': 1268.72,
        'P_045': 402258,
        'T_045': 1268.72,
        'P_05': 82688,
        'T_05': 892.91,
        'compressor_reaction_tip': 0.5,
        'compressor_reaction_hub': 0.5,
        'turbine_reaction_tip': 0.5,
        'turbine_reaction_hub': 0.5,
        'check_dp': 5,
        'engine_diameter': 2.6,
        'min_blade_length': 0.012,
        'lpt_work_coefficient': 2.6,
        'lpt_min_blade_length': 0.031,
        'hpt_disk_depth': 0.15,
        'hpt_blade_density': 8193.25,
        'hpt_poissons_ratio': 0.27,
        'hpt_yield_strength_dict': {20: 1100,
                                    540: 982,
                                    600: 960,
                                    650: 894,
                                    700: 760,
                                    760: 555,
                                    820: 408},
    }


def get_engine_variables():
    return {
        'hpt_work_coefficient': 0.8,
        'hpt_angular_velocity': 1250,
        'hpt_min_blade_length': 0.03,
        'lpc_diffusion_factor': 0.5,
        'hpc_diffusion_factor': 0.5,
        'lpt_lift_coeff': 0.8,
        'hpt_lift_coeff': 0.8,
    }


def get_engine_vars_from_file(valid_variables_path):
    valid_variables_list = f.read_hashed_file_to_dict_list(
        valid_variables_path, sort_key='engine_score', reverse=True)
    # Get the engine variables with the highest score
    valid_variables_list[0].pop('engine_score', None)
    return valid_variables_list[0]


def main(engine_data_dir_path, engine_variables_path=None):
    engine_name = 'TEST_ENGINE' if not engine_variables_path else engine_variables_path.split(
        '/')[-1].split('.')[0]
    engine_variables = get_engine_vars_from_file(
        engine_variables_path) if engine_variables_path else get_engine_variables()
    engine = Engine(**get_constants(), **get_engine_constants(),
                    **engine_variables)
    components = [engine.fan, engine.lpc, engine.hpc, engine.hpt, engine.lpt]
    [print(f'{component}\n*****\n') for component in components]
    f.save_obj_to_file(
        engine, f'{engine_data_dir_path}/{engine_name}.json')
    plots.draw_engine(engine)


if __name__ == '__main__':
    engine_data_dir_path = f'./data/EngineData'

    # # Run optimal engine design:
    # engine_variables_path = f'./data/VariablesData/Valid/hdf_hav_hlc_hmbl_hwc_ldf_llc.csv'
    # main(engine_data_dir_path, engine_variables_path)

    # Run test engine design:
    main(engine_data_dir_path)
