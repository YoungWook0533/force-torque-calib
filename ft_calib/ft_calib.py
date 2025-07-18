#!/usr/bin/env python3
# fts_calib_from_file.py
# ---------------------------------------------------------------
# Compute bias and COM of a force/torque sensor from a 24‑pose
# gravity data set whose wrenches are already in the sensor frame.
# ---------------------------------------------------------------
import sys
import re
import numpy as np

# ---------- parameters you might want to change ----------
MASS = 0.347        # [kg] sensor (or tool) mass

# ---------- helper to parse one line with 6 numbers ----------
W6 = re.compile(r'[-+]?[0-9]*\.?[0-9]+(?:[eE][-+]?[0-9]+)?')

# ---------------------------------------------------------------
# REPLACEMENT for load_wrench_block() — robust to "1.   3.4 …" etc.
# ---------------------------------------------------------------
def load_wrench_block(path):
    """
    Return a (24,6) numpy array with the wrench rows.
    Stops reading when it encounters the line "<rotation matrices>" or EOF.
    """
    rows = []
    float_pat = re.compile(r'[-+]?\d*\.\d+|[-+]?\d+')
    with open(path, 'r') as f:
        for line in f:
            if '<rotation matrices>' in line.lower():
                break
            nums = float_pat.findall(line)
            if len(nums) >= 6:                 # keep the last 6 tokens
                rows.append([float(x) for x in nums[-6:]])
    rows = np.asarray(rows)
    if rows.shape != (24, 6):
        raise ValueError(f'Expected 24×6 wrench block, got {rows.shape}')
    return rows


def main(file_path):
    W = load_wrench_block(file_path)          # 24 × 6
    # 1. bias (gravity cancels across ±axis set)
    bias = W.mean(axis=0)
    F_tilde = W[:, :3] - bias[:3]
    T_tilde = W[:, 3:] - bias[3:]

    # 2. gravity vectors in sensor frame
    g_s = F_tilde / MASS

    # 3. build regressor A (72×3) and torque stack T (72)
    A_rows, T_rows = [], []
    for (gx, gy, gz), tau in zip(g_s, T_tilde):
        A_rows += [[   0,  gz, -gy],
                   [ -gz,   0,  gx],
                   [  gy, -gx,   0]]
        T_rows += list(tau)
    A = np.asarray(A_rows)
    T = np.asarray(T_rows)

    # 4. least‑squares COM
    r = -np.linalg.lstsq(A, T, rcond=None)[0] / MASS

    # 5. residual RMS
    residual_rms = np.linalg.norm(T + MASS * (A @ r)) / np.sqrt(T.size)

    # ---------- output ----------
    print('\nBias vector  [N, N·m] :')
    print(bias)
    print('\nEstimated COM r [m] (sensor frame):')
    print(r)
    print(f'\nRMS residual [N·m]  : {residual_rms:.3f}')

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print('Usage: python fts_calib_from_file.py  <dataset.txt>')
        sys.exit(1)
    main(sys.argv[1])
