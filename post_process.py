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
    padded_data = np.pad(data, (window_size // 2, window_size // 2), mode='edge')
    kernel = np.ones(window_size) / window_size
    return np.convolve(padded_data, kernel, mode='valid')


def get_lower_rolling_mean(data: NDArray, window_size: int = 11, k_percent: float = 0.5) -> NDArray:
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


def process_raw_reads(fpath: str, quantity: Literal["mean", "max", "top10"] = "top10",
                      bg_path: str = None, out_file: str = None,
                      show_plot: bool = True, show_3D: bool = False):
    df = pd.read_csv(fpath)
    if bg_path is None:
        bg_path = fpath.replace(".csv", "_bg.csv")
    df_bg = pd.read_csv(bg_path)

    smoothed_vals = []

    for cell_id, group_df in df.groupby('cell_id'):
        # Subtract values with background
        data = group_df[quantity].to_numpy()  # - df_bg['mean'].to_numpy()
        lower = get_lower_rolling_mean(data, window_size=11)
        normed = np.clip((data - lower) / lower, a_min=0, a_max=None)  # Can go below zero at boundaries.
        smoothed = smooth_timeseries(normed, 3)
        smoothed_vals.extend(smoothed)
        plt.plot(group_df['frame'], smoothed, label=f'Cell {cell_id}')

    if show_plot:
        # Add labels and title
        plt.xlabel('Frame')
        plt.ylabel('∆F/F')
        plt.tight_layout()
        plt.show()

    df['smoothed'] = smoothed_vals

    if not out_file is None:
        df.to_csv(out_file, index=False)

    if show_3D:
        fig = px.line_3d(df, x='frame', y='cell_id', z='smoothed', color='cell_id',
                         labels={'frame': 'Frame',
                                 'smoothed': '∆F/F',
                                 'cell_id': 'Cell'
                                 })
        fig.show()


process_raw_reads("data/processed/exp_2/GPN1/GPN1_001.csv")
