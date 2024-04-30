from math import floor

import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
import seaborn as sns
from nptyping import NDArray

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


def process_raw_reads(fpath: str, bg_path: str = None):
    df = pd.read_csv(fpath)
    if bg_path is None:
        bg_path = fpath.replace(".csv", "_bg.csv")
    df_bg = pd.read_csv(bg_path)

    for cell_id, group_df in df.groupby('cell_id'):
        # Subtract values with background
        data = group_df['mean'].to_numpy()  # - df_bg['mean'].to_numpy()
        lower = get_lower_rolling_mean(data)
        normed = (data - lower) / lower
        smoothed = smooth_timeseries(normed, 3)
        plt.plot(group_df['frame'], smoothed, label=f'Cell {cell_id}')

    # Add labels and title
    plt.xlabel('Frame')
    plt.ylabel('∆F/F')
    plt.legend()
    plt.grid(True)

    # Show plot
    plt.show()


process_raw_reads("data/processed/exp_1/GPN1/GPN1_001.csv")
