"""
path_utils.py

This module provides utility functions for working with file paths and directories in a project.
It includes functions to determine the project root, manage files and directories, and handle paths.

Features:
- Identify the project root directory.
- Convert relative paths to absolute paths.
- Construct absolute file paths.
- Clear and delete directories safely.
- Create directories with error handling.
- Delete files with logging and exception handling.

Logging is configured via the config module.
"""

import config as config
import logging

from pathlib import Path
from typing import Union


from typing import Union, Optional
from pathlib import Path

def get_project_root() -> Path:
    """
    Determines the project root by searching for a known marker file (e.g., .git).
    If no marker is found, it defaults to the directory containing this script.
    
    Returns:
        Path: Absolute path to the project root.
    """
    try:
        current_dir = Path(__file__).parent.resolve()
    except NameError:
        logging.warning("`__file__` is not defined. Defaulting to current working directory.")
        return Path.cwd()  # Fallback if __file__ is unavailable
    
    while current_dir != current_dir.parent:  # Stop at filesystem root
        if (current_dir / ".git").exists() or (current_dir / ".gitignore").exists():
            return current_dir
        current_dir = current_dir.parent
    
    return Path.cwd()  # Final fallback to working directory

# Cache the project root
PROJECT_ROOT = get_project_root()

def to_absolute_path(relative_path: Union[str, Path]) -> Path:
    """
    Converts a relative path to an absolute path relative to the project root.

    Args:
        relative_path (str | Path): The relative path.
    
    Returns:
        Path: The absolute path.
    """
    return (PROJECT_ROOT / Path(relative_path)).resolve()


from typing import Union, Optional
from pathlib import Path

def get_file_path(dir_str: Union[str, Path], file_name: Optional[str] = None) -> Path:
    """
    Constructs an absolute path to a directory or file.

    Args:
        dir_str (str | Path):
            The (relative) directory path.
        file_name (str, optional):
            The name of the file within that directory.
            If None, returns only the directory path.
    
    Returns:
        Path: The absolute path to the directory or directory/file.
    """
    base = to_absolute_path(dir_str)  # 이미 구현된 절대경로 변환 함수
    return base if file_name is None else base / file_name

def clear_dir(dir_str: Union[str, Path], delete: bool = False):
    """
    Clears all files and subdirectories in the specified directory.
    If `delete=True`, the directory itself is removed after clearing.

    Args:
        dir_str (str | Path): The directory path to clear.
        delete (bool, optional): Whether to delete the directory after clearing. Defaults to False.    
    
    Returns:
        None
    """
    directory = to_absolute_path(dir_str)

    if not directory.exists() or not directory.is_dir():
        logging.warning(f"Directory not found or is not a directory: {directory}")
        return
    
    for item in directory.iterdir():
        try:
            if item.is_file():
                item.unlink()
                logging.debug(f"Deleted file: {item}")
            elif item.is_dir():
                clear_dir(item, delete=delete)  # Recursively clear subdirectories
        except PermissionError:
            logging.error(f"Permission denied: {item}")
        except OSError as e:
            logging.error(f"Failed to remove {item}: {e}")

    if delete:
        try:
            directory.rmdir()
            logging.debug(f"Deleted directory: {directory}")
            return
        except OSError:
            # TODO: Handle specific cases where directory cannot be deleted
            logging.error(f"Could not delete {directory}, it may not be empty.")

def delete_file(file_str: Union[str, Path]):
    """
    Deletes a specified file if it exists.

    Args:
        file_str (str | Path): The file path to delete.
    """
    file = to_absolute_path(file_str)
    if file.exists() and file.is_file():
        try:
            file.unlink()
            logging.debug(f"Deleted file: {file}")
        except OSError as e:
            logging.error(f"Failed to delete {file}: {e}")
    else:
        logging.warning(f"File not found: {file}")

def make_dir(dir_str: Union[str, Path]) -> Path:
    """
    Creates a directory (including parent directories if needed).
    
    Args:
        dir_str (str | Path): The directory path to create.
    
    Returns:
        Path: The absolute path of the created directory.
    """
    dir_path = to_absolute_path(dir_str)
    try:
        if not dir_path.exists():
            dir_path.mkdir(parents=True, exist_ok=True)
            logging.debug(f"Created directory: {dir_path}")
    except OSError as e:
        logging.error(f"Failed to create directory {dir_path}: {e}")
    
    return dir_path

def get_files_in_dir(dir_str: Union[str, Path], ext: str = '') -> list:
    """
    Retrieves a list of files in the specified directory with an optional file extension filter.
    
    Args:
        dir_str (str | Path): The directory path to search.
        ext (str, optional): The file extension to filter by. Defaults to ''.
    
    Returns:
        list: A list of file names.
    """
    dir_path = to_absolute_path(dir_str)
    if not dir_path.is_dir():
        logging.warning(f"Directory not found: {dir_path}")
        return []
    
    files = [f.name for f in dir_path.iterdir() if f.is_file() and (f.suffix == ext or not ext)]
    return files