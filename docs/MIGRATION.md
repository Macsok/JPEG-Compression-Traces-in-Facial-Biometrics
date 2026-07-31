# Repository migration record

This record describes the reorganization of the working directory performed
on 2026-07-31. No files in neighbouring directories were modified.

## Preservation policy

The pre-migration Polish-language materials are preserved under
[`archive/polish_originals`](../archive/polish_originals). Their checksums are
recorded in
[`archive/polish_originals/SHA256SUMS`](../archive/polish_originals/SHA256SUMS).
The archive is historical evidence and is not part of the active execution
path.

Active notebook copies use the following output policy:

- an output is removed when it contains Polish text or was rendered from
  Polish plot labels;
- an English-only output is retained;
- workstation-specific paths in retained textual outputs are replaced with
  repository-relative paths or neutral placeholders.

This policy preserves useful historical results without carrying
Polish-language presentation or private local paths into the active workflow.

## Notebook mapping

| Historical file | Active English copy |
| --- | --- |
| `testing-notebook.ipynb` | `notebooks/01_feature_exploration/01_general_feature_exploration.ipynb` |
| `testing-notebook-single-blockiness.ipynb` | `notebooks/01_feature_exploration/02_single_blockiness_exploration.ipynb` |
| `jpeg-testing-quantization-table.ipynb` | `notebooks/01_feature_exploration/03_jpeg_quantization_tables.ipynb` |
| `multiple-compression.ipynb` | `notebooks/02_multiple_compression/01_generate_and_analyze_multiple_compression.ipynb` |
| `multiple-compression-visualise.ipynb` | `notebooks/02_multiple_compression/02_visualize_multiple_compression.ipynb` |
| `ML.ipynb` | `notebooks/03_classification/01_train_jfif_vs_ppm_classifier.ipynb` |
| `ML-evaluation-and-tests.ipynb` | `notebooks/03_classification/02_evaluate_jfif_vs_ppm_classifier.ipynb` |
| `TEST-quality-and-jfif-or-ppm.ipynb` | `notebooks/03_classification/03_test_quality_and_format_models.ipynb` |
| `ML-compression-detection.ipynb` | `notebooks/04_quality_regression/01_train_quality_regressors.ipynb` |
| `ML-compression-detection-load-model.ipynb` | `notebooks/04_quality_regression/02_evaluate_selected_quality_regressor.ipynb` |
| `ML-compression-tests.ipynb` | `notebooks/04_quality_regression/03_test_quality_regressors.ipynb` |
| `ML-compression-tests-multiple-datasets.ipynb` | `notebooks/04_quality_regression/04_compare_quality_across_datasets.ipynb` |
| `web-cam.ipynb` | `notebooks/05_camera/01_camera_experiments.ipynb` |

## Structural changes

- Reusable feature calculations moved from `index_script.py` to the
  installable package under `src/jpeg_compression_detection`.
- Batch extraction and the camera demonstration moved to `scripts/` and use
  command-line arguments.
- Hard-coded workstation paths were replaced by constants from
  `jpeg_compression_detection.paths`.
- The five feature tables and their manifest live directly in `data/`; no
  empty source, intermediate, or output placeholders are committed.
- Two preserved reference figures live in `docs/figures`.
- Canonical runs are isolated under the on-demand `results/<run-id>` path and
  include parameters, package/source records, executed notebooks, models,
  figures, and a SHA-256 result manifest. Manual outputs use
  `results/manual`; the complete `results/` tree is ignored by Git.
- Exact direct dependency versions recovered from the Python 3.10.11
  environment are declared in `pyproject.toml`.

## Execution repairs

The migration also repairs workflow blockers without changing estimator
hyperparameters:

- the quality-regression training notebook now writes its trained regressors
  and selects the best validation model explicitly, with a JSON record of the
  selection metric, feature order, and metrics; each candidate is checkpointed
  before the next potentially expensive model begins;
- the downstream quality notebook evaluates that validation-selected alias on
  the original held-out validation and test partitions instead of resplitting
  a sample from the full table, which could include rows already used for
  training;
- repeated-compression generation handles both staged PNG and PPM inputs, and
  its visualization reads the matching generated data rather than the
  unrelated global PPM table;
- the two committed human-face tables replace an unavailable workstation-only
  selfie table in the supplementary cross-dataset comparison;
- batch extraction uses a stable schema, writes a separate error table, and
  fails by default if any image cannot be processed;
- camera cancellation writes nothing, while an explicitly enabled software
  fallback and a physical capture receive distinct names and JSON sidecars;
- output directories are created before writing;
- optional datasets, example images, models, and camera hardware are checked
  before optional cells use them;
- destructive exploratory cleanup is restricted to generated result data and
  is disabled or guarded by default;
- random sampling added during evaluation uses seed 42 where applicable.

The numerical feature implementation was compared directly with the original
module on the same deterministic image; all blockiness ratios, JPEG-quality
estimates, PSNR values, and DCT summary values matched exactly.

The active general feature-exploration notebook now imports that stable
package implementation instead of retaining an older, duplicated experimental
implementation. Results from that exploratory notebook can therefore differ
from its historical Polish snapshot. Treat this as a method-version boundary;
the snapshot remains available for exact review of the older implementation.

## Scientific caveats retained

The migration does not retroactively correct the experimental design. In
particular, row-wise splitting can leak recompressions of the same source
image across splits, and the JFIF-versus-PPM classifier can learn dataset
identity rather than compression format. These issues are documented in
[`DATA.md`](DATA.md) and should be addressed in a new versioned experiment,
not silently changed while reproducing the historical workflow.
