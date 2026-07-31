"""Repository-relative paths shared by scripts and notebooks."""

import os
import re
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATA_DIR = PROJECT_ROOT / "data"
RESULTS_DIR = PROJECT_ROOT / "results"

RUN_ID = os.environ.get("JPEG_RESEARCH_RUN_ID")
if RUN_ID and not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.-]*", RUN_ID):
    raise ValueError(
        "JPEG_RESEARCH_RUN_ID contains unsupported path characters"
    )
RUN_RESULTS_DIR = RESULTS_DIR / (RUN_ID or "manual")

MODELS_DIR = RUN_RESULTS_DIR / "models"
FIGURES_DIR = RUN_RESULTS_DIR / "figures"
CAMERA_OUTPUT_DIR = RUN_RESULTS_DIR / "camera"
GENERATED_DATA_DIR = RUN_RESULTS_DIR / "generated_data"


def resolve_from_project(path: str | Path) -> Path:
    """Resolve a user-supplied path relative to the repository root."""

    candidate = Path(path)
    return candidate if candidate.is_absolute() else PROJECT_ROOT / candidate


def display_path(path: str | Path) -> str:
    """Format a path without exposing a machine-local absolute directory."""

    candidate = Path(path).resolve()
    try:
        return candidate.relative_to(PROJECT_ROOT).as_posix()
    except ValueError:
        return f"<external>/{candidate.name}"
