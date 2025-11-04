import json
from typing import List, Any

def load_json(json_file: str) -> dict[str, Any] | list[Any]:
    """Loads a JSON file and returns the data

    Args:
        json_file (str): Path to JSON file to load

    Returns:
        dict[str, Any] | list[Any]: Resulting values
    """
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data

def load_json_root(json_file: str) -> List[str]:
    """Loads a JSON file and returns the root values.

    - If JSON is an array, returns the array as-is
    - If JSON is a dict, returns list of keys

    Args:
        json_file (str): Path to JSON file to load

    Returns:
        List[str]: Resulting list of values
    """

    # open file
    data = load_json(json_file)

    # return based on type
    if isinstance(data, list):
        return data
    elif isinstance(data, dict):
        return list(data.keys())
    else:
        raise ValueError(f'{json_file} needs to be an array or object.')
