from typing import Dict, Tuple, Set
import json
import numpy as np
import os


class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return json.JSONEncoder.default(self, obj)


def humanise_str(string):
    return string.replace('_', ' ').title()


def to_dict(obj):
    """
    Takes an object and recursively returns a dictionary containing keys and values as base classes.
    """
    if isinstance(obj, dict):
        return {k: to_dict(v) for k, v in obj.items()}
    elif isinstance(obj, (list, tuple)):
        return [to_dict(e) for e in obj]
    elif hasattr(obj, '__dict__'):
        return to_dict(obj.__dict__)
    else:
        return obj


def to_json(obj):
    return json.dumps(to_dict(obj), indent=4, cls=NumpyEncoder)


def save_obj_to_file(obj, filename):
    """
    Saves a JSON string to a text file.
    """
    json_str = to_json(obj)
    with open(filename, 'w') as file:
        json.dump(json.loads(json_str), file, indent=4)


def format_elapsed_time(elapsed_time: float) -> str:
    hours, remainder = divmod(int(elapsed_time), 3600)
    minutes, seconds = divmod(remainder, 60)
    milliseconds = int((elapsed_time - int(elapsed_time)) * 1000)
    return f"{hours:02}:{minutes:02}:{seconds:02}:{milliseconds:03}"


def sort_dict(d: Dict) -> Dict:
    return {k: d[k] for k in sorted(d)}


def hash_dict_keys(d: Dict) -> str:
    return ','.join(sort_dict(d).keys())


def compact_hash_dict_keys(d: Dict) -> str:
    keys = sort_dict(d).keys()
    return '_'.join(''.join(word[0] for word in s.split('_')) for s in keys)


def hash_dict_vals(d: Dict) -> str:
    return ','.join(map(str, sort_dict(d).values()))


def unhash_dict(keys_hash: str, vals_hash: str) -> Dict:
    keys, vals_str = keys_hash.split(','), vals_hash.split(',')
    return dict(zip(keys, map(float, vals_str)))


def hashed_vals_to_csv(key_hash: str, hashed_vals_set: Set[str], filename: str):
    with open(filename, 'w') as f:
        f.write(f"{key_hash}\n")
        f.writelines(f"{val_hash}\n" for val_hash in hashed_vals_set)


def csv_to_hashed_val_set(filename: str) -> Tuple[str, Set[str]]:
    with open(filename, 'r') as f:
        lines = [line.strip() for line in f]
    return lines[0], set(lines[1:])


def read_vars_file(filepath: str) -> Tuple[str, Set[str]]:
    return csv_to_hashed_val_set(filepath) if os.path.isfile(filepath) else ('', set())


def read_hashed_file_to_dict_list(filename: str, sort_key: str = None, reverse: bool = False):
    # Read the key hash and value hashes from the file
    key_hash, hashed_val_set = csv_to_hashed_val_set(filename)
    # Split the key hash into a list of keys
    keys = key_hash.split(',')
    # Initialize an empty list to store the dictionaries
    dict_list = []
    # Iterate through the value hashes
    for val_hash in hashed_val_set:
        # Split the value hash into a list of values and convert them to float
        vals_str = val_hash.split(',')
        vals = list(map(float, vals_str))
        # Create a dictionary by mapping the keys to their corresponding values
        var_dict = {k: v for k, v in zip(keys, vals)}
        # Add the dictionary to the list
        dict_list.append(var_dict)
    if sort_key is not None:
        return sorted(dict_list, key=lambda d: d[sort_key], reverse=reverse)
    return dict_list
