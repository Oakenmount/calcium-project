from math import floor
from typing import Literal

import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
import seaborn as sns
from nptyping import NDArray
import plotly.express as px

# plotting config
sns.set(style="darkgrid", font_scale=1.5)
plt.rcParams['figure.figsize'] = (12, 5)


def smooth_timeseries(data: NDArray, window_size: int = 3) -> NDArray:
    """
    Smooth a time series using a sliding window.

    :param data: The input time series data.
    :type data: NDArray
    :param window_size: The size of the sliding window. Larger size results in smoother curves.
    :type window_size: int
    :return: The smoothed time series data.
    :rtype: NDArray
    """
    padded_data = np.pad(data, (window_size // 2, window_size // 2), mode='edge')
    kernel = np.ones(window_size) / window_size
    return np.convolve(padded_data, kernel, mode='valid')


def get_lower_rolling_mean(data: NDArray, window_size: int = 11, k_percent: float = 0.5) -> NDArray:
    """
    Calculate a rolling mean for each data point, using the lower k values within a window.

    :param data: The input data.
    :type data: NDArray
    :param window_size: The size of the rolling window.
    :type window_size: int
    :param k_percent: The percentage of lower values to consider in the window.
    :type k_percent: float
    :return: The array containing the lower rolling mean for each data point.
    :rtype: NDArray
    """
    if window_size % 2 == 0 or window_size < 1:
        raise ValueError("Window size must be an integer greater than 1")
    # init return arr
    lower_mean_arr = np.zeros_like(data)
    k = floor(window_size * k_percent)
    win_half = (window_size - 1) // 2
    for i in range(len(data)):
        # window bounds
        lower_bound = max(i - win_half, 0)
        upper_bound = min(i + win_half + 1, len(data))
        # data at window
        window = data[lower_bound:upper_bound]
        # get lower k values mean
        min_k = np.argpartition(window, k)[:k]
        lower_mean_arr[i] = window[min_k].mean()

    return lower_mean_arr


def plot_2D(df: pd.DataFrame):
    """
    Plot smoothed data.

    :param df: DataFrame containing data to be plotted.
    :type df: pd.DataFrame
    :return: None
    :rtype: None
    """
    ax = sns.lineplot(x='frame', y='processed', hue='cell_id', data=df, palette="tab10", legend=False)
    ax.set(xlabel='Frame', ylabel='∆F/F')
    plt.tight_layout()
    plt.show()


def plot_3D(df: pd.DataFrame):
    """
    Plot data in 3D.

    :param df: DataFrame containing data to be plotted.
    :type df: pd.DataFrame
    :return: None
    :rtype: None
    """
    fig = px.line_3d(df, x='frame', y='cell_id', z='processed', color='cell_id',
                     labels={'frame': 'Frame',
                             'processed': '∆F/F',
                             'cell_id': 'Cell'
                             })
    fig.show()


def process_raw_reads(fpath: str, quantity: Literal["mean", "max", "top10"] = "top10",
                      bg_path: str = None, subtract_bg: bool = True,
                      smoothing: int = 3, window_size: int = 11) -> pd.DataFrame:
    """
    Process raw reads from a CSV file, subtracting background and smoothing data.

    :param fpath: Path to the CSV file containing raw reads.
    :type fpath: str
    :param quantity: The type of quantity to consider.
    :type quantity: Literal["mean", "max", "top10"]
    :param bg_path: Path to the CSV file containing background data.
    :type bg_path: str, optional
    :param subtract_bg: Whether to subtract background data.
    :type subtract_bg: bool, optional
    :param smoothing: The size of the smoothing window.
    :type smoothing: int, optional
    :param window_size: The size of the rolling window for calculating the lower mean.
    :type window_size: int, optional
    :return: DataFrame containing processed data.
    :rtype: pd.DataFrame
    """
    df = pd.read_csv(fpath)
    if bg_path is None:
        bg_path = fpath.replace(".csv", "_bg.csv")
    df_bg = pd.read_csv(bg_path)

    smoothed_vals = []

    for cell_id, group_df in df.groupby('cell_id'):
        # Subtract values with background
        data = group_df[quantity].to_numpy()
        if subtract_bg:
            data -= df_bg['mean'].to_numpy()
        lower = get_lower_rolling_mean(data, window_size=window_size)
        normed = np.clip((data - lower) / lower, a_min=0, a_max=None)  # Can go below zero at boundaries.
        smoothed = smooth_timeseries(normed, smoothing)
        smoothed_vals.extend(smoothed)

    df['processed'] = smoothed_vals

    return df


df = process_raw_reads(r"C:\Users\LAB-ADMIN\Desktop\Control1\processed\Control1_001.csv")
plot_2D(df)