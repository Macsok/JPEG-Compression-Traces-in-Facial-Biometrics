# Compression Inspector

A standalone web application based on `TEST-quality-and-jfif-or-ppm.ipynb`.
Select one or more images, or a folder with subfolders, to predict PPM/JFIF and
estimate JPEG quality. Results include thumbnails, features, probabilities,
and CSV/JSON exports. Once the Docker image has been downloaded, the interface
and analysis work without an internet connection.

## Getting started

Run the following command from this directory:

```bash
docker compose up --build -d
```

Open **http://localhost:8000**. The first image build requires internet access.
Subsequent runs use the models already included in the image.

```bash
docker compose logs -f
docker compose down
```

Alternatively, without Compose:

```bash
docker build -t compression-inspector:1.0.0 .
docker run --rm -p 127.0.0.1:8000:8000 compression-inspector:1.0.0
```

At least 2 GB of available RAM is recommended; larger images may require more.
The application runs on the CPU. Users do not need a GPU, Python, or a notebook
on their computer. Docker must support Linux containers.

## Using the application

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
Change `MAX_UPLOAD_MB` and `MAX_IMAGE_PIXELS` in Compose or with
`docker run -e ...`. Increasing the pixel limit increases memory usage and
analysis time.

## Models and notebook compatibility

`app/models/` contains copies of the original files, approximately 448 MiB in total:

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
`confidence` is the maximum SVC probability, as in the notebook. SVC can sometimes
return a label different from the class with the highest probability; both
values are preserved without correction. Uniform images may produce infinite
PSNR. The application reports a missing feature instead of supplying an
artificial value to the model.

## Distribution through a registry

Replace `REGISTRY/NAMESPACE` with your registry and namespace:

```bash
docker tag compression-inspector:1.0.0 REGISTRY/NAMESPACE/compression-inspector:1.0.0
docker login REGISTRY
docker push REGISTRY/NAMESPACE/compression-inspector:1.0.0
```

Recipients can run the image without this repository or separate model files:

```bash
docker run --rm -p 127.0.0.1:8000:8000 REGISTRY/NAMESPACE/compression-inspector:1.0.0
```

You can also distribute the image as a file:

```bash
docker save -o compression-inspector.tar compression-inspector:1.0.0
docker load -i compression-inspector.tar
```

Copy the entire `compression-web` directory to build the application on another
computer. A parent `.gitignore` may exclude `.pkl` files, so include the actual
`app/models/` files when distributing the source. The built image already
contains them. A standard build targets the architecture of the build machine.

## API and deployment

```bash
curl http://localhost:8000/health
curl -F 'file=@/path/to/image.jpg' http://localhost:8000/api/predict
```

The API accepts one file per request and returns JSON containing `success`,
`filename`, `format`, `prediction`, `confidence` (0–100), `probabilities` (0–1),
`predicted_quality`, `indicators`, `width`, `height`, `elapsed_seconds`, and
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

Recorded verification results: [VALIDATION.md](VALIDATION.md).
