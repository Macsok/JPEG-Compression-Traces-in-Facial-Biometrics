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

# MEGA and probability diagnostics — 2026-10-16

- Classic was saved in commit `8cae488`; MEGA is on `design/anatomy-mega`.
  `/` serves MEGA and `/?view=classic` serves the previous layout.
- MEGA: 128 structural solids, 1,471 SVG paths; fixed instrument, moving scanner,
  signal pulses, scroll camera, pointer parallax, three presets and saved pause.
- Geometry reviewed at 4× in both themes; line checks found **0 floating ends**
  among 116 ends on 246 lines, including both scan endpoints.
- Real-browser interaction suite passed: approximately 30 animation updates/s,
  complete pause after settling, synchronized keyboard column/die/output,
  camera presets, language and theme, fixed background while scrolling,
  actual JPEG submission, report and language switching without losing results.
- Visual review at 1440 × 1000 and 390 × 844, light/dark and English/Polish.
  Mobile has no horizontal page overflow; controls automatically collapse in
  the workspace and can be expanded manually. Reduced motion stays still and
  allows keyboard column selection. Browser console clean.
- All **11 backend tests** passed against the packaged model weights. Predictions,
  raw probabilities, confidence, quality and features remain identical to the
  notebook reference for six formats. The new diagnostic is also checked against
  a support vector and a distant vector where the decision equals the intercept.
- jsdom suite passed, including translated baseline messages, CSV/JSON diagnostic
  export and raw probability preservation. No new model weights were trained.
- Five actual local photographs passed the updated HTTP smoke test. Two examples
  explain the repeated confidence reported by the user:

| Sample | Raw confidence (%) | Decision | Absolute kernel contribution bound | Status |
| --- | ---: | ---: | ---: | --- |
| `00732_960620_fa.ppm.jpg80.jpg` | 78.1838824241 | -0.084166364756 | 6.4123e-25 | baseline |
| `00732_960620_fa.ppm.jpg87.jpg` | 78.1838886077 | -0.084166425835 | 6.1432e-8 | baseline |
| `00732_960620_fa.ppm.png` | 99.9999999892 | 2.156293511972 | 44.6351 | responsive |
| `download.jfif` | 99.9518384341 | -1.156011143640 | 1.6906 | responsive |
| `random-person-2.jpeg` | 99.9999422081 | -2.289101104641 | 41.1825 | responsive |

The classifier intercept is -0.08416636475643523. For the first two samples,
RBF kernel contributions are negligible, so the decision and calibrated
probability approach a constant. These are independent computations per image,
not a cached result. A separate presentation issue rounded near-one probabilities
to 100.0%. The table now shows >99.9% and keeps exact values in Details.

The UI displays **No model support / Brak wsparcia modelu** when the sum of
absolute kernel contributions is at most 1e-6 decision units. This only detects
collapse to the intercept; `responsive` is not a certification of reliability.
A real-photo browser submission verified the warning in the rendered report.
The raw result stays in exports, alongside its diagnostic. Correcting the
model's generalization requires a separate training and validation effort.

Reproduce API checks with `python3 tests/smoke_http.py /path/to/images`.
`tests/engine_browser.json` contains the browser interaction sequence for the
Anatomy `drive.mjs` tool. Preview uses `compose.preview.yaml` and the packaged
1.0.0 image's weights, with local code mounted read-only. No image was published.

# Signal instrument refinement — 2026-10-16

- Removed the Model probability column from both MEGA and Classic. The report
  now has four columns; error rows span the remaining three. Probabilities and
  the baseline diagnostic remain in expandable Details and exports.
- Extended the instrument to 147 solids: eight physical spectrum indicators
  with sliding cursors, inset signal scope, moving sample reticle, detailed
  scales and fasteners. Improved contrast in both themes and corrected a
  cooling-assembly fastener's drawing order so the fins occlude it correctly.
- One shared sample module drives the illustrated pixels, scope and orthonormal
  1D DCT magnitudes. The smooth/detail switch changes all three together. The
  displayed spectrum uses logarithmic magnitude; it is not inference telemetry.
- `node --test tests/engine_signal.mjs`: constant/zero/DC and cosine-basis checks
  passed. UI suite passed with four-column success/error rows and intact exports.
- Extended real-browser suite passed: sample switch updates scope and spectrum
  while paused, motion settles, all original controls and real JPEG analysis
  work, and the resulting table has four columns. Console clean.
- Reviewed the entire instrument at 4× in light/dark and at scan endpoints.
  Line checks: **0 floating ends among 134 ends on 260 lines**, including the
  inset scope's trace/grid. Mobile 390 × 844 stays within the viewport; dock
  collapses in the workspace. Reduced motion stays still and supports immediate
  manual sample changes and keyboard selection.

# Standalone GHCR release 1.1.0 — 2026-10-16

- Built the final Linux/amd64 image from the current application source.
  Model artifacts are copied during the build from the original 1.0.0 image
  pinned to digest `sha256:0c378dc5bc38c7f388cc570c2f0546ce2adeedc8cb836dc789c906d7b413aaad`;
  SHA-256 validation and feature-order checks passed. No local model files needed.
- The Docker test stage passed all 11 backend tests. The separate UI image passed
  the jsdom suite. The final runtime image excludes the test-stage files.
- Started the final image with Compose in an isolated project on port 18080:
  healthy, read-only filesystem, non-root user, no source/model bind mounts.
  All five local sample images passed the HTTP smoke test.
- The browser interaction suite passed against this standalone container:
  MEGA/Classic, sample and spectrum controls, pause, keyboard, themes, languages,
  scrolling, real JPEG analysis and four-column report. Browser console clean.
- `compose.yaml` now selects 1.1.0 from GHCR. Normal startup uses
  `docker compose pull` then `docker compose up -d --no-build`.
  `compose.preview.yaml` remains an optional overlay for local source edits.
- Published `ghcr.io/macsok/compression-inspector:1.1.0` with digest
  `sha256:959b6998034176bef2dfb0c2a57358ec304acc47cf35757d445f697c555ee109`.
  Anonymous registry inspection confirmed the Linux/amd64 manifest matches the
  tested image. The previous 1.0.0 tag was not changed. The isolated test project
  was removed after verification.

# Scanner head occlusion fix — 2026-10-16

- Draw the optical window before its housing and the housing before the beam.
  Two carriage cheeks now connect the lower housing to its top cover around
  the beam. Uprights end at their mounting caps instead of intersecting them.
  Regenerated the checked-in SVG (149 structural solids).
- Anatomy depth-order verification of the bridge against neighboring slabs
  passed at 0%, 25%, 50%, 75% and 100% of travel, using the rendered part order.
- Reviewed columns 1, 4 and 8 in both themes, plus 4× head close-ups.
  All six line checks reported 0 floating ends; browser console clean.
- The existing browser interaction suite passed against local Compose preview,
  including pause, keyboard controls, sample changes and real JPEG analysis.
  This source fix is available in local preview; the published GHCR 1.1.0 image
  still contains the previous geometry.

# Whole-instrument layer correction — 2026-10-16

- Corrected memory latch/board order and removed their intersecting edges.
  Moved the scope behind the sensor rails; split the rail drawing around the
  sample tray and placed each rear end stop behind its guide.
- Moved the capacitor row behind the power packages. Split processor terminal
  banks around the socket and mounting clamps around the package.
- Added `node tools/build-engine.mjs --audit`, using vendored Anatomy tools.
  It records all 149 rounded-prism envelopes and reads their actual final SVG
  order. All 32 sampled scan/spectrum poses passed with 0 incorrect overlaps.
  Decorative bevels and surface engravings require separate visual checks.
- Reviewed upper/lower instrument regions at 4× in light and dark themes.
  Browser line checks at columns 1, 4 and 8 passed in both themes: 0 floating
  ends among 134 ends on 260 lines. The application browser suite passed,
  including pause, sample switching, scrolling and real JPEG analysis.
- Refreshed local Compose preview on port 8000. No new GHCR image published.
