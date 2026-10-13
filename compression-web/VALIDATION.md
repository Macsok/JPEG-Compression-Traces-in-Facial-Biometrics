# Validation — 2026-10-13

- Built the Linux/amd64 image `compression-inspector:1.0.0` with model weights included.
- `docker build --target test`: 10 tests passed, including agreement between
  predictions and all features from the notebook functions for six image formats.
- Started the application through Compose with a read-only filesystem and `/tmp`
  on tmpfs, without mounting models or the source repository. Health check: `healthy`.
- The page, JavaScript, CSS, and `/health` endpoint returned HTTP 200.
- Uploaded five real images from `contest-images` to the container over HTTP:

| File | Prediction | JPEG quality |
| --- | --- | ---: |
| `00732_960620_fa.ppm.jpg80.jpg` | JFIF | 81.59 |
| `00732_960620_fa.ppm.jpg87.jpg` | JFIF | 86.95 |
| `00732_960620_fa.ppm.png` | PPM | 93.50 |
| `download.jfif` | JFIF | 71.89 |
| `random-person-2.jpeg` | JFIF | 91.72 |

These are model outputs, not a measurement of accuracy on an independent dataset.
The test images are not included in the application image.

At the initial validation, the SHA-256 checksums of the four model artifacts and
`index_script.py` matched the originals in the project. All new files were placed
in `compression-web`. The extractor's comments and docstrings were subsequently
translated into English, and its checksum in `app/artifacts.json` was updated.
An AST comparison confirmed that its executable code, excluding docstrings,
was unchanged by the translation. The model artifacts were not modified.

No interaction test was performed in a real browser because no browser tool
was available in the environment. This initial interface verification covered
HTTP responses for the page and its assets. Folder selection, buttons, and
exports still require verification in the user's browser.

After this initial validation, the container was stopped. Docker images remained
available locally and were not pushed to a registry. To start the application,
run `docker compose up -d`.
