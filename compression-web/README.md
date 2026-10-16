# Compression Inspector

A standalone web application based on `TEST-quality-and-jfif-or-ppm.ipynb`.
Select one or more images, or a folder with subfolders, to predict PPM/JFIF and
estimate JPEG quality. Results include thumbnails, features, probabilities,
and CSV/JSON exports. Once the Docker image has been downloaded, the interface
and analysis work without an internet connection.

## Getting started with Docker Compose

Install Docker with the Compose plugin (included in Docker Desktop). From the
repository root, enter `compression-web/` and start the published application:

```bash
cd compression-web
docker compose pull
docker compose up -d --no-build
```

If your terminal is already in `compression-web/`, omit the `cd` command.
Open **http://localhost:8000** for MEGA, or
**http://localhost:8000/?view=classic** for the previous layout.

`compose.yaml` uses **`ghcr.io/macsok/compression-inspector:1.1.0`**. This standalone
Linux/amd64 image contains the current interface, inference code, runtime and
pretrained weights. Only the Compose file is needed to run it; there are no
source or model mounts and no separate Python installation or training step.

The initial image download requires internet access. With the image cached,
`docker compose up -d --no-build` and analysis work offline; omit `pull` offline.

From `compression-web/`:

```bash
# Check status and follow logs (Ctrl+C exits the log view).
docker compose ps
docker compose logs -f compression

# Restart the service.
docker compose restart compression

# Stop and remove the container; keep the downloaded image.
docker compose down
```

To start again, repeat `docker compose up -d --no-build`. To install a new release,
update the image tag in `compose.yaml`, then run `docker compose pull` and
`docker compose up -d --no-build`. Updating source files alone does not change
the application inside a published image; use a source build or the overlay below.

At least 2 GB of available RAM is recommended; larger images may require more.
The application runs on the CPU. Users do not need a GPU or a notebook on their
computer. Docker must support Linux containers.

## Build from source or preview local edits

To build a standalone image from this checkout, run from `compression-web/`:

```bash
docker compose up --build -d
```

The Dockerfile copies the original model weights from the 1.0.0 image pinned by
SHA-256 digest, then validates all artifacts against `app/artifacts.json`.
No model files need to be added to the checkout. The first source build requires
internet access for the base images and Python dependencies. The resulting image
contains both code and weights and runs without source mounts. Rebuild after
source changes. A source build targets the architecture of the build machine.

For UI and inference edits without rebuilding, use the optional overlay:

```bash
docker compose -f compose.yaml -f compose.preview.yaml up -d --no-build
```

This mounts `app/static`, `app/templates`, `server.py` and `inference.py` read-only
from the checkout, using the 1.1.0 runtime and models. Keep these source files in
place and use both `-f` options for subsequent Compose commands. Restart with
`docker compose -f compose.yaml -f compose.preview.yaml restart compression`
after Python or template edits. Changes to dependencies or other Python modules
require a new image build. To return to the published image, run
`docker compose pull` and `docker compose up -d --no-build` without the overlay.

## Using the application

The default **MEGA** design uses a large, detailed image-processing instrument
built with [Anatomy](https://github.com/wheresryan22/anatomy). It remains fixed
behind the page while you scroll; the camera moves between the sensor, processor
and outputs. A scanning bridge and pulses on the circuit traces animate the
instrument. Its 147 structural solids are generated locally. Eight sliding
spectrum indicators and an inset signal scope follow the same sample column.
Switch between smooth and detailed samples in the illustration controls.
The indicators show log-scaled magnitudes of the column’s orthonormal 1D DCT;
this is an illustrative signal, independent of the uploaded images.

The illustration is independent of uploaded images and model results. Its
slider selects one of eight columns in an illustrative 8 × 8 sample. Use the
slider, keyboard, three camera presets, or pause all ambient motion. The pause
preference is saved locally. Animation is capped at 30 updates per second,
stops in hidden tabs and respects reduced motion. On a phone the controls
collapse as you enter the upload workspace and can be expanded manually.

The previous **Classic** design remains at **http://localhost:8000/?view=classic**;
the header links between versions. The accepted original was saved in commit
`8cae488` before MEGA work began. Both designs support English/Polish and
light/dark themes, with no external fonts, scripts or runtime services.

To change the geometry, edit `tools/build-engine.mjs` (MEGA) or
`tools/build-inspector.mjs` (Classic), then run the corresponding file with Node.
Generated SVGs in `app/templates/` are checked in; building and running the
Docker application does not need Node. The vendored geometry kit's MIT license
is in `tools/anatomy/LICENSE`.

The default interface language is English. Buttons showing the UK and Polish
flags in the upper right corner let you select the language. Your choice is
saved locally in the browser. Changing the language updates messages, errors,
results, and the histogram without reloading the page or interrupting analysis.
Model feature names and CSV/JSON keys remain fixed; exported error messages use
the selected language.

Next to the flags, the sun button selects the light theme and the moon button
selects the dark theme. The active option is highlighted. Icons have tooltips
and screen reader labels, and support keyboard navigation.
The default theme is light. Your choice is saved in the browser independently
of the language and applies to the table, histogram, and image selection panel.

1. Select images or a folder. The browser includes subfolders recursively.
2. Click **Start analysis**. Images are uploaded one at a time, preserving their original bytes.
3. Review the results and details. Invalid images receive individual error messages.
4. Download CSV or JSON results, including after stopping an analysis.

A shared histogram above the table shows predicted quality for JFIF and PPM.
The X axis covers 10–95 in bins of 5; the Y axis shows the number of samples.
The two series overlap. Hover over a bin to see the counts for both groups.
Bins include their lower bound and exclude their upper bound, except for the
last bin, which also includes 95. Results outside the range are counted below
the chart; failed analyses are excluded. The chart updates after each image
and resets when a new analysis starts.

Supported extensions: JPG, JPEG, JFIF, PPM, PNG, BMP, TIF, TIFF, WebP.
Folder selection requires browser support for `webkitdirectory`; selecting
multiple files is an alternative. Drag and drop accepts files; use the button
to select a folder. ZIP archives, RAW images, animations, and multipage TIFF
files are not supported.
Large datasets are uploaded one image at a time. The report and thumbnails are
held in the browser tab's memory. Refreshing the page clears the report and
interrupts the queue. Stopping an analysis allows the current image to finish.
Starting again creates a new report.

Default limits: 64 MB per request (the file must leave room for multipart
headers), 24 million pixels, and a minimum image size of 16 × 16 pixels.
Change `MAX_UPLOAD_MB` and `MAX_IMAGE_PIXELS` in `compose.yaml`, then repeat
the Compose `up` command for your setup to recreate the service with the new
settings. Increasing the pixel limit increases memory usage and analysis time.

## Models and notebook compatibility

The packaged image contains these four original model artifacts, approximately
448 MiB in total. The Dockerfile copies them from the pinned model-artifact
image into `/opt/compression/models/`:

- `best_model_svm_(rbf).pkl`: SVC, with labels 0 = JFIF and 1 = PPM.
- `scaler.pkl`: scaling for the classifier's 15 features.
- `feature_columns.pkl`: feature order.
- `best_compression_model.pkl`: RandomForestRegressor, using 14 features without `estimated_quality`.

`app/index_script.py` retains the original executable code, with comments and
docstrings translated into English. The blockiness,
DCT, and recompression algorithms are preserved, including the original `uint8`
arithmetic, because changing these features would affect the trained models'
predictions. Images are analysed at their original resolution; only thumbnails
are resized. Feature scaling is applied only to the classifier, as in the notebook.

The models were saved using scikit-learn 1.3.2, and the application pins that
version. Do not replace it without validating the models; see the
[model persistence compatibility documentation](https://scikit-learn.org/stable/model_persistence.html).
The image build checks the SHA-256 checksums in `app/artifacts.json`, the model
version, and the feature order. Models and source code are included in the image;
no model mounts or model downloads are required at startup.

Classification describes similarity to the training classes rather than the
actual file format. JPEG quality is an estimate; for PPM it is indicative only.
The API's `confidence` remains the maximum raw SVC probability (0–100), as in
the notebook. SVC can sometimes return a label different from the class with
the highest probability; both values are preserved without correction.
The results table contains Image, Prediction, JPEG quality and Details.
There is no probability column; exact class probabilities remain in Details
and the exports.

Some inputs produce almost the same 78.1839% because their RBF similarities to
all support vectors are negligible. The SVM decision then tends to its fixed
intercept: this is a model limitation, not reuse of a previous image's result.
Details displays **No model support** for these cases, alongside an explanation
that the prediction is a baseline. Raw classification and quality outputs are
retained for notebook compatibility; this change does not retrain either model.

`classification_diagnostics` includes `status`, `kernel_contribution_bound`,
`max_kernel_similarity`, `decision` and `intercept`. Status `baseline` means
`sum(abs(dual_coef) * RBF_similarity) <= 1e-6` in decision units. This absolute
bound avoids mistaking cancellation of strong contributions for lack of support.
Status `responsive` only means that this specific collapse was not detected;
it is not a general out-of-distribution test or a guarantee of accuracy.
CSV exports include `confidence_status` and `kernel_contribution_bound`; JSON
includes all diagnostics. See [VALIDATION.md](VALIDATION.md) for measured examples.

Uniform images may produce infinite
PSNR. The application reports a missing feature instead of supplying an
artificial value to the model.

## Publishing a release to GHCR

Build and verify the image from this directory before publishing. For a new
release, update the version in `Dockerfile` and both Compose files, and use the
same version in these commands. For 1.1.0:

```bash
docker build --target test -t compression-inspector:test-1.1.0 .
docker build -t ghcr.io/macsok/compression-inspector:1.1.0 .
docker login ghcr.io -u macsok
docker push ghcr.io/macsok/compression-inspector:1.1.0
```

For the login password use a GitHub personal access token (classic) with
`write:packages`, as described in the
[GHCR authentication documentation](https://docs.github.com/en/packages/working-with-a-github-packages-registry/working-with-the-container-registry#authenticating-to-the-container-registry).
The SSH key used for Git does not authenticate Docker. Keep versioned release
tags unchanged; publish a new version for subsequent changes.

Recipients can use a copy of `compose.yaml` and run `docker compose pull` followed
by `docker compose up -d --no-build`. The image includes all application code
and model weights, so `compose.preview.yaml` is not needed.

You can also distribute the image as a file:

```bash
docker save -o compression-inspector.tar ghcr.io/macsok/compression-inspector:1.1.0
docker load -i compression-inspector.tar
docker compose up -d --no-build
```

After loading the image, Compose runs it without contacting the registry.

## API and deployment

```bash
curl http://localhost:8000/health
curl -F 'file=@/path/to/image.jpg' http://localhost:8000/api/predict
```

The API accepts one file per request and returns JSON containing `success`,
`filename`, `format`, `prediction`, `confidence` (0–100), `probabilities` (0–1),
`classification_diagnostics`, `predicted_quality`, `indicators`, `width`, `height`, `elapsed_seconds`, and
`thumbnail`.
Error responses: 400 for a missing file, 413 for the upload limit, 415 for an
unsupported extension, 422 for an invalid image or features, and 429 for a busy
model with `Retry-After: 2`. The interface retries requests that return 429.

Gunicorn runs as a user without administrator privileges. A single process
loads the models once, and a lock limits analysis to one image at a time.
A second thread handles requests such as health checks. Uploaded originals are
deleted after each request. Results are not stored on the server.
Compose uses a read-only filesystem and a temporary `/tmp`. The port is bound
to localhost by default. To expose the service over a network, configure the
port binding and your own reverse proxy with TLS, appropriate limits, and
timeouts. The application does not include user accounts or authorization.

## Tests

```bash
docker build --target test -t compression-inspector:test .
```

Tests use the actual model weights. They compare API responses with functions
extracted from the notebook for JPEG, PPM, PNG, BMP, TIFF, and WebP. The reference
functions retain their original executable code, with comments translated into English.
They also check invalid files, limits, uniform images, temporary file cleanup,
and a busy model. Tests require neither datasets nor changes to the original
notebooks.

Run the interface tests in jsdom without installing Node.js on your computer:

```bash
docker build -f tests/ui.Dockerfile -t compression-inspector:ui-test .
```

These tests check the English default, language switching during and after
analysis, retained results, translated errors, the histogram, exports, and
saved preferences. jsdom tests DOM behaviour; it does not perform a visual
review of the page.

Test a running container over HTTP, optionally using your own image directory:

```bash
python3 tests/smoke_http.py ../contest-images
```

Run the illustrative signal checks with `node --test tests/engine_signal.mjs`.
Recorded verification results: [VALIDATION.md](VALIDATION.md).
