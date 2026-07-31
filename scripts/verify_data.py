"""Verify canonical research data against data/manifest.json."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from jpeg_compression_detection.paths import PROJECT_ROOT


MANIFEST_PATH = PROJECT_ROOT / "data" / "manifest.json"


def sha256(path: Path) -> str:
    """Return the SHA-256 digest of a file without loading it into memory."""

    digest = hashlib.sha256()
    with path.open("rb") as file_handle:
        for chunk in iter(lambda: file_handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def csv_data_rows(path: Path) -> int:
    """Count CSV data rows, excluding the header."""

    with path.open("rb") as file_handle:
        line_count = sum(1 for _ in file_handle)
    return max(0, line_count - 1)


def load_manifest(path: Path) -> dict[str, Any]:
    """Load one repository manifest."""

    with path.open(encoding="utf-8") as file_handle:
        return json.load(file_handle)


def verify_manifest(
    manifest_path: Path,
    *,
    check_hashes: bool = True,
) -> list[str]:
    """Return human-readable validation errors for one manifest."""

    errors: list[str] = []
    manifest = load_manifest(manifest_path)

    for entry in manifest["files"]:
        relative_path = Path(entry["path"])
        path = PROJECT_ROOT / relative_path

        if not path.is_file():
            errors.append(f"missing: {relative_path.as_posix()}")
            continue

        actual_size = path.stat().st_size
        if actual_size != entry["bytes"]:
            errors.append(
                f"size mismatch: {relative_path.as_posix()} "
                f"(expected {entry['bytes']}, got {actual_size})"
            )

        if "data_rows" in entry:
            actual_rows = csv_data_rows(path)
            if actual_rows != entry["data_rows"]:
                errors.append(
                    f"row-count mismatch: {relative_path.as_posix()} "
                    f"(expected {entry['data_rows']}, got {actual_rows})"
                )

        if check_hashes:
            actual_hash = sha256(path)
            if actual_hash != entry["sha256"]:
                errors.append(
                    f"SHA-256 mismatch: {relative_path.as_posix()}"
                )

    return errors


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--skip-hashes",
        action="store_true",
        help="Check file existence, size, and row counts without SHA-256.",
    )
    return parser.parse_args()


def main() -> None:
    """Validate every file declared by the canonical data manifest."""

    args = parse_args()
    print(f"Checking {MANIFEST_PATH.relative_to(PROJECT_ROOT)}")
    errors = verify_manifest(
        MANIFEST_PATH,
        check_hashes=not args.skip_hashes,
    )

    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        raise SystemExit(1)

    print("All declared files match their manifests.")


if __name__ == "__main__":
    main()
