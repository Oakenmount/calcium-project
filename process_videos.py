from glob import glob
from typing import List

import nd2
import os

import numpy as np
import pandas as pd
import torch
from skimage import io
from tqdm import tqdm
from numpy.typing import NDArray


def get_mask_centroids(mask: NDArray) -> List:
    coords = []
    for i in range(1, mask.max() + 1):
        cell_mask = mask == i
        centroid = np.transpose(cell_mask.nonzero()).mean(axis=0)
        coords.append([i - 1, centroid[1], centroid[0]])  # column, row -> x, y
    return coords


def process_video(vid_path: str, out_path: str = None, mask_path: str = None, exists_ok: bool = False):
    if mask_path is None:
        mask_path = vid_path[:-4] + "_cp_masks.png"
    if out_path is None:
        out_path = vid_path[:-4] + ".csv"

    # validate args
    if not exists_ok and os.path.exists(out_path):
        raise FileExistsError(f"{out_path} already exists")
    if not vid_path[-4:] == ".nd2":
        raise ValueError(f"{vid_path} is not an nd2 file")
    if not os.path.exists(mask_path):
        raise FileNotFoundError(f"{mask_path} not found")
    if not out_path[-4:] == ".csv":
        raise ValueError("out_path must be a .csv file")

    # make dirs if not exists
    out_dir = os.path.dirname(out_path)
    os.makedirs(out_dir, exist_ok=True)

    # load data
    vid = nd2.imread(vid_path).astype(np.int32)
    mask = io.imread(mask_path)

    # get spacial data
    coords = get_mask_centroids(mask)
    coords_df = pd.DataFrame(coords, columns=["cell_id", "x", "y"])
    coords_df.to_csv(out_path.replace(".csv", "_positions.csv"), index=False)

    # calc bottom 10% bg
    bg = mask == 0

    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    bg_t = torch.tensor(bg, dtype=torch.bool, device=device)
    vid_t = torch.tensor(vid, dtype=torch.float32, device=device)

    frame_vals = []
    for i in range(len(vid)):
        bg_vals = torch.masked_select(vid_t[i], bg_t)
        k = int(len(bg_vals) / 10)  # k = bottom 10%
        top_k_vals = torch.topk(bg_vals, k, largest=False).values
        frame_vals.append([i, top_k_vals.mean().item()])
    bg_df = pd.DataFrame(frame_vals, columns=["frame", "mean"])
    bg_df.to_csv(out_path.replace(".csv", "_bg.csv"), index=False)

    # get temporal data
    df_rows = []
    for i in tqdm(range(1, mask.max() + 1)):
        cell_mask = mask == i  # 0 is bg and last num is not included in loop above
        area = cell_mask.sum()
        cell_mask_t = torch.tensor(cell_mask, dtype=torch.bool, device=device)
        for frame in range(len(vid)):
            frame_masked = torch.masked_select(vid_t[frame], cell_mask_t)
            avg = frame_masked.mean().item()
            k = int(area / 10)  # k = top 10%
            top_k_vals = torch.topk(frame_masked, k).values
            top10 = top_k_vals.mean().item()
            # cell id, frame, mean signal, max signal, top10 signal
            df_rows.append([i - 1, frame, avg, frame_masked.max().item(), top10])

    df = pd.DataFrame(df_rows, columns=["cell_id", "frame", "mean", "max", "top10"])
    df.to_csv(out_path, index=False)


if __name__ == "__main__":
    pbar = tqdm(glob("data/**/*.nd2", recursive=True))
    for fpath in pbar:
        try:
            pbar.set_postfix_str(f"Processing {fpath}")
            process_video(fpath)
        except (FileExistsError, FileNotFoundError, ValueError) as e:
            print(e)
