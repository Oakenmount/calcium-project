from typing import List

import nd2
import os

import numpy as np
import pandas as pd
from skimage import io
from tqdm import tqdm
from numpy.typing import NDArray


def get_mask_centroids(mask: NDArray) -> List:
    coords = []
    for i in range(mask.max()):
        cell_mask = mask == (i + 1)
        centroid = np.transpose(cell_mask.nonzero()).mean(axis=0)
        coords.append([i, centroid[1], centroid[0]])  # column, row -> x, y
    return coords


def process_video(vid_path: str, out_path: str, exists_ok: bool = False):
    # validate args
    if not exists_ok and os.path.exists(out_path):
        raise FileExistsError(f"{out_path} already exists")
    if not vid_path[-4:] == ".nd2":
        raise ValueError(f"{vid_path} is not an nd2 file")
    mask_path = vid_path[:-4] + "_cp_masks.png"
    if not os.path.exists(mask_path):
        raise FileNotFoundError(f"{mask_path} not found")
    if not out_path[-4:] == ".csv":
        raise ValueError("out_path must be a .csv file")

    # make dirs if not exists
    out_dir = os.path.dirname(out_path)
    os.makedirs(out_dir, exist_ok=True)

    # load data
    vid = nd2.imread(vid_path)
    mask = io.imread(mask_path)

    # get spacial data
    coords = get_mask_centroids(mask)
    coords_df = pd.DataFrame(coords, columns=["cell_id", "x", "y"])
    coords_df.to_csv(out_path.replace(".csv", "_positions.csv"), index=False)

    # calc bg
    bg = (mask == 0)
    frame_vals = []
    for i in range(len(vid)):
        frame_vals.append([i, vid[i, bg].mean()])
    bg_df = pd.DataFrame(frame_vals, columns=["frame", "mean"])
    bg_df.to_csv(out_path.replace(".csv", "_bg.csv"), index=False)

    # get temporal data
    df_rows = []
    for i in tqdm(range(mask.max())):
        cell_mask = mask == (i + 1)  # 0 is bg and last num is not included in loop above
        area = cell_mask.sum()
        vid_masked = np.zeros_like(vid)
        vid_masked[:, cell_mask] = vid[:, cell_mask]
        for frame in range(len(vid)):
            frame_masked = vid_masked[frame, cell_mask].ravel()
            avg = frame_masked.sum() / area
            k = int(area / 10)  # k = top10
            idx = np.argpartition(frame_masked, -k)[-k:]
            top10 = frame_masked[idx]
            # cell id, frame, mean signal, max signal, top10 signal
            df_rows.append([i, frame, avg, frame_masked.max(), top10.mean()])
        if i > 3:
            break
    df = pd.DataFrame(df_rows, columns=["cell_id", "frame", "mean", "max", "top10"])
    df.to_csv(out_path, index=False)


if __name__ == "__main__":
    process_video("data/raw/exp_1/GPN1/GPN1_001.nd2", "data/processed/exp_1/GPN1/GPN1_001.csv", exists_ok=True)
