from __future__ import annotations

import argparse
import json

import pytest

from jpeg_compression_detection.paths import PROJECT_ROOT, RESULTS_DIR
from scripts.run_reproduction import (
    sanitize_error_message,
    validate_run_id,
    validate_timeout,
    write_result_manifest,
)
from scripts.verify_data import MANIFEST_PATH


def test_run_identifier_rejects_path_separators() -> None:
    assert validate_run_id("paper-v1") == "paper-v1"
    with pytest.raises(argparse.ArgumentTypeError):
        validate_run_id("../outside")


def test_timeout_accepts_positive_seconds_or_disabled_value() -> None:
    assert validate_timeout("21600") == 21_600
    assert validate_timeout("-1") == -1
    with pytest.raises(argparse.ArgumentTypeError):
        validate_timeout("0")


def test_stored_error_message_hides_project_root() -> None:
    error = RuntimeError(f"Failure under {PROJECT_ROOT}")

    sanitized = sanitize_error_message(error)

    assert str(PROJECT_ROOT) not in sanitized
    assert "Failure under ." == sanitized


def test_only_the_data_manifest_is_a_canonical_input() -> None:
    assert MANIFEST_PATH == PROJECT_ROOT / "data" / "manifest.json"


def test_result_manifest_uses_the_final_name_and_excludes_itself(
    tmp_path,
) -> None:
    run_directory = tmp_path / "paper-v1"
    run_directory.mkdir()
    (run_directory / "run.json").write_text("{}\n", encoding="utf-8")

    manifest_path = write_result_manifest(run_directory)
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))

    assert manifest_path.name == "result-manifest.json"
    assert [entry["path"] for entry in manifest["files"]] == ["run.json"]


def test_result_root_is_repository_relative() -> None:
    assert RESULTS_DIR == PROJECT_ROOT / "results"
