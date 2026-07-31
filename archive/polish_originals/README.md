# Historical Polish-language snapshot

This directory is an immutable research snapshot of the original
Polish-language materials captured before the repository was reorganized and
translated to English.

It contains:

- the original project description as
  [`README.pl.md`](README.pl.md);
- the original Python files under [`scripts/`](scripts/);
- the original notebook sources and their historical outputs under
  [`notebooks/`](notebooks/).

The snapshot exists for traceability: it allows a reviewer to compare the
active English files with the wording, paths, execution state, and results
available at the time of migration. Polish text, historical absolute paths,
stale notebook outputs, and missing external resources inside this directory
are therefore preserved evidence, not active configuration.

Do not import, execute, format, translate, clear outputs from, or otherwise
edit files in this snapshot. Some historical notebook cells create, overwrite,
or remove generated files. Run only the active code and notebooks from the
repository root, [`src/`](../../src/), and [`scripts/`](../../scripts/).
The file [`SHA256SUMS`](SHA256SUMS) records the immutable snapshot contents.

The active copies may differ in the following intentionally limited ways:

- comments, docstrings, Markdown, messages, and plot labels are in English;
- machine-specific paths are replaced with repository-relative paths;
- optional datasets and model artifacts are checked before use so a clean
  `Run All` can report missing inputs instead of depending on one workstation;
- reusable code is imported from the active package rather than copied among
  notebooks.

Translation or path cleanup must not be presented as a change to the
scientific method. If an algorithm, feature definition, data filter, model
hyperparameter, split, metric, or codec setting changes, record it as a
separate method/version change and regenerate the affected data, models, and
figures under new artifact names.

When citing or reviewing a result, identify whether it came from the active
reproducible workflow or from this historical snapshot. If a correction to the
snapshot is ever unavoidable, create a new dated snapshot and checksum
manifest rather than rewriting these files in place.
