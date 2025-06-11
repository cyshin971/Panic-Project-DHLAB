"""
pandas_utils.py

This module provides utility functions for working with pandas DataFrames. 
It includes functions to create empty DataFrames, read CSV files, add rows, 
find unique rows, filter DataFrames, remove columns, move columns, rearrange columns, 
and aggregate data.

Functions:
----------
- create_empty_df(columns: list[str] = None) -> pd.DataFrame:
    Creates an empty DataFrame with the specified columns.

- read_csv(file_path: Path) -> pd.DataFrame:
    Reads a CSV file from the given file path.

- add_row(df: pd.DataFrame, row: dict) -> None:
    Adds a row to the DataFrame in place.

- find_unique_row(df: pd.DataFrame, col: str, value) -> tuple:
    Finds the unique row in a DataFrame where the specified column matches the given value.

- filter_for_list(df: pd.DataFrame, column: str, values: list) -> pd.DataFrame:
    Filters a DataFrame based on whether the specified column's values are in the given list.

- remove_columns(df: pd.DataFrame, columns: list[str]) -> None:
    Removes the specified columns from the DataFrame in place.

- move_column(df: pd.DataFrame, column_name: str, new_position: int) -> None:
    Moves the specified column to the new position in the DataFrame in place.

- rearrange_columns(df: pd.DataFrame, columns: list[str]) -> None:
    Rearranges the columns of the DataFrame based on the specified order.

- aggregate_by_column(df: pd.DataFrame, group_col: str, agg_matrix: list[tuple]) -> pd.DataFrame:
    Aggregates the DataFrame based on the specified group column and aggregation matrix.
"""
import library.config as config
import logging

import pandas as pd

from pathlib import Path

pd.set_option('display.precision', 2)  # Set display precision

def create_empty_df(columns: list[str] = None) -> pd.DataFrame:
    """
    Creates an empty DataFrame with the specified columns.

    Parameters
    ----------
    columns : list of str, optional
        List of column names for the empty DataFrame. If not provided, defaults to an empty list.

    Returns
    -------
    pd.DataFrame
        An empty DataFrame with the specified columns.

    Raises
    ------
    ValueError
        If the provided columns are not a list of strings.
    """
    if columns is None:
        columns = []
    elif not all(isinstance(col, str) for col in columns):
        raise ValueError("All columns must be strings.")
    
    return pd.DataFrame(columns=columns)

def read_csv(file_path: Path) -> pd.DataFrame:
    """
    Reads a CSV file from the given file path.

    Parameters
    ----------
    file_path : Path
        The path to the CSV file.

    Returns
    -------
    pd.DataFrame
        A pandas DataFrame containing the data from the CSV file.

    Raises
    ------
    FileNotFoundError
        If the file does not exist at the given path.
    ValueError
        If the file is empty, corrupt, or cannot be parsed.
    """
    if not file_path.exists():
        raise FileNotFoundError(f"File {file_path} not found.")
    try:
        return pd.read_csv(file_path)
    except pd.errors.EmptyDataError:
        raise ValueError(f"The file {file_path} is empty or corrupt.")
    except pd.errors.ParserError as e:
        raise ValueError(f"Error parsing the file {file_path}: {e}")

# TODO: handle cases when there are columns in the row that are not in the DataFrame
def add_row(df: pd.DataFrame, row: dict) -> None:
    """
    Adds a row to the DataFrame in place.
    This function modifies the DataFrame in place.

    Parameters
    ----------
    df : pd.DataFrame
        The input DataFrame.
    row : dict
        A dictionary where keys are column names and values are the corresponding row values.

    Raises
    ------
    ValueError
        If the row dictionary keys do not match the DataFrame columns.
    """
    missing_cols = set(df.columns) - set(row.keys())
    for col in missing_cols:
        row[col] = None
    
    df.loc[len(df)] = row

def find_unique_row(df: pd.DataFrame, col: str, value) -> tuple:
    """
    Finds the unique row in a DataFrame where the specified column matches the given value.

    Parameters
    ----------
    df : pd.DataFrame
        The DataFrame to search.
    col : str
        The name of the column in which to look for the value.
    value : Any
        The value to be matched in the specified column.

    Returns
    -------
    tuple
        A tuple (index, row) where `index` is the index of the matching row and `row` is a pandas Series containing the row's data.
        If no unique row is found, returns (None, None).

    Raises
    ------
    KeyError
        If the specified column does not exist in the DataFrame.
    ValueError
        If no row or multiple rows are found with the specified value.
    """
    if col not in df.columns:
        raise KeyError(f"Column '{col}' does not exist in the DataFrame.")
    
    matching_rows = df[df[col] == value]
    
    if matching_rows.shape[0] == 0:
        raise ValueError(f"No row found with {col} == {value}.")
    elif matching_rows.shape[0] != 1:
        raise ValueError(f"Expected exactly one row with {col} == {value}, but found {matching_rows.shape[0]}.")
    
    index = matching_rows.index[0]
    return index, matching_rows.iloc[0]

def filter_for_cols(df: pd.DataFrame, columns: list[str]) -> pd.DataFrame:
    """
    Filters a DataFrame to include only the specified columns.

    Parameters
    ----------
    df : pd.DataFrame
        The DataFrame to filter.
    columns : list of str
        The list of column names to keep in the DataFrame.

    Returns
    -------
    pd.DataFrame
        A DataFrame containing only the specified columns.

    Raises
    ------
    ValueError
        If any specified column is not present in the DataFrame.
    """
    missing_cols = [col for col in columns if col not in df.columns]
    if missing_cols:
        raise ValueError(f"Missing columns: {missing_cols}")

    return df[columns].copy()

def filter_for_list(df: pd.DataFrame, column: str, values: list) -> pd.DataFrame:
    """
    Filters a DataFrame based on whether the specified column's values are in the given list.

    Parameters
    ----------
    df : pd.DataFrame
        The DataFrame to filter.
    column : str
        The column name on which to filter.
    values : list
        The list of values to keep.

    Returns
    -------
    pd.DataFrame
        A filtered DataFrame containing only rows where the column's value is in the list.

    Raises
    ------
    ValueError
        If the specified column is not found in the DataFrame.
    """
    if column not in df.columns:
        raise ValueError(f"Column '{column}' not found in DataFrame")

    # Convert values to match column dtype if it's datetime
    if pd.api.types.is_datetime64_any_dtype(df[column]):
        values = pd.to_datetime(values, errors='coerce')  # Ensure proper conversion

    return df[df[column].isin(values)]

def remove_columns(df: pd.DataFrame, columns: list[str], ignore_missing = False) -> None:
    """
    Removes the specified columns from the DataFrame in place.

    Parameters
    ----------
    df : pd.DataFrame
        The input DataFrame.
    columns : list of str
        List of column names to remove.

    Returns
    -------
    None
        This function modifies the DataFrame in place.

    Raises
    ------
    ValueError
        If any specified column is not present in the DataFrame.
    """
    missing_cols = [col for col in columns if col not in df.columns]
    if missing_cols:
        if ignore_missing:
            columns = [col for col in columns if col not in missing_cols]
            logging.debug(f"Columns not found in DataFrame: {missing_cols}. Ignoring.")
        else:
            raise ValueError(f"Missing columns: {missing_cols}")

    df.drop(columns=columns, inplace=True)
    df.reset_index(drop=True, inplace=True)

def move_column(df: pd.DataFrame, column_name: str, new_position: int) -> None:
    """
    Moves the specified column to the new position in the DataFrame in place.

    Parameters
    ----------
    df : pd.DataFrame
        The DataFrame to modify.
    column_name : str
        The name of the column to move.
    new_position : int
        The new index position for the column (0-indexed).

    Returns
    -------
    None
        This function modifies the DataFrame in place.

    Raises
    ------
    ValueError
        If the specified column does not exist in the DataFrame or
        if the new position is out of bounds.
    """
    if column_name not in df.columns:
        raise ValueError(f"Column '{column_name}' not found in DataFrame.")
    if new_position < 0:
        # If new_position is negative, it will be treated as an offset from the end.
        new_position += len(df.columns)
    if not (0 <= new_position < len(df.columns)):
        raise ValueError(f"New position '{new_position}' is out of bounds.")

    # Get the list of current columns.
    cols = list(df.columns)
    # Remove the target column and insert it at the desired position.
    cols.insert(new_position, cols.pop(cols.index(column_name)))
    # Reinitialize the DataFrame in place with the new column order.
    df.__init__(df[cols])

def rearrange_columns(df: pd.DataFrame, columns: list[str]) -> None:
    """
    Rearranges the columns of the DataFrame based on the specified order.

    Parameters
    ----------
    df : pd.DataFrame
        The input DataFrame.
    columns : list of str
        The list of column names in the desired order.

    Returns
    -------
    None
        This function modifies the DataFrame in place.
    """
    # Add missing columns with None values
    for col in columns:
        if col not in df.columns:
            df[col] = None

    # Remove any extra columns not in the specified list
    extra_cols = [col for col in df.columns if col not in columns]
    if extra_cols:
        df.drop(columns=extra_cols, inplace=True)

    # Reorder the columns based on the specified list in place
    for i, col in enumerate(columns):
        move_column(df, col, i)

def aggregate_by_column(df: pd.DataFrame, group_col: str, agg_matrix: list[tuple]) -> pd.DataFrame:
    """
    Aggregates the DataFrame based on the specified group column and aggregation matrix.

    Parameters
    ----------
    df : pd.DataFrame
        The input DataFrame.
    group_col : str
        The column name to group by (e.g., 'Symbol').
    agg_matrix : list of tuples
        A list of tuples where each tuple contains:
            (new_col_name, original_col_name, aggregation_function)
        - new_col_name (str): The name for the new column in the aggregated DataFrame.
        - original_col_name (str): The column name in the original DataFrame to aggregate.
        - aggregation_function (str or callable): The aggregation function to apply.

    Returns
    -------
    pd.DataFrame
        The aggregated DataFrame with renamed columns.

    Raises
    ------
    ValueError
        If the group column is not found in the DataFrame,
        if a specified column for aggregation is not found,
        or if the aggregation function is invalid.

    Notes
    -----
    Supported Aggregation Functions
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    - Basic Aggregations:
        'first', 'last', 'sum', 'mean', 'median', 'min', 'max', 'count', 'nunique'
    - Statistical:
        'std', 'var', 'skew', 'kurt'
    - String Operations (for categorical/text columns):
        'unique', 'mode'
    - Custom Lambda Functions:
        You can also pass custom callables for advanced aggregations.

    Example
    -------
    >>> agg_matrix = [
    ...     ('Total Value', 'Value', 'sum'),
    ...     ('Avg Value', 'Value', 'mean'),
    ...     ('Earliest Date', 'Date', 'min'),
    ...     ('Latest Date', 'Date', 'max'),
    ...     ('Custom', 'Value', lambda x: x.max() - x.min())
    ... ]
    >>> df_result = aggregate_by_column(df, 'Category', agg_matrix)
    """
    if group_col not in df.columns:
        raise ValueError(f"Group column '{group_col}' not found in DataFrame.")

    valid_aggregations = {
        'first', 'last', 'sum', 'mean', 'median', 'min', 'max', 'count',
        'nunique', 'std', 'var', 'skew', 'kurt', 'unique', 'mode'
    }

    # Use NamedAgg to ensure custom column names are preserved
    agg_kwargs = {}
    for new_col, orig_col, func in agg_matrix:
        if orig_col not in df.columns:
            raise ValueError(f"Column '{orig_col}' not found in DataFrame for aggregation.")

        if isinstance(func, str):
            if func not in valid_aggregations:
                raise ValueError(
                    f"Invalid aggregation function '{func}'. Must be one of "
                    f"{valid_aggregations} or a callable."
                )
        elif not callable(func):
            raise ValueError(
                f"Invalid type for aggregation function '{func}'. "
                f"Must be a string or callable."
            )

        agg_kwargs[new_col] = pd.NamedAgg(column=orig_col, aggfunc=func)

    aggregated_df = df.groupby(group_col).agg(**agg_kwargs).reset_index()

    return aggregated_df