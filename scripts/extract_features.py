"""Extract JPEG-compression features from a directory of images."""

from __future__ import annotations

import argparse
import csv
import time
from pathlib import Path

from jpeg_compression_detection import detect_jpeg_compression
from jpeg_compression_detection.paths import (
    GENERATED_DATA_DIR,
    display_path,
    resolve_from_project,
)


SUPPORTED_EXTENSIONS = {
    ".jpg",
    ".jpeg",
    ".png",
    ".bmp",
    ".tif",
    ".tiff",
    ".jfif",
    ".webp",
    ".ppm",
}
FEATURE_FIELDNAMES = [
    "filename",
    "extension",
    *(f"blockiness_{index}" for index in range(8)),
    "blockiness_max",
    "blockiness_mean",
    "blockiness_std",
    "energy_mean",
    "energy_std",
    "estimated_quality",
    "psnr",
]


def process_images_in_directory(
    input_dir: str | Path,
    output_csv: str | Path,
    error_csv: str | Path | None = None,
    fail_on_error: bool = False,
) -> int:
    """Process every supported image in one directory and write a CSV file.

    Paths supplied by the caller may be absolute. Command-line defaults and
    all paths documented by this repository are relative to the project root.
    The return value is the number of successfully analyzed images. When
    ``fail_on_error`` is true, all rows and the error log are written before
    a RuntimeError is raised for any failed image.
    """

    input_path = resolve_from_project(input_dir)
    output_path = resolve_from_project(output_csv)
    error_path = (
        resolve_from_project(error_csv)
        if error_csv is not None
        else output_path.with_name(f"{output_path.stem}.errors.csv")
    )
    if output_path.resolve() == error_path.resolve():
        raise ValueError(
            "Feature output and error output must be different files"
        )

    if not input_path.is_dir():
        raise NotADirectoryError(
            f"Input directory does not exist: {display_path(input_path)}"
        )

    image_files = sorted(
        path
        for path in input_path.iterdir()
        if path.is_file() and path.suffix.lower() in SUPPORTED_EXTENSIONS
    )

    if not image_files:
        raise FileNotFoundError(
            f"No supported images found in: {display_path(input_path)}"
        )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    print(f"Found {len(image_files)} images to process")

    total_start_time = time.perf_counter()
    successful_count = 0
    errors: list[dict[str, str]] = []

    with output_path.open("w", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(
            csv_file,
            fieldnames=FEATURE_FIELDNAMES,
        )
        writer.writeheader()

        for index, image_file in enumerate(image_files, start=1):
            print(
                f"Processing {index}/{len(image_files)}: "
                f"{image_file.name}"
            )
            start_time = time.perf_counter()

            try:
                metrics = detect_jpeg_compression(image_file)
                processing_time = time.perf_counter() - start_time

                result = {
                    "filename": image_file.stem,
                    "extension": image_file.suffix,
                }

                if isinstance(metrics, dict):
                    result.update(metrics)
                else:
                    raise ValueError(metrics)

                writer.writerow(result)
                csv_file.flush()
                successful_count += 1
                print(
                    f"Completed in {processing_time:.4f} s and saved"
                )

            except Exception as error:
                print(f"Error while processing {image_file.name}: {error}")
                errors.append(
                    {
                        "filename": image_file.stem,
                        "extension": image_file.suffix,
                        "error": str(error),
                    }
                )

    total_time = time.perf_counter() - total_start_time
    print("=" * 60)
    print(f"Attempted {len(image_files)} images")
    print(f"Successful: {successful_count}")
    print(f"Failed: {len(errors)}")
    print(f"Total time: {total_time:.2f} s")
    if image_files:
        print(
            f"Mean time per image: "
            f"{total_time / len(image_files):.4f} s"
        )
    print(f"Results written to: {display_path(output_path)}")

    error_path.parent.mkdir(parents=True, exist_ok=True)
    with error_path.open("w", newline="", encoding="utf-8") as error_file:
        error_writer = csv.DictWriter(
            error_file,
            fieldnames=["filename", "extension", "error"],
        )
        error_writer.writeheader()
        error_writer.writerows(errors)
    print(f"Error log written to: {display_path(error_path)}")

    print("=" * 60)

    if errors and fail_on_error:
        raise RuntimeError(
            f"{len(errors)} of {len(image_files)} images failed; "
            f"see {display_path(error_path)}"
        )

    return successful_count


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--input",
        type=Path,
        required=True,
        help=(
            "Licensed image directory. Relative paths are resolved from "
            "the repository root."
        ),
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=GENERATED_DATA_DIR / "features.csv",
        help=(
            "Output CSV, relative to the repository root by default "
            f"(default: {display_path(GENERATED_DATA_DIR / 'features.csv')})."
        ),
    )
    parser.add_argument(
        "--error-output",
        type=Path,
        default=None,
        help=(
            "Optional error CSV. By default, failures are written beside the "
            "feature table as <output-stem>.errors.csv."
        ),
    )
    parser.add_argument(
        "--allow-errors",
        action="store_true",
        help=(
            "Return exit code 0 even when one or more images fail. "
            "Failures are always recorded in the error CSV."
        ),
    )
    return parser.parse_args()


def main() -> None:
    """Run the batch feature extractor."""

    args = parse_args()
    process_images_in_directory(
        args.input,
        args.output,
        args.error_output,
        fail_on_error=not args.allow_errors,
    )


if __name__ == "__main__":
    main()
