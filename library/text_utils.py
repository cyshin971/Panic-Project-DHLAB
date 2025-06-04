"""
text_utils.py

This module provides utility functions for handling text and numerical data.
It includes functions to load numerical data into a NumPy array, save text to a plain text file,
and save a Pandas DataFrame to a CSV file.

Functions:
- load_np_data(file_path: str, delimiter: str = ",") -> np.ndarray:
    Load numerical data from a text file into a NumPy array.
- save_plain_text(text: str, save_path: str, file_name: str, suffix: str = "txt") -> Path:
    Save the given text to a plain text file.
- save_as_csv(df, save_path: str, file_name: str, index: bool = False) -> Path:
    Save a Pandas DataFrame to a CSV file.
"""
import library.config as config
import logging

import numpy as np
from pathlib import Path

from library.path_utils import make_dir, to_absolute_path

def load_np_data(file_path: str, delimiter: str = ",") -> np.ndarray:
    """
    Load numerical data from a text file into a NumPy array.

    Args:
        file_path (str): The path to the file containing numerical data.
        delimiter (str, optional): The delimiter used in the file. Defaults to ','.

    Returns:
        np.ndarray: The loaded NumPy array.
    """
    absolute_path = to_absolute_path(file_path)
    return np.loadtxt(absolute_path, delimiter=delimiter)

def save_plain_text(text: str, save_path: str, file_name: str, suffix: str = "txt") -> Path:
    """
    Save the given text to a plain text file.

    This function creates the necessary directory if it doesn't exist,
    constructs the full file path, and writes the text to the file with UTF-8 encoding.

    Args:
        text (str): The text content to be saved.
        save_path (str): The directory path where the file will be saved.
        file_name (str): The name of the file to be saved.
        suffix (str, optional): The file extension. Defaults to "txt".

    Returns:
        Path: The full path of the saved file.
    """
    file_name = f"{file_name}.{suffix}"
    dir_path = make_dir(save_path)
    file_path = dir_path / file_name
    file_path.write_text(text, encoding="utf-8")
    logging.debug(f"Saved {file_name} to {dir_path}")
    return file_path

def save_as_csv(df, save_path: str, file_name: str, index: bool = False) -> Path:
    """
    Save a Pandas DataFrame to a CSV file.

    This function ensures the directory exists before saving the DataFrame as a CSV file.

    Args:
        df (pd.DataFrame): The DataFrame to be saved.
        save_path (str): The directory path where the file will be saved.
        file_name (str): The name of the file to be saved.
        index (bool, optional): Whether to include row indices in the saved CSV file. Defaults to False.

    Returns:
        Path: The full path of the saved CSV file.
    """
    file_name = f"{file_name}.csv"
    dir_path = make_dir(save_path)
    file_path = dir_path / file_name
    df.to_csv(file_path, index=index)
    logging.debug(f"Saved {file_name} to {dir_path}")
    return file_path