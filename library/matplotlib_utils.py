import library.config as config
import logging

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.axes import Axes
from typing import Sequence, Optional, Tuple, Any
import pandas as pd

def plot_bar_df(df: pd.DataFrame, x_col: str, y_col: str, *,
                xlabel: str = None,
                ylabel: str = None,
                title: str = None,
                figsize: tuple[float, float] = (8, 4),
                rotation: float = 0,
                percentage: bool = False) -> None:
    """
    Plot a bar chart from two columns in a DataFrame.

    Parameters
    ----------
    df : pandas.DataFrame
        The DataFrame containing the data to plot.
    x_col : str
        The name of the column to use for the x-axis (categories).
    y_col : str
        The name of the column to use for the y-axis (values).
    xlabel : str, optional
        Label for the x-axis. If None, uses x_col.
    ylabel : str, optional
        Label for the y-axis. If None, uses y_col.
    title : str, optional
        Title of the plot. If None, no title is set.
    figsize : tuple of float, default (8, 4)
        Figure size in inches, as (width, height).
    rotation : float, default 0
        Rotation angle of x-tick labels, in degrees.
    percentage : bool, default False
        If True, adds percentage labels to each bar.

    Returns
    -------
    None
        Displays the bar chart.

    Raises
    ------
    KeyError
        If x_col or y_col is not found in the DataFrame.

    Examples
    --------
    >>> df = pd.DataFrame({
    ...     'fruit': ['apple', 'banana', 'cherry'],
    ...     'count': [10, 15, 7]
    ... })
    >>> plot_bar(df, 'fruit', 'count',
    ...          xlabel='Fruit Type',
    ...          ylabel='Quantity',
    ...          title='Fruit Counts',
    ...          percentage=True)
    """
    if x_col not in df.columns:
        raise KeyError(f"Column '{x_col}' not found in DataFrame.")
    if y_col not in df.columns:
        raise KeyError(f"Column '{y_col}' not found in DataFrame.")

    x = df[x_col].astype(str)
    y = df[y_col]

    plt.figure(figsize=figsize)
    bars = plt.bar(x, y)
    plt.xticks(rotation=rotation)

    plt.xlabel(xlabel if xlabel is not None else x_col)
    plt.ylabel(ylabel if ylabel is not None else y_col)
    if title:
        plt.title(title, fontweight='bold')

    if percentage:
        total = y.sum()
        for bar in bars:
            height = bar.get_height()
            plt.text(bar.get_x() + bar.get_width() / 2, height,
                     f'{(height / total) * 100:.1f}%',
                     ha='center', va='bottom', fontsize=10)

    # Remove top and right spines
    plt.gca().spines['top'].set_visible(False)
    plt.gca().spines['right'].set_visible(False)
    
    plt.tight_layout()
    plt.show()

def plot_pie_df(df: pd.DataFrame,
                columns: Sequence[Tuple[str, str]],
                *,
                figsize: Tuple[float, float] = (6, 6),
                titles: Optional[Sequence[str]] = None,
                percentage: bool = True) -> None:
    """
    Plot multiple pie charts as subplots based on a list of (labels_col, values_col) tuples.

    Parameters
    ----------
    df : pandas.DataFrame
        The DataFrame containing the data.
    columns : sequence of tuple of str
        A list of (labels_col, values_col) tuples specifying the columns for each pie chart.
    figsize : tuple of float, default (6, 6)
        Base figure size in inches. The total figure size will scale with the number of subplots.
    titles : sequence of str, optional
        Titles for each subplot. If None, no titles are set.
    percentage : bool, default True
        If True, display percentage labels on the slices.

    Returns
    -------
    None
        Displays the pie charts.

    Raises
    ------
    KeyError
        If any column in `columns` is not found in `df`.
    ValueError
        If the length of `titles` does not match the length of `columns`.
    """
    num_charts = len(columns)
    if titles and len(titles) != num_charts:
        raise ValueError("`titles` must have the same length as `columns`.")

    # Determine the grid size for subplots
    rows = int(num_charts**0.5)
    cols = (num_charts + rows - 1) // rows

    # Create the figure and axes
    fig, axes = plt.subplots(rows, cols, figsize=(figsize[0] * cols, figsize[1] * rows))
    axes = axes.flatten() if num_charts > 1 else [axes]

    for i, (labels_col, values_col) in enumerate(columns):
        if labels_col not in df.columns:
            raise KeyError(f"Column '{labels_col}' not found in DataFrame.")
        if values_col not in df.columns:
            raise KeyError(f"Column '{values_col}' not found in DataFrame.")

        labels = df[labels_col].astype(str).tolist()
        values = df[values_col].tolist()

        ax = axes[i]
        ax.pie(
            values,
            labels=labels,
            autopct=('%1.1f%%' if percentage else None),
            startangle=90
        )

        if titles:
            ax.set_title(titles[i], fontweight='bold')

    # Hide unused subplots if any
    for j in range(num_charts, len(axes)):
        axes[j].axis('off')

    plt.tight_layout()
    plt.show()

def plot_pie_chart(labels: Sequence[str],
                   values: Sequence[float],
                   *,
                   ax: Optional[Axes] = None,
                   figsize: Tuple[float, float] = (6, 6),
                   title: Optional[str] = None,
                   percentage: bool = True) -> Axes:
    """
    Plot a pie chart given lists of labels and values, on a given Axes.

    Parameters
    ----------
    labels : sequence of str
        The labels for each slice of the pie chart.
    values : sequence of float
        The numeric values for each slice of the pie chart.
    ax : matplotlib.axes.Axes, optional
        The Axes to draw the pie chart on. If None, a new figure+axes is created.
    figsize : tuple of float, default (6, 6)
        Figure size in inches, only used if `ax` is None.
    title : str, optional
        Title of the chart. If None, no title is set.
    percentage : bool, default True
        If True, displays percentage labels on the pie slices.

    Returns
    -------
    ax : matplotlib.axes.Axes
        The Axes containing the pie chart (for further customization).

    Raises
    ------
    ValueError
        If `labels` and `values` have different lengths.

    Examples
    --------
    >>> labels = ['apple', 'banana', 'cherry']
    >>> values = [10, 15, 7]
    >>> fig, ax = plt.subplots(figsize=(8, 4))
    >>> plot_pie_chart(labels, values, ax=ax, title='Fruit Distribution')
    >>> fig.tight_layout()
    """
    if len(labels) != len(values):
        raise ValueError("`labels` and `values` must be the same length.")

    if ax is None:
        fig, ax = plt.subplots(figsize=figsize)

    ax.pie(
        values,
        labels=labels,
        autopct=('%1.1f%%' if percentage else None),
        startangle=90
    )

    if title:
        ax.set_title(title, fontweight='bold')

    return ax

def plot_histogram_of_counts(column: pd.Series,
                            title: Optional[str] = None,
                            figsize: Tuple[float, float] = (10, 4),
                            xlabel: Optional[str] = None,
                            ylabel: str = "Frequency",
                            ymax: Optional[int] = None,
                            xmax: Optional[int] = None,
                            bins_step: int = 5,
                            zero_start: bool = True,
                            exclude_zero: bool = False,
                            color: str = 'blue') -> None:
    """
    Plot a histogram of counts for a given pandas Series (column), showing only nonzero values.

    Parameters
    ----------
    column : pandas.Series
        The data column to plot. Only nonzero values are included.
    title : str, optional
        Title of the plot. If None, uses 'Histogram of <column name>'.
    figsize : tuple of float, default (10, 4)
        Size of the figure in inches, as (width, height).
    xlabel : str, optional
        Label for the x-axis. If None, uses the column name.
    ylabel : str, default "Frequency"
        Label for the y-axis.
    ymax : int, optional
        Maximum value for the y-axis. If None, auto-scales based on data.
    xmax : int, optional
        Maximum value for the x-axis. If None, auto-scales based on data.
    bins_step : int, default 5
        Step size for x-tick labels.
    zero_start : bool, default True
        If True, histogram x-axis starts at zero.
    exclude_zero : bool, default False
        If True, exclude zero values from the histogram.
    color : str, default 'blue'
        Color of the histogram bars.

    Returns
    -------
    None
        Displays the histogram.

    Notes
    -----
    If there are no nonzero values in the column, the function prints a message and does not plot.

    Examples
    --------
    >>> s = pd.Series([0, 1, 2, 2, 3, 5, 0, 7])
    >>> plot_histogram_of_counts(s, title="Value Distribution")
    """
    if exclude_zero:
        data = column[column > 0]
    else:
        data = column[column >= 0]
    if data.empty:
        logging.warning("No data to plot (all values are zero or excluded).")
        return

    min_val = int(data.min())
    max_val = int(data.max())
    if zero_start:
        min_val = 0  # Start from zero if specified
    if xmax is not None:
        max_val = xmax
    bins = np.arange(min_val, max_val + 2)  # +2 to include max in bin edges

    plt.figure(figsize=figsize)
    plt.hist(data, bins=bins, color=color, alpha=0.7)
    plt.title(title or f'Histogram of {column.name}')
    plt.xlabel(xlabel or column.name)
    plt.ylabel(ylabel)
    plt.grid(axis='y', alpha=0.75)
    plt.xticks(np.arange(min_val, max_val + 1, bins_step))
    if ymax is not None:
        plt.ylim(top=ymax)
    if xmax is not None:
        plt.xlim(right=xmax)
    plt.tight_layout()
    plt.show()