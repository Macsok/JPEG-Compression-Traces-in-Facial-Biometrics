"""Feature extraction for JPEG compression analysis.

The implementation intentionally preserves the calculations used to generate
the committed result tables. Refactoring this module should therefore be
treated as a scientific-method change and validated against those tables.
"""

from pathlib import Path
from typing import Any

import cv2
import numpy as np


def detect_jpeg_blockiness(image: np.ndarray) -> np.ndarray:
    """Return blockiness ratios for the eight offsets of an 8 x 8 JPEG block.

    The returned array contains one ratio for every adjacent-pixel boundary:

    - ``blockiness_ratios[0]``: boundary between pixels 0 and 1
    - ``blockiness_ratios[1]``: boundary between pixels 1 and 2
    - ...
    - ``blockiness_ratios[7]``: boundary between pixels 7 and 8, i.e. the
      principal JPEG block boundary
    """

    gray = (
        cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        if len(image.shape) > 2
        else image
    )

    # Compute differences between adjacent pixels once.
    h_diff = np.abs(np.diff(gray, axis=1))  # Right-hand neighbour.
    v_diff = np.abs(np.diff(gray, axis=0))  # Lower neighbour.

    blockiness_ratios = np.zeros(8, dtype=np.float32)

    for offset in range(8):
        # Select every eighth boundary, starting at the current offset.
        h_block_diff = h_diff[:, offset::8]
        v_block_diff = v_diff[offset::8, :]

        # Masks avoid repeated, relatively expensive calls to np.delete.
        h_mask = np.ones(h_diff.shape[1], dtype=bool)
        h_mask[offset::8] = False
        v_mask = np.ones(v_diff.shape[0], dtype=bool)
        v_mask[offset::8] = False

        # Compare the selected block boundaries with all other differences.
        block_diff_mean = (
            h_block_diff.mean() + v_block_diff.mean()
        ) * 0.5
        non_block_diff_mean = (
            h_diff[:, h_mask].mean() + v_diff[v_mask, :].mean()
        ) * 0.5

        blockiness_ratios[offset] = (
            block_diff_mean / non_block_diff_mean
            if non_block_diff_mean > 0
            else 0.0
        )

    return blockiness_ratios


def estimate_jpeg_quality(image: np.ndarray) -> tuple[int, float]:
    """Estimate JPEG quality by comparing the image with recompressions.

    The original image is recompressed at a fixed list of quality levels. The
    level with the lowest mean squared error (MSE) is returned together with
    its peak signal-to-noise ratio (PSNR).

    Caution:

    - The method does not recover the original JPEG encoder parameters.
    - It does not reliably distinguish an uncompressed image from a
      high-quality JPEG.
    - Double-compressed images can produce misleading estimates.
    """

    gray = (
        cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        if len(image.shape) > 2
        else image
    )
    gray_float = gray.astype(np.float32)

    qualities = [
        10,
        20,
        30,
        40,
        50,
        60,
        70,
        75,
        78,
        80,
        82,
        84,
        86,
        88,
        89,
        90,
        91,
        92,
        93,
        94,
        95,
    ]
    best_quality = 100
    best_mse = float("inf")
    best_psnr = 0.0

    for quality in qualities:
        encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), quality]
        _, encoded_img = cv2.imencode(".jpg", gray, encode_param)
        decoded_img = cv2.imdecode(encoded_img, cv2.IMREAD_GRAYSCALE)

        mse = np.mean(
            (gray_float - decoded_img.astype(np.float32)) ** 2
        )

        if mse < best_mse:
            best_mse = mse
            best_quality = quality
            best_psnr = (
                10 * np.log10(65025.0 / mse)
                if mse > 0
                else float("inf")
            )

    return best_quality, best_psnr


def analyze_dct_spectrum(image: np.ndarray) -> tuple[float, float]:
    """Return mean and standard deviation of 8 x 8-block DCT AC energy."""

    gray = (
        cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        if len(image.shape) > 2
        else image
    )

    height, width = gray.shape
    padded_height = height - (height % 8)
    padded_width = width - (width % 8)

    if padded_height == 0 or padded_width == 0:
        return 0.0, 0.0

    gray_crop = gray[:padded_height, :padded_width].astype(np.float32)

    block_rows = padded_height // 8
    block_columns = padded_width // 8
    dct_energy = np.zeros(block_rows * block_columns, dtype=np.float32)

    index = 0
    for row in range(0, padded_height, 8):
        for column in range(0, padded_width, 8):
            block = gray_crop[row : row + 8, column : column + 8]
            dct = cv2.dct(block)
            # AC energy is the total energy excluding the [0, 0] DC term.
            dct_energy[index] = (
                np.sum(np.abs(dct)) - np.abs(dct[0, 0])
            )
            index += 1

    return float(dct_energy.mean()), float(dct_energy.std())


def detect_jpeg_compression(
    image_path: str | Path,
) -> dict[str, Any] | str:
    """Extract the compression features used throughout this repository."""

    image = cv2.imread(str(image_path))
    if image is None:
        return "Unable to read the image"

    blockiness_ratios = detect_jpeg_blockiness(image)
    energy_mean, energy_std = analyze_dct_spectrum(image)
    estimated_quality, psnr = estimate_jpeg_quality(image)

    result: dict[str, Any] = {
        "energy_mean": energy_mean,
        "energy_std": energy_std,
        "estimated_quality": int(estimated_quality),
        "psnr": float(psnr) if np.isfinite(psnr) else None,
        "blockiness_mean": float(np.mean(blockiness_ratios)),
        "blockiness_max": float(np.max(blockiness_ratios)),
        "blockiness_std": float(np.std(blockiness_ratios)),
    }

    for index, value in enumerate(blockiness_ratios):
        result[f"blockiness_{index}"] = float(value)

    return result
