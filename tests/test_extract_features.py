from __future__ import annotations

import csv

import pytest

import scripts.extract_features as extractor


def valid_metrics() -> dict[str, float | int | None]:
    return {
        **{f"blockiness_{index}": 1.0 for index in range(8)},
        "blockiness_max": 1.0,
        "blockiness_mean": 1.0,
        "blockiness_std": 0.0,
        "energy_mean": 10.0,
        "energy_std": 2.0,
        "estimated_quality": 90,
        "psnr": 40.0,
    }


def test_supported_extensions_include_common_tiff_suffixes() -> None:
    assert {".tif", ".tiff"} <= extractor.SUPPORTED_EXTENSIONS


def test_failure_before_success_keeps_a_stable_feature_schema(
    tmp_path,
    monkeypatch,
) -> None:
    input_dir = tmp_path / "images"
    input_dir.mkdir()
    (input_dir / "a.jpg").touch()
    (input_dir / "b.jpg").touch()

    def fake_detection(path):
        return "unreadable" if path.name == "a.jpg" else valid_metrics()

    monkeypatch.setattr(
        extractor,
        "detect_jpeg_compression",
        fake_detection,
    )

    output_path = tmp_path / "features.csv"
    successful = extractor.process_images_in_directory(
        input_dir,
        output_path,
    )

    assert successful == 1

    with output_path.open(newline="", encoding="utf-8") as file_handle:
        rows = list(csv.DictReader(file_handle))
        assert file_handle.closed is False

    assert rows == [
        {
            **{
                field: str(valid_metrics()[field])
                for field in extractor.FEATURE_FIELDNAMES
                if field not in {"filename", "extension"}
            },
            "filename": "b",
            "extension": ".jpg",
        }
    ]

    error_path = tmp_path / "features.errors.csv"
    with error_path.open(newline="", encoding="utf-8") as file_handle:
        errors = list(csv.DictReader(file_handle))

    assert errors == [
        {
            "filename": "a",
            "extension": ".jpg",
            "error": "unreadable",
        }
    ]


def test_fail_on_error_raises_after_writing_both_tables(
    tmp_path,
    monkeypatch,
) -> None:
    input_dir = tmp_path / "images"
    input_dir.mkdir()
    (input_dir / "broken.jpg").touch()
    monkeypatch.setattr(
        extractor,
        "detect_jpeg_compression",
        lambda path: "unreadable",
    )

    output_path = tmp_path / "features.csv"
    with pytest.raises(RuntimeError, match="1 of 1 images failed"):
        extractor.process_images_in_directory(
            input_dir,
            output_path,
            fail_on_error=True,
        )

    assert output_path.is_file()
    assert (tmp_path / "features.errors.csv").is_file()


def test_feature_and_error_outputs_must_be_different(tmp_path) -> None:
    input_dir = tmp_path / "images"
    input_dir.mkdir()
    (input_dir / "image.jpg").touch()
    shared_path = tmp_path / "shared.csv"

    with pytest.raises(ValueError, match="must be different"):
        extractor.process_images_in_directory(
            input_dir,
            shared_path,
            shared_path,
        )
