import numpy as np
from src.turbomach_analyser import Engine
from src.utils import formatter as f
import itertools
import time
from tqdm import tqdm


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
        'turbine_reaction_mean': 0.5,
        'check_dp': 5,
        'engine_diameter': 2.6,
        'min_blade_length': 0.012,
        'lpt_work_coefficient': 2.6,
        'lpt_min_blade_length': 0.031,
        'hpt_disk_depth': 0.15,
        'hpt_blade_density': 8193.25,
        'hpt_poissons_ratio': 0.27,
        'hpt_yield_strength_dict': {20: 1100e6,
                                    540: 982e6,
                                    600: 960e6,
                                    650: 894e6,
                                    700: 760e6,
                                    760: 555e6,
                                    820: 408e6},
        'lpt_lift_coeff': 0.85,
    }


def __get_variable_ranges():
    return {
        'hpt_min_blade_length': np.linspace(0.019, 0.023, 3, endpoint=True),
        'hpt_work_coefficient': np.linspace(1.76, 2, 3, endpoint=True),
        'hpt_angular_velocity': np.linspace(500, 1500, 6, endpoint=True),
        'lpc_diffusion_factor': np.linspace(0.1, 0.5, 5, endpoint=True),
        'hpc_diffusion_factor': np.linspace(0.1, 0.5, 5, endpoint=True),
        'hpt_lift_coeff': np.linspace(0.7, 0.9, 3, endpoint=True),
        'lpc_reaction_mean': np.linspace(0.3, 0.9, 3, endpoint=True),
        'hpc_reaction_mean': np.linspace(0.3, 0.9, 3, endpoint=True),
    }


def __get_variable_ranges_from_file(valid_variables_path, per_var_iterations):
    valid_variables_list = f.read_hashed_file_to_dict_list(
        valid_variables_path)
    # Remove the engine score from all dictionaries
    [valid_variables.pop('engine_score', None)
     for valid_variables in valid_variables_list]
    result = {}
    # Find the minimum and maximum values for each key
    for d in valid_variables_list:
        for key, value in d.items():
            if key not in result:
                result[key] = {"min": value, "max": value}
            else:
                if value < result[key]["min"]:
                    result[key]["min"] = value
                if value > result[key]["max"]:
                    result[key]["max"] = value

    # Create the final dictionary with np.linspace for each key
    for key, value in result.items():
        result[key] = np.linspace(
            value["min"],
            value["max"],
            per_var_iterations,
            endpoint=True)
        # Convert to set and back to list to remove duplicates
        result[key] = list(set(result[key]))
        # Sort the list after removing duplicates
        result[key].sort()
    return result


def generate_possible_var_dicts(var_ranges_dict):
    return ({k: v for k, v in zip(var_ranges_dict.keys(), p)}
            for p in itertools.product(*var_ranges_dict.values()))


def get_no_iterations(var_ranges_dict):
    return np.prod([len(x) for x in var_ranges_dict.values()])


def read_vars_files(tried_vars_path, valid_vars_path):
    tried_var_key_hash, tried_var_vals_hash_set = f.read_vars_file(
        tried_vars_path)
    valid_var_key_hash, valid_var_vals_hash_set = f.read_vars_file(
        valid_vars_path)
    return tried_var_key_hash, tried_var_vals_hash_set, valid_var_key_hash, valid_var_vals_hash_set


def __run_iteration(no_iterations: int,
                    all_possible_vars_dicts,
                    tried_var_vals_hash_set: set,
                    valid_var_vals_hash_set: set,
                    tried_var_key_hash: str,
                    valid_var_key_hash: str,
                    var_key_hash: str):
    with tqdm(total=no_iterations,
              desc='Processing',
              unit='var_dict',) as pbar:
        with tqdm(total=no_iterations,
                  desc='Accepted  ',
                  unit='var_dict',
                  position=1,
                  colour='CYAN') as valid_pbar:
            valid_pbar.update(len(valid_var_vals_hash_set))
            for var_dict in all_possible_vars_dicts:
                var_val_hash = f.hash_dict_vals(var_dict)
                if var_val_hash not in tried_var_vals_hash_set or var_key_hash != tried_var_key_hash:
                    tried_var_vals_hash_set.add(var_val_hash)
                    try:
                        engine = Engine(**get_constants(),
                                        **get_engine_constants(),
                                        **var_dict)
                        if engine.is_valid:
                            valid_var_vals_hash_set.add(
                                var_val_hash + f',{engine.score}')
                            valid_pbar.update(1)
                    except:
                        pass
                pbar.update(1)
    if var_key_hash != tried_var_key_hash:
        tried_var_key_hash = var_key_hash
        valid_var_key_hash = var_key_hash + ',engine_score'
    return tried_var_key_hash, tried_var_vals_hash_set, valid_var_key_hash, valid_var_vals_hash_set


def complete_run(tried_vars_dir: str, valid_vars_dir: str, var_ranges_dict, per_var_iterations=None):
    var_key_hash = f.hash_dict_keys(var_ranges_dict)
    var_key_hash_compact = f.compact_hash_dict_keys(var_ranges_dict)
    tried_vars_path = f'{tried_vars_dir}/{var_key_hash_compact}.csv'
    valid_vars_path = f'{valid_vars_dir}/{var_key_hash_compact}.csv'

    if per_var_iterations is not None:
        var_ranges_dict = __get_variable_ranges_from_file(
            valid_vars_path, per_var_iterations)

    all_possible_vars_dicts = generate_possible_var_dicts(var_ranges_dict)
    tried_var_key_hash, tried_var_vals_hash_set, valid_var_key_hash, valid_var_vals_hash_set = read_vars_files(
        tried_vars_path, valid_vars_path)
    no_iterations = get_no_iterations(var_ranges_dict)

    tried_var_key_hash, tried_var_vals_hash_set, valid_var_key_hash, valid_var_vals_hash_set = __run_iteration(
        no_iterations, all_possible_vars_dicts, tried_var_vals_hash_set, valid_var_vals_hash_set, tried_var_key_hash, valid_var_key_hash, var_key_hash)

    f.hashed_vals_to_csv(tried_var_key_hash,
                         tried_var_vals_hash_set,
                         tried_vars_path)
    f.hashed_vals_to_csv(valid_var_key_hash,
                         valid_var_vals_hash_set,
                         valid_vars_path)

    return len(valid_var_vals_hash_set)


def first_run(tried_vars_dir: str, valid_vars_dir: str):
    print('\nRunning first iteration')
    var_ranges_dict = __get_variable_ranges()
    no_valid_iterations = complete_run(
        tried_vars_dir, valid_vars_dir, var_ranges_dict)
    print(f'No of valid iterations: {no_valid_iterations}')
    print('Completed first iteration')


def second_run(tried_vars_dir: str, valid_vars_dir: str, per_var_iterations: int):
    print('\nRunning second iteration')
    var_ranges_dict = __get_variable_ranges()
    no_valid_iterations = complete_run(
        tried_vars_dir, valid_vars_dir, var_ranges_dict, per_var_iterations)
    print(f'No of valid iterations: {no_valid_iterations}')
    print('Completed second iteration')


def main(tried_vars_dir: str, valid_vars_dir: str, second_iteration: False, second_per_var_iterations: int):
    first_run(tried_vars_dir, valid_vars_dir)
    if second_iteration:
        second_run(tried_vars_dir, valid_vars_dir, second_per_var_iterations)


if __name__ == '__main__':
    tried_variables_dir = './data/VariablesData/Tried'
    valid_variables_dir = './data/VariablesData/Valid'
    st = time.time()

    main(tried_variables_dir,
         valid_variables_dir,
         second_iteration=True,
         second_per_var_iterations=6)

    # Get variable ranges from valid results:
    # print(__get_variable_ranges_from_file(
    #     './data/VariablesData/Valid/cdf_hav_hmbl_hwc_lmbl_lwc_mbl_tlc.csv', 5))

    et = time.time()
    print(f'\nruntime: {f.format_elapsed_time(et - st)}')
