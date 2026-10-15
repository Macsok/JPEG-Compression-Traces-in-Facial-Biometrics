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

# Anatomy interface refresh — 2026-10-15

- Existing jsdom localization suite passed against the updated application
  files: selection, analysis, retained reports, histogram, exports, language,
  theme, accessibility labels and unavailable local storage.
- Browser review at 1440 px and 390 px, in English/Polish and light/dark themes:
  no horizontal page overflow; browser console clean.
- Figure checked at 4× in both themes. Anatomy line checks reported **0 of 70
  floating ends** at the first and last column.
- Native range keyboard controls update the carriage, highlighted column and
  readout. Reduced-motion mode stays still and permits manual column selection.
- Pointer selection settles correctly, the automatic tour moves, and animation
  stops when the figure is outside the viewport.
- Real end-to-end check using a generated 96 × 96 JPEG: successful response,
  JFIF classification and quality estimate 79.04; report, thumbnail and histogram
  displayed correctly. Backend/model code was not modified.
- Sample grayscale uses SVG fill attributes to comply with the existing CSP;
  no inline styles or relaxed security policy are needed.
