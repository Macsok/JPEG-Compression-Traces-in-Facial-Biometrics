"""Compare a source image with a frame captured from a physical camera."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import cv2
import numpy as np

from jpeg_compression_detection.paths import (
    CAMERA_OUTPUT_DIR,
    display_path,
    resolve_from_project,
)


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--source",
        type=Path,
        required=True,
        help=(
            "Image displayed for capture, relative to the repository root "
            "when a relative path is supplied."
        ),
    )
    parser.add_argument(
        "--camera-index",
        type=int,
        default=0,
        help="OpenCV camera index (default: 0).",
    )
    parser.add_argument(
        "--extension",
        choices=(".png", ".jpg", ".jpeg", ".bmp"),
        default=".png",
        help="Capture file extension (default: .png).",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=CAMERA_OUTPUT_DIR,
        help=(
            "Capture directory "
            f"(default: {display_path(CAMERA_OUTPUT_DIR)})."
        ),
    )
    parser.add_argument(
        "--allow-fallback",
        action="store_true",
        help=(
            "Write a clearly labeled source-image copy when the physical "
            "camera is unavailable."
        ),
    )
    return parser.parse_args()


def source_reference(source_path: Path) -> str:
    """Return a repository-relative source label when possible."""

    return display_path(source_path)


def write_capture_metadata(
    capture_path: Path,
    *,
    mode: str,
    source_path: Path,
    camera_index: int,
) -> None:
    """Write a sidecar that distinguishes physical and fallback results."""

    metadata_path = capture_path.with_suffix(
        capture_path.suffix + ".json"
    )
    metadata_path.write_text(
        json.dumps(
            {
                "mode": mode,
                "source": source_reference(source_path),
                "camera_index": camera_index,
                "capture_file": capture_path.name,
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )


def capture_from_camera(
    source_path: Path,
    camera_index: int,
    output_dir: Path,
    extension: str,
    allow_fallback: bool = False,
) -> Path | None:
    """Display a source image and capture a frame from a camera."""

    source_image = cv2.imread(str(source_path))
    if source_image is None:
        raise FileNotFoundError(
            f"Unable to read source image: {display_path(source_path)}"
        )

    output_dir.mkdir(parents=True, exist_ok=True)
    print("=== CAMERA CAPTURE COMPARISON ===")
    print(f"Loaded source image: {display_path(source_path)}")
    print(
        f"Shape: {source_image.shape}; dtype: {source_image.dtype}"
    )

    camera = cv2.VideoCapture(camera_index)
    if not camera.isOpened():
        camera.release()
        if not allow_fallback:
            raise RuntimeError(
                "Camera unavailable. Re-run with --allow-fallback only for "
                "a software smoke test."
            )
        capture_path = output_dir / f"software_fallback{extension}"
        if not cv2.imwrite(str(capture_path), source_image):
            raise RuntimeError(
                f"Unable to write fallback: {display_path(capture_path)}"
            )
        write_capture_metadata(
            capture_path,
            mode="software_fallback",
            source_path=source_path,
            camera_index=camera_index,
        )
        print(
            "Camera unavailable; saved a clearly labeled source-image copy "
            "for a software smoke test."
        )
        return capture_path

    try:
        ok, test_frame = camera.read()
        if not ok:
            raise RuntimeError("Unable to read an initial camera frame")

        camera_shape = test_frame.shape
        resized_source = cv2.resize(
            source_image,
            (camera_shape[1], camera_shape[0]),
        )

        cv2.imshow(
            "Source image - point the camera at this window",
            resized_source,
        )
        print("Press 'c' to capture or 'q' to cancel.")

        captured_frame: np.ndarray | None = None
        cancelled = False
        while True:
            ok, frame = camera.read()
            if not ok:
                break

            cv2.imshow("Camera preview - press C to capture", frame)
            key = cv2.waitKey(1) & 0xFF
            if key == ord("c"):
                captured_frame = frame.copy()
                break
            if key == ord("q"):
                cancelled = True
                break

        if cancelled:
            print("Capture cancelled; no file was written.")
            return None
        if captured_frame is None:
            raise RuntimeError("Camera stream ended before a frame was captured")

        capture_path = output_dir / f"physical_camera_capture{extension}"
        if not cv2.imwrite(str(capture_path), captured_frame):
            raise RuntimeError(
                f"Unable to write capture: {display_path(capture_path)}"
            )
        write_capture_metadata(
            capture_path,
            mode="physical_camera",
            source_path=source_path,
            camera_index=camera_index,
        )
        print(f"Saved capture: {display_path(capture_path)}")

        if resized_source.shape == captured_frame.shape:
            difference = cv2.absdiff(resized_source, captured_frame)
            print(
                "Pixel difference: "
                f"sum={np.sum(difference)}, "
                f"max={np.max(difference)}, "
                f"mean={np.mean(difference):.2f}"
            )

        return capture_path
    finally:
        camera.release()
        cv2.destroyAllWindows()


def main() -> None:
    """Run the interactive camera demonstration."""

    args = parse_args()
    capture_from_camera(
        source_path=resolve_from_project(args.source),
        camera_index=args.camera_index,
        output_dir=resolve_from_project(args.output_dir),
        extension=args.extension,
        allow_fallback=args.allow_fallback,
    )


if __name__ == "__main__":
    main()
