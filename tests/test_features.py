from __future__ import annotations

import cv2
import numpy as np
from jpeg_compression_detection.paths import (
    CAMERA_OUTPUT_DIR,
    DATA_DIR,
    FIGURES_DIR,
    GENERATED_DATA_DIR,
    MODELS_DIR,
    PROJECT_ROOT,
    RESULTS_DIR,
    RUN_ID,
    RUN_RESULTS_DIR,
    display_path,
)

from jpeg_compression_detection import (
    analyze_dct_spectrum,
    detect_jpeg_blockiness,
    detect_jpeg_compression,
)


EXPECTED_FEATURES = {
    "energy_mean",
    "energy_std",
    "estimated_quality",
    "psnr",
    "blockiness_mean",
    "blockiness_max",
    "blockiness_std",
    *(f"blockiness_{index}" for index in range(8)),
}


def test_blockiness_returns_eight_finite_ratios() -> None:
    rng = np.random.default_rng(42)
    image = rng.integers(0, 256, size=(64, 64, 3), dtype=np.uint8)

    ratios = detect_jpeg_blockiness(image)

    assert ratios.shape == (8,)
    assert np.isfinite(ratios).all()


def test_dct_spectrum_handles_images_smaller_than_one_block() -> None:
    image = np.zeros((7, 7), dtype=np.uint8)

    assert analyze_dct_spectrum(image) == (0.0, 0.0)


def test_detect_jpeg_compression_returns_documented_schema(
    tmp_path,
) -> None:
    image_path = tmp_path / "sample.png"
    image = np.full((32, 32, 3), 127, dtype=np.uint8)
    assert cv2.imwrite(str(image_path), image)

    result = detect_jpeg_compression(image_path)

    assert isinstance(result, dict)
    assert set(result) == EXPECTED_FEATURES


def test_detect_jpeg_compression_reports_missing_image(tmp_path) -> None:
    result = detect_jpeg_compression(tmp_path / "missing.png")

    assert result == "Unable to read the image"


def test_display_path_hides_machine_local_roots(tmp_path) -> None:
    assert display_path(DATA_DIR / "results_ppm.csv") == (
        "data/results_ppm.csv"
    )
    assert display_path(tmp_path / "sample.png") == "<external>/sample.png"


def test_result_paths_share_one_run_directory() -> None:
    expected_run_directory = RESULTS_DIR / (RUN_ID or "manual")

    assert DATA_DIR == PROJECT_ROOT / "data"
    assert RESULTS_DIR == PROJECT_ROOT / "results"
    assert RUN_RESULTS_DIR == expected_run_directory
    assert MODELS_DIR == expected_run_directory / "models"
    assert FIGURES_DIR == expected_run_directory / "figures"
    assert CAMERA_OUTPUT_DIR == expected_run_directory / "camera"
    assert GENERATED_DATA_DIR == (
        expected_run_directory / "generated_data"
    )
