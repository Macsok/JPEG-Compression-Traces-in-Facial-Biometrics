# Data and results inventory

The repository distributes five derived feature tables directly in `data/`.
The licensed source-image collections are not included. Row counts below
exclude the header and were validated on 2026-07-31.

## Committed feature tables

| File | Rows | Role | Missing values | Bytes | SHA-256 |
| --- | ---: | --- | --- | ---: | --- |
| `data/results_240k_one_compression_filtered.csv` | 238,098 | JPEG-quality regression; the target is encoded as `_q<quality>` in `filename` | `psnr`: 406 | 70,469,600 | `BD2C2E6B85746094866278410A247CCDEA9831B392783D3074063AC6ECC659FC` |
| `data/results_jfif.csv` | 11,000 | JFIF/JPEG side of the historical format-classification experiment | None | 3,145,435 | `939949FE7F707B1C202764874085CF41F5849C1C56DB1F29CD5270B4AE6CC8DE` |
| `data/results_ppm.csv` | 11,338 | PPM side of the historical format-classification experiment | None | 3,273,388 | `F9EC2A2C4D870552B7F0B5E458841BC691C842EC4DF7394B458CB0617D5FA0CB` |
| `data/results_humanFacesDatasetAI.csv` | 4,630 | AI-generated-face cross-dataset evaluation features | None | 1,289,888 | `71F73BE554D43D1BD8BC3043CDA82413E8D2363C9B1EB85987B38C449CC71207` |
| `data/results_humanFacesDatasetReal.csv` | 5,000 | Real-face cross-dataset evaluation features | `psnr`: 1 | 1,391,940 | `5CFBF2482687E72AA9A414F9B3EE409E4FA8D7293B6A627030AFC9CF42126C56` |

All five tables use the same 17-column schema:

```text
filename, extension,
blockiness_0, blockiness_1, blockiness_2, blockiness_3,
blockiness_4, blockiness_5, blockiness_6, blockiness_7,
blockiness_max, blockiness_mean, blockiness_std,
energy_mean, energy_std, estimated_quality, psnr
```

No malformed rows or case-insensitive duplicate `filename` values were found.
Missing `psnr` values are empty CSV fields. Code that calls `dropna()` changes
the sample count and must report the post-filter count.

The quality-regression table contains 21 intended JPEG quality levels: 10, 20,
30, 40, 50, 60, 70, 75, 78, 80, 82, 84, 86, 88, 89, 90, 91, 92, 93, 94, and
95. It contains 11,338 rows per quality before missing-PSNR filtering. The
training notebook extracts the target from the filename rather than a dedicated
target column.

The paths, sizes, row counts, roles, and digests are machine-readable in
[`data/manifest.json`](../data/manifest.json). The shared
[path module](../src/jpeg_compression_detection/paths.py) exposes `DATA_DIR`
for these files.

## Flat repository layout

```text
data/
  manifest.json
  results_240k_one_compression_filtered.csv
  results_humanFacesDatasetAI.csv
  results_humanFacesDatasetReal.csv
  results_jfif.csv
  results_ppm.csv
docs/
  figures/                 # two preserved reference plots
results/<run-id>/          # created only when a canonical run starts
results/manual/            # created only by a manual workflow
```

There are no empty data placeholders. A researcher may keep licensed images in
any local or external directory and pass that directory explicitly to the
extractor. Generated image variants, models, plots, and camera captures belong
under the ignored `results/` tree, which is created on demand. Optional
subdirectories below `data/` are also ignored so locally supplied image
collections cannot be committed accidentally. `results/manual/` is disposable;
set a unique `JPEG_RESEARCH_RUN_ID` for results that must be retained.

```bash
python scripts/extract_features.py \
  --input <licensed-image-directory> \
  --output results/manual/features.csv
```

The input path in this example is intentionally a placeholder. Do not replace
a missing research dataset with a similarly named collection.

## Inputs and model files that are not bundled

The source images underlying all five tables are absent. Historical notebooks
refer to logical collections such as `contest-images`, `ColorFeret-unpacked`,
`jfif`, `multiple-compression`, `phone-images`, `ppm-copy`, `test-images`, and
`web-cam-images`. Map those names to verified local datasets without restoring
machine-specific absolute paths.

Several optional evaluation tables are also absent, including variants named
for iFakeFaceDB, RGB-faces-128x128, Selfie Dataset, Tufts, VGG, ECVP,
DigiFace, and repeated-compression tests. A filename is not sufficient
provenance; record the exact provider, version, license, acquisition date, and
checksum.

No trained model files are bundled. Canonical runs write them to
`results/<run-id>/models`; manual notebook sessions use
`results/manual/models`. Expected files include:

- `best_classification_model.pkl`, `best_model_<winner>.pkl`, `scaler.pkl`,
  `feature_columns.pkl`, and `all_models.pkl` for classification;
- `best_compression_model.pkl` and one named model file per quality-regression
  candidate;
- one `<candidate>_metrics.json` checkpoint per completed regression candidate;
- `quality_model_selection.json`, recording validation-only model selection,
  exact feature order, and train/validation/test metrics.

The stable model aliases are incomplete without their preprocessing and
selection records. Never load an unverified pickle or joblib file because it
can execute arbitrary code. Recovered model files require scikit-learn 1.3.2.

## Required provenance record

Before using a source collection, record at minimum:

- stable dataset ID, official title, version or release date;
- provider, official landing page, license, redistribution restrictions, and
  access date;
- required citation and consent/privacy restrictions;
- acquisition method, responsible researcher, archive checksum, extracted file
  count, and total bytes;
- subject and source-image identifiers needed for grouped splits;
- every rename, filter, conversion, resize, recompression, and exclusion;
- code revision, configuration, and environment used to derive each output.

A dataset-level YAML record may start from this unfilled template:

```yaml
dataset_id: TODO
title: TODO
version: TODO
provider: TODO
landing_page: TODO
license_name: TODO
license_reference: TODO
required_citation: TODO
accessed_at: TODO
source_archive: TODO
source_archive_sha256: TODO
extracted_file_count: TODO
redistribution_allowed: TODO
notes: TODO
```

Maintain a file-level CSV or TSV manifest with at least:

```text
dataset_id,relative_path,bytes,sha256,subject_id,source_image_id,split,parent_sha256,transformation
```

Commit the manifest rather than restricted images when redistribution is
forbidden. The repository ignores `results/`; keep restricted source images
outside version control or use a properly configured data-versioning tool.

## Checksum procedure

Verify the five committed tables before use.

Windows PowerShell:

```powershell
Get-FileHash -Algorithm SHA256 data/results_*.csv | Format-Table Path,Hash
```

Linux or macOS:

```bash
sha256sum data/results_*.csv
```

The repository verifier also checks declared sizes and CSV row counts:

```bash
python scripts/verify_data.py
```

Use `--skip-hashes` only for a fast structural check, never for a published
run. Generate a sorted, per-file checksum manifest separately for every
licensed source collection and inspect filenames for personal information
before publication.

## Experimental-integrity requirements

The quality-regression table contains many compression variants derived from
the same source image. A row-wise split can place variants of one source in all
three partitions and inflate performance. A confirmatory experiment must derive
a stable `source_image_id` and use grouped splitting.

The JFIF and PPM tables also originate from different collections. Near-perfect
classification can reflect dataset identity, dimensions, or acquisition
pipeline rather than compression alone. A confirmatory design should use paired
encodings and group-held-out or dataset-held-out evaluation.

Never overwrite a published CSV after changing feature calculations, codec
versions, filtering, or split logic. Write a new version, preserve the old
checksum, and document the scientific-method change.
