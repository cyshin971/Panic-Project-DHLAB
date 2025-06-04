"""
This module provides utility functions for handling RTF files.

Functions:
    rtf_to_plain(file_path: str) -> str:
        Converts an RTF file to plain text.
"""
import library.config as config
import logging

from striprtf.striprtf import rtf_to_text

from library.path_utils import to_absolute_path

def rtf_to_plain(file_path: str) -> str:
    """
    Converts an RTF file to plain text.

    Args:
        file_path (str): The path to the RTF file.

    Returns:
        str: The plain text extracted from the RTF file, or None if the file does not exist.

    Raises:
        FileNotFoundError: If the file does not exist at the given path.
    """
    absolute_path = to_absolute_path(file_path)
    plain_text = None
    if absolute_path.exists():
        rtf_content = absolute_path.read_text(encoding="utf-8")
        plain_text = rtf_to_text(rtf_content)
    else:
        print(f"File {file_path} not found.")
    return plain_text