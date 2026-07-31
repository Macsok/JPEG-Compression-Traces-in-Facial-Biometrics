"""Execute the canonical modeling notebooks into a separate result folder."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
from importlib.metadata import distributions
import json
import os
import platform
import re
import subprocess
import sys
from pathlib import Path

from jpeg_compression_detection.paths import (
    PROJECT_ROOT,
    RESULTS_DIR,
    display_path,
)

try:
    from scripts.verify_data import MANIFEST_PATH, verify_manifest
except ModuleNotFoundError:
    # Direct execution places scripts/ rather than the repository root first
    # on sys.path.
    from verify_data import MANIFEST_PATH, verify_manifest


DEFAULT_TIMEOUT = 21_600
PIPELINES = {
    "classification": (
        Path(
            "notebooks/03_classification/"
            "01_train_jfif_vs_ppm_classifier.ipynb"
        ),
        Path(
            "notebooks/03_classification/"
            "02_evaluate_jfif_vs_ppm_classifier.ipynb"
        ),
    ),
    "quality-regression": (
        Path(
            "notebooks/04_quality_regression/"
            "01_train_quality_regressors.ipynb"
        ),
        Path(
            "notebooks/04_quality_regression/"
            "02_evaluate_selected_quality_regressor.ipynb"
        ),
    ),
}
SOURCE_LOCATIONS = (
    Path("README.md"),
    Path(".gitattributes"),
    Path(".gitignore"),
    Path(".python-version"),
    Path("pyproject.toml"),
    Path("requirements.txt"),
    Path("src"),
    Path("scripts"),
    Path("notebooks"),
    Path("tests"),
    Path("docs"),
    Path("environment"),
    Path("data/manifest.json"),
)


def sha256_file(path: Path) -> str:
    """Return the SHA-256 digest of one file."""

    digest = hashlib.sha256()
    with path.open("rb") as file_handle:
        for chunk in iter(lambda: file_handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def file_record(path: Path, relative_to: Path) -> dict[str, object]:
    """Describe one file without recording a machine-local absolute path."""

    return {
        "path": path.relative_to(relative_to).as_posix(),
        "bytes": path.stat().st_size,
        "sha256": sha256_file(path),
    }


def source_files() -> list[Path]:
    """Return active source, configuration, and documentation files."""

    files: set[Path] = set()
    for relative_path in SOURCE_LOCATIONS:
        path = PROJECT_ROOT / relative_path
        if path.is_file():
            files.add(path)
        elif path.is_dir():
            files.update(
                candidate
                for candidate in path.rglob("*")
                if candidate.is_file()
                and "__pycache__" not in candidate.parts
                and candidate.suffix != ".pyc"
            )
    return sorted(files, key=lambda path: path.as_posix().casefold())


def version_control_state() -> dict[str, object]:
    """Record Git state when this directory is a Git working tree."""

    if not (PROJECT_ROOT / ".git").exists():
        return {
            "type": "none",
            "revision": None,
            "worktree_status": None,
            "note": (
                "No .git metadata was present; use the source manifest as "
                "the code identity for this run."
            ),
        }

    revision = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=PROJECT_ROOT,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
    status = subprocess.run(
        ["git", "status", "--short"],
        cwd=PROJECT_ROOT,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.splitlines()
    return {
        "type": "git",
        "revision": revision,
        "worktree_status": status,
    }


def capture_environment(run_root: Path) -> dict[str, object]:
    """Write package and source manifests into this run's environment folder."""

    environment_dir = run_root / "environment"
    environment_dir.mkdir(parents=True, exist_ok=True)

    package_versions: dict[str, str] = {}
    for distribution in distributions():
        name = distribution.metadata.get("Name")
        if name:
            package_versions[name] = distribution.version
    packages_path = environment_dir / "packages.json"
    packages_path.write_text(
        json.dumps(
            dict(
                sorted(
                    package_versions.items(),
                    key=lambda item: item[0].casefold(),
                )
            ),
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )

    records = [
        file_record(path, PROJECT_ROOT)
        for path in source_files()
    ]
    canonical_records = json.dumps(
        records,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    source_digest = hashlib.sha256(canonical_records).hexdigest()
    source_manifest_path = environment_dir / "source-manifest.json"
    source_manifest_path.write_text(
        json.dumps(
            {
                "algorithm": "sha256",
                "source_tree_sha256": source_digest,
                "files": records,
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )

    return {
        "packages": packages_path.relative_to(run_root).as_posix(),
        "source_manifest": (
            source_manifest_path.relative_to(run_root).as_posix()
        ),
        "source_tree_sha256": source_digest,
        "version_control": version_control_state(),
    }


def write_result_manifest(run_root: Path) -> Path:
    """Checksum every run result except the manifest itself."""

    manifest_path = run_root / "result-manifest.json"
    records = [
        file_record(path, run_root)
        for path in sorted(
            (
                candidate
                for candidate in run_root.rglob("*")
                if candidate.is_file() and candidate != manifest_path
            ),
            key=lambda path: path.as_posix().casefold(),
        )
    ]
    manifest_path.write_text(
        json.dumps(
            {
                "algorithm": "sha256",
                "generated_at_utc": datetime.now(
                    timezone.utc
                ).isoformat(),
                "files": records,
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    return manifest_path


def validate_inputs() -> None:
    """Fail before execution if a committed input does not match its hash."""

    errors = verify_manifest(MANIFEST_PATH)
    if errors:
        formatted = "\n".join(f"- {error}" for error in errors)
        raise RuntimeError(f"Input verification failed:\n{formatted}")


def execute_notebook(
    notebook_path: Path,
    output_dir: Path,
    timeout: int,
    run_id: str,
) -> None:
    """Execute one notebook from the repository root."""

    absolute_path = PROJECT_ROOT / notebook_path
    if not absolute_path.is_file():
        raise FileNotFoundError(f"Notebook not found: {notebook_path}")

    output_dir.mkdir(parents=True, exist_ok=True)
    command = [
        sys.executable,
        "-m",
        "jupyter",
        "nbconvert",
        "--to",
        "notebook",
        "--execute",
        str(absolute_path),
        "--output",
        notebook_path.name,
        "--output-dir",
        str(output_dir),
        f"--ExecutePreprocessor.timeout={timeout}",
    ]

    print(f"Executing {notebook_path.as_posix()}")
    environment = os.environ.copy()
    environment["JPEG_RESEARCH_RUN_ID"] = run_id
    subprocess.run(
        command,
        cwd=PROJECT_ROOT,
        env=environment,
        check=True,
    )


def default_run_id() -> str:
    """Return a sortable UTC identifier for one reproduction attempt."""

    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def validate_run_id(value: str) -> str:
    """Reject identifiers that could escape or ambiguously nest a run."""

    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.-]*", value):
        raise argparse.ArgumentTypeError(
            "run ID must contain only letters, digits, '.', '_', or '-'"
        )
    return value


def validate_timeout(value: str) -> int:
    """Accept a positive per-cell timeout or -1 to disable it."""

    timeout = int(value)
    if timeout == -1 or timeout > 0:
        return timeout
    raise argparse.ArgumentTypeError(
        "timeout must be a positive number of seconds or -1"
    )


def sanitize_error_message(error: BaseException) -> str:
    """Remove machine-local roots from an error stored with run metadata."""

    message = str(error)
    for private_value in (str(PROJECT_ROOT), sys.executable):
        message = message.replace(
            private_value,
            "." if private_value == str(PROJECT_ROOT) else Path(
                sys.executable
            ).name,
        )
    return message


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--pipeline",
        choices=(*PIPELINES, "all"),
        default="all",
        help="Pipeline to reproduce (default: all).",
    )
    parser.add_argument(
        "--timeout",
        type=validate_timeout,
        default=DEFAULT_TIMEOUT,
        help=(
            "Per-cell timeout in seconds; use -1 to disable "
            f"(default: {DEFAULT_TIMEOUT})."
        ),
    )
    parser.add_argument(
        "--skip-input-verification",
        action="store_true",
        help="Do not verify committed inputs against their SHA-256 hashes.",
    )
    parser.add_argument(
        "--run-id",
        type=validate_run_id,
        default=None,
        help=(
            "Result directory name. Defaults to a UTC timestamp such as "
            "20260731T120000Z."
        ),
    )
    parser.add_argument(
        "--finalize-only",
        action="store_true",
        help=(
            "Refresh result-manifest.json for an existing --run-id after "
            "manual hardware records have been added; execute no notebooks."
        ),
    )
    return parser.parse_args()


def finalize_existing_run(run_id: str) -> None:
    """Refresh the manifest after all manual run records have been added."""

    run_root = RESULTS_DIR / run_id
    metadata_path = run_root / "run.json"
    if not metadata_path.is_file():
        raise FileNotFoundError(
            "Existing run metadata not found: "
            f"{display_path(metadata_path)}"
        )

    run_metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    run_metadata["finalized_at_utc"] = datetime.now(
        timezone.utc
    ).isoformat()
    metadata_path.write_text(
        json.dumps(run_metadata, indent=2) + "\n",
        encoding="utf-8",
    )
    manifest_path = write_result_manifest(run_root)
    print(f"Finalized run manifest: {display_path(manifest_path)}")
    print("Do not modify the run directory after finalization.")


def main() -> None:
    """Run the selected notebook pipeline."""

    args = parse_args()
    if args.finalize_only:
        if args.run_id is None:
            raise ValueError("--finalize-only requires an explicit --run-id")
        finalize_existing_run(args.run_id)
        return

    if not args.skip_input_verification:
        validate_inputs()

    selected = (
        tuple(PIPELINES)
        if args.pipeline == "all"
        else (args.pipeline,)
    )
    run_id = args.run_id or default_run_id()
    run_root = RESULTS_DIR / run_id
    if run_root.exists():
        raise FileExistsError(
            f"Run directory already exists; choose another --run-id: "
            f"{display_path(run_root)}"
        )
    output_root = run_root / "executed_notebooks"
    run_root.mkdir(parents=True)

    run_metadata = {
        "run_id": run_id,
        "status": "running",
        "started_at_utc": datetime.now(timezone.utc).isoformat(),
        "pipelines": list(selected),
        "command": [
            Path(sys.executable).name,
            "scripts/run_reproduction.py",
            *sys.argv[1:],
        ],
        "timeout_seconds_per_cell": args.timeout,
        "python": sys.version,
        "python_executable": Path(sys.executable).name,
        "platform": platform.platform(),
        "input_verification": not args.skip_input_verification,
        "input_manifest": file_record(MANIFEST_PATH, PROJECT_ROOT),
        "environment": None,
    }
    metadata_path = run_root / "run.json"

    def write_metadata() -> None:
        metadata_path.write_text(
            json.dumps(run_metadata, indent=2) + "\n",
            encoding="utf-8",
        )

    write_metadata()
    try:
        run_metadata["environment"] = capture_environment(run_root)
        write_metadata()
        for pipeline_name in selected:
            pipeline_output = output_root / pipeline_name
            for notebook_path in PIPELINES[pipeline_name]:
                execute_notebook(
                    notebook_path,
                    pipeline_output,
                    args.timeout,
                    run_id,
                )
    except BaseException as error:
        run_metadata["status"] = (
            "cancelled" if isinstance(error, KeyboardInterrupt) else "failed"
        )
        run_metadata["finished_at_utc"] = datetime.now(
            timezone.utc
        ).isoformat()
        run_metadata["error"] = (
            f"{type(error).__name__}: {sanitize_error_message(error)}"
        )
        write_metadata()
        write_result_manifest(run_root)
        raise
    else:
        run_metadata["status"] = "complete"
        run_metadata["finished_at_utc"] = datetime.now(
            timezone.utc
        ).isoformat()
        write_metadata()
        write_result_manifest(run_root)

    print(f"Run results written under: {display_path(run_root)}")


if __name__ == "__main__":
    main()
