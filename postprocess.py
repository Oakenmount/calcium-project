from math import floor
from typing import Literal

import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
import seaborn as sns
from nptyping import NDArray
import plotly.express as px
from scipy.signal import find_peaks, peak_widths

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


def plot_2D(df: pd.DataFrame, show_peaks: bool=True,
            peak_prominence: float=0.02,
            peak_abs_height: float=0.02,
            peak_rel_height: float=0.5):
    for cell_id, group_df in df.groupby('cell_id'):
        plt.plot(group_df['frame'], group_df['processed'], label=f'Cell {cell_id}')
        if show_peaks:
            data_arr = group_df['processed'].to_numpy()
            peaks, peak_info = find_peaks(data_arr, height = peak_abs_height, prominence = peak_prominence)
            widths = peak_widths(data_arr, peaks, rel_height = peak_rel_height)
            plt.plot(peaks, data_arr[peaks], '.', color="black")
            plt.hlines(*widths[1:], color="grey", linestyle="--", alpha=0.5)

    plt.xlabel('Frame')
    plt.ylabel('∆F/F')
    plt.tight_layout()
    plt.show()

def plot_image(df: pd.DataFrame):
    # Get unique cell_ids and frames
    cell_ids = df['cell_id'].unique()
    frames = df['frame'].unique()

    # Create a blank image matrix
    image = np.zeros((len(cell_ids), len(frames)))
    # Fill in the image matrix with signal values
    for index, row in df.iterrows():
        cell_index = np.where(cell_ids == row['cell_id'])[0][0]
        frame_index = np.where(frames == row['frame'])[0][0]
        image[cell_index, frame_index] = row['processed']

    # Plot the image
    plt.imshow(image, aspect='auto', cmap='viridis', origin='lower')
    plt.xlabel('Frame')
    plt.ylabel('Cell ID')
    plt.title('Signal Intensity')
    plt.colorbar(label='∆F/F')
    plt.tight_layout()
    plt.show()

def plot_3D(df: pd.DataFrame, show_peaks: bool=True,
            peak_prominence: float=0.02,
            peak_abs_height: float=0.02,
            peak_rel_height: float=0.5):
    """
    Plot data in 3D with optional peak visualization.

    :param df: DataFrame containing data to be plotted.
    :type df: pd.DataFrame
    :param show_peaks: Whether to show peaks in the plot.
    :type show_peaks: bool, optional
    :param peak_prominence: Minimum prominence of peaks.
    :type peak_prominence: float, optional
    :param peak_abs_height: Absolute height of peaks.
    :type peak_abs_height: float, optional
    :param peak_rel_height: Relative height of peaks.
    :type peak_rel_height: float, optional
    :return: None
    :rtype: None
    """
    fig = px.line_3d(df, x='frame', y='cell_id', z='processed', color='cell_id',
                     labels={'frame': 'Frame',
                             'processed': '∆F/F',
                             'cell_id': 'Cell'
                             })

    if show_peaks:
        for cell_id, group_df in df.groupby('cell_id'):
            data_arr = group_df['processed'].to_numpy()
            peaks, peak_info = find_peaks(data_arr, height=peak_abs_height, prominence=peak_prominence)
            widths = peak_widths(data_arr, peaks, rel_height=peak_rel_height)
            fig.add_scatter3d(x=peaks, y=[cell_id] * len(peaks), z=data_arr[peaks],
                              mode='markers', marker=dict(color='black', size=2), legendgroup=cell_id, showlegend=False)
            if len(widths[0]) > 0:
                for i in range(widths[0].shape[0]):
                    fig.add_scatter3d(x=[widths[2][i], widths[3][i]],
                                      y=[cell_id,cell_id],
                                      z=[widths[1][i],widths[1][i]],
                                      mode="lines",
                                      line=dict(color='black', width=2),
                                      legendgroup=cell_id,
                                      showlegend=False
                    )

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

#df = process_raw_reads(r"C:\Users\LAB-ADMIN\Desktop\Control1\processed\Control1_001.csv")
#plot_image(df)
#plot_3D(df, show_peaks=True)