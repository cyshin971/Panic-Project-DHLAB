"""
datetime_utils.py

This module provides utility functions for handling and formatting dates.
It includes functions to format a single date string and to format date columns in a pandas DataFrame.

Functions:
----------
- format_date(date: str, format='%Y-%m-%d') -> datetime.date:
    Converts a date string to a datetime.date object based on the specified format.

- format_date_df(df: pd.DataFrame, date_col: str, date_format: str) -> None:
    Formats the specified date column in the DataFrame to the given date format.
"""
import library.config as config
import logging

import datetime as dt
import pandas as pd

def format_date(date: str, format='%Y-%m-%d'):
    """
    Converts a date string to a datetime.date object based on the specified format.

    Parameters
    ----------
    date : str
        The date string to be converted.
    format : str, optional
        The format of the date string (default is '%Y-%m-%d').

    Returns
    -------
    datetime.date
        The converted date object.
    """
    return dt.datetime.strptime(date, format).date()

def format_date_df(df: pd.DataFrame, date_col: str, date_format: str) -> None:
    """
    Formats the specified date column in the DataFrame to the given date format.

    Parameters
    ----------
    df : pd.DataFrame
        The DataFrame containing the date column to format.
    date_col : str
        The name of the column containing date values.
    date_format : str
        The format to which the date column should be converted.

    Returns
    -------
    None
        This function modifies the DataFrame in place.

    Raises
    ------
    ValueError
        If the specified date column does not exist in the DataFrame or
        if the date parsing fails due to invalid date strings.
    """
    if date_col not in df.columns:
        raise ValueError(f"Column '{date_col}' not found in DataFrame.")
    try:
        df[date_col] = pd.to_datetime(df[date_col], format=date_format)
    except ValueError as e:
        raise ValueError(f"Error converting column '{date_col}' to datetime: {e}")

def filter_by_date_range(df: pd.DataFrame, start_date: str, end_date: str, col: str, copy: bool = True) -> pd.DataFrame:
    """
    Filter a DataFrame by a date range (inclusive).

    Parameters
    ----------
    df : pd.DataFrame
        The DataFrame to filter.
    start_date : str
        The minimum date (inclusive) in 'YYYY-MM-DD' format.
    end_date : str
        The maximum date (inclusive) in 'YYYY-MM-DD' format.
    col : str, optional
        The column name to filter by. Defaults to 'Order Date'.
    copy : bool, optional
        Whether to return a copy of the DataFrame. Defaults to True.

    Returns
    -------
    pd.DataFrame
        The filtered DataFrame containing only rows where the specified column's date is within the range.

    Raises
    ------
    ValueError
        If the specified column does not exist in the DataFrame.
    ValueError
        If the specified column is not of a datetime type.
    """
    if col not in df.columns:
        raise ValueError(f"Column '{col}' not found in DataFrame.")
    
    if df.empty:
        return df.copy() if copy else df

    # Ensure the column is in datetime format
    df_temp = df.copy() if copy else df
    if not pd.api.types.is_datetime64_any_dtype(df_temp[col]):
        try:
            df_temp[col] = pd.to_datetime(df_temp[col])
        except Exception as e:
            raise ValueError(f"Error converting column '{col}' to datetime: {e}")
    
    start_date = pd.to_datetime(start_date)
    end_date = pd.to_datetime(end_date)
    
    return df_temp[(df_temp[col] >= start_date) & (df_temp[col] <= end_date)]


def filter_by_month(df: pd.DataFrame, month: int, year: int, col: str, copy: bool = True) -> pd.DataFrame:
    """
    Filter a DataFrame by a specific month and year.

    Parameters
    ----------
    df : pd.DataFrame
        The DataFrame to filter.
    month : int
        The month to filter by (1-12).
    year : int
        The year to filter by (1900-2100).
    col : str, optional
        The column name to filter by. Defaults to 'Order Date'.
    copy : bool, optional
        Whether to return a copy of the DataFrame. Defaults to True.

    Returns
    -------
    pd.DataFrame
        The filtered DataFrame containing only rows where the specified column's month and year match the given values.

    Raises
    ------
    ValueError
        If the specified column does not exist in the DataFrame.
    ValueError
        If the month is not between 1 and 12.
    ValueError
        If the year is not between 1900 and 2100.
    ValueError
        If the specified column is not of a datetime type.
    """
    if month < 1 or month > 12:
        raise ValueError("Month must be between 1 and 12.")
    if year < 1900 or year > 2100:
        raise ValueError("Year must be between 1900 and 2100 (inclusive).")
    
    # Construct the start and end dates for the month
    start_date = f"{year}-{month:02d}-01"
    end_date = f"{year}-{month:02d}-{pd.Timestamp(start_date).days_in_month}"
    
    return filter_by_date_range(df, start_date, end_date, col=col, copy=copy)