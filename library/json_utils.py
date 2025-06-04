"""
This module provides utility functions for saving and loading dictionaries to and from JSON files.

Functions:
    save_dict_to_file(data: dict, file_path: str, file_name: str, indent: int = 4) -> Path:
        Save a dictionary to a specified file path in JSON format.
    
    load_dict_from_file(file_path: str, file_name: str) -> dict:
        Load a dictionary from a specified JSON file.
"""
import library.config as config
import logging

import json
from pathlib import Path

from library.path_utils import make_dir, get_file_path, to_absolute_path

def save_dict_to_file(data: dict, file_path: str, file_name: str, indent: int = 4) -> Path:
    """
    Save a dictionary to a specified file path in JSON format.

    Args:
        data (dict): The dictionary to save.
        file_path (str): The directory path where the dictionary will be saved.
        file_name (str): The name of the file to be saved.
        indent (int, optional): The indentation level for pretty-printing. Default is 4.
    
    Returns:
        Path: The full path of the saved JSON file.
    
    Raises:
        ValueError: If data is not a dictionary.
        IOError: If there is an issue writing to the file.
    """
    file_name = f"{file_name}.json"
    if not isinstance(data, dict):
        raise ValueError("Input data must be a dictionary.")
    
    dir_path = make_dir(file_path)
    path = dir_path / file_name
    
    try:
        with path.open("w", encoding="utf-8") as f:
            json.dump(data, f, indent=indent)
        logging.debug(f"Dictionary saved successfully to {path}")
    except IOError as e:
        raise IOError(f"Error writing to file {path}: {e}")
    
    return path

def load_dict_from_file(file_path: str, file_name: str) -> dict:
    """
    Load a dictionary from a specified JSON file.

    Args:
        file_path (str): The directory path where the dictionary is stored.
        file_name (str): The name of the JSON file.

    Returns:
        dict: The loaded dictionary.

    Raises:
        FileNotFoundError: If the file does not exist.
        ValueError: If the file content is not a valid dictionary.
        IOError: If there is an issue reading the file.
    """
    file_name = f"{file_name}.json"
    path = get_file_path(to_absolute_path(file_path), file_name)
    
    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")
    
    try:
        with path.open("r", encoding="utf-8") as f:
            data = json.load(f)
        
        if not isinstance(data, dict):
            raise ValueError(f"Invalid JSON format: Expected a dictionary, got {type(data).__name__}")
        logging.debug(f"Dictionary loaded successfully from {path}")
        return data
    except json.JSONDecodeError as e:
        raise ValueError(f"Error decoding JSON file {path}: {e}")
    except IOError as e:
        raise IOError(f"Error reading file {path}: {e}")