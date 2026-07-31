# Research environment

This document defines the reproducible software baseline for the JPEG
compression experiments. The authoritative machine-readable files are
[pyproject.toml](../pyproject.toml),
[environment/environment.yml](../environment/environment.yml), and
[requirements.txt](../requirements.txt).

## Recovered baseline

The notebooks record Python 3.10.11. Plot metadata records Matplotlib 3.7.1,
and the serialized scikit-learn model files were created with scikit-learn
1.3.2. The repository therefore standardizes on Python 3.10.11 and the exact
direct dependency pins below.

| Scope | Package | Version | Primary use |
| --- | --- | ---: | --- |
| Core | NumPy | 1.26.3 | Arrays and numerical feature calculations |
| Core | opencv-python | 4.10.0.84 | Image decoding, JPEG encoding, DCT, and camera access |
| Research | imageio | 2.36.0 | Image and RAW conversion helpers |
| Research | ipykernel | 5.5.6 | Jupyter kernel |
| Research | IPython | 7.34.0 | Interactive notebook runtime |
| Research | joblib | 1.2.0 | Model serialization |
| Research | Matplotlib | 3.7.1 | Figures |
| Research | nbconvert | 7.16.4 | Notebook conversion and execution support |
| Research | nbformat | 5.10.4 | Notebook validation and tooling |
| Research | notebook | 6.5.5 | Classic Jupyter Notebook server |
| Research | pandas | 2.2.2 | Feature tables and analysis |
| Research | Pillow | 11.0.0 | Image conversion and JPEG generation |
| Research | pygame | 2.5.2 | Optional camera experiment |
| Research | rawpy | 0.25.1 | Optional camera-RAW conversion |
| Research | requests | 2.32.3 | Optional acquisition helpers in historical notebooks |
| Research | scikit-learn | 1.3.2 | Classification, regression, scaling, and metrics |
| Research | SciPy | 1.10.1 | Statistical diagnostics |
| Research | seaborn | 0.12.2 | Statistical plots |
| Research | tqdm | 4.65.0 | Optional progress reporting |
| Test | pytest | 6.2.5 | Automated tests |

The Conda specification also pins pip 25.2. Build requirements are declared
separately in `pyproject.toml` as `setuptools>=68` and `wheel`.

### Recovered Jupyter component snapshot

The reference Python 3.10.11 environment reported the following Jupyter
components. These include transitive components that are not all direct pins
in `pyproject.toml`; capture them in the full freeze for a release.

| Component | Version |
| --- | ---: |
| IPython | 7.34.0 |
| ipykernel | 5.5.6 |
| ipywidgets | 8.1.1 |
| jupyter_client | 7.4.9 |
| jupyter_core | 5.3.0 |
| jupyter_server | 2.14.2 |
| nbclient | 0.10.0 |
| nbconvert | 7.16.4 |
| nbformat | 5.10.4 |
| notebook | 6.5.5 |

JupyterLab was not installed in the recovered environment. Use the classic
Notebook server (`python -m notebook`) unless a separately documented
JupyterLab installation is intentionally introduced.

These are exact *direct* pins, not a complete transitive lock. The current
[`environment/requirements-lock.txt`](../environment/requirements-lock.txt)
is an installation entry point for the pinned project dependencies; it does
not enumerate every transitive wheel. After validating a clean environment,
capture `pip freeze --all` as described below and retain it with the research
release.

## Setup with `venv`

Run all commands from the repository root. Confirm that the interpreter is
exactly Python 3.10.11 before installing packages.

### Windows PowerShell

```powershell
py -3.10 -m venv .venv
.\.venv\Scripts\Activate.ps1
python --version
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m ipykernel install --user --name jpeg-compression-research --display-name "JPEG compression research (Python 3.10.11)"
python -m pytest
```

If `py -3.10` resolves to a different 3.10 patch release, install or select
Python 3.10.11 explicitly and recreate `.venv`.

### Linux or macOS

```bash
python3.10 -m venv .venv
source .venv/bin/activate
python --version
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m ipykernel install --user --name jpeg-compression-research --display-name "JPEG compression research (Python 3.10.11)"
python -m pytest
```

Start the notebook server with `python -m notebook` and select the registered
kernel. A notebook must be run with the repository root as its working
directory so that the repository-relative paths resolve consistently.

## Setup with Conda

The same file works on Windows, Linux, and macOS:

```bash
conda env create -f environment/environment.yml
conda activate jpeg-compression-research
python --version
python -m pytest
```

The Conda environment installs the project in editable mode with the
`research` and `test` extras. Recreate the environment instead of upgrading
individual packages in place when reproducing published results.

## Platform and GUI requirements

Batch feature extraction is CPU-only and does not require a GPU. The camera
demonstration is different: it requires a physical camera, permission to use
it, and an interactive desktop session supported by `cv2.imshow`. Keep
`opencv-python`; do not replace it with `opencv-python-headless` for camera
runs.

- **Windows:** enable Camera access for desktop applications. Camera indices
  and capture backends can change after reconnecting a device or updating a
  driver.
- **Linux:** an X11 or Wayland display and access to the relevant
  `/dev/video*` device are required. Membership of the system's video-device
  group may be necessary. Remote and container sessions normally need
  explicit camera and display forwarding.
- **macOS:** grant Camera permission to the terminal or Python host. The first
  run can pause while macOS displays the permission prompt.
- **Headless systems:** run only non-camera workflows. Plotting notebooks can
  use a non-interactive Matplotlib backend, but `cv2.imshow` cannot.

For a camera experiment, record at least the camera make and model, driver or
capture backend, camera index, resolution, frame rate, exposure, white
balance, display model, display brightness, camera-to-display distance,
viewing angle, ambient lighting, output format, and OpenCV build information.
The fallback that copies the source image when no camera is available is a
software smoke test, not a physical-camera measurement.

## Determinism and compatibility caveats

Exact Python packages are necessary but not sufficient for byte-identical
results.

- JPEG bytes can differ with the OpenCV, Pillow, and linked libjpeg or
  libjpeg-turbo build, even when the Python API version is identical.
- RAW conversion depends on the rawpy/LibRaw build and camera profile.
- Canonical model splits, stochastic estimators, and validation subsampling
  use seed 42. Some optional exploratory cells in the historical snapshot were
  unseeded; set all seeds explicitly before extending those experiments.
- `n_jobs=-1`, BLAS implementations, CPU instruction sets, and thread
  scheduling can introduce small numerical or ordering differences. Record
  thread settings and hardware; use a fixed thread count for strict
  comparisons.
- Camera frames are inherently non-deterministic. Reproduction means
  repeating a documented protocol, not reproducing identical pixels.
- Joblib/pickle files are version-sensitive and unsafe to load from an
  untrusted source. Verify their checksums and use scikit-learn 1.3.2.
- Feature extraction intentionally preserves the historical calculations used
  to create the processed CSV files. An algorithm correction requires a new
  data/model version rather than silently overwriting the published tables.

For controlled runs, set Python, NumPy, and estimator seeds to 42, keep all
variants of one source image in the same data split, sort input paths, and
write the effective configuration beside each generated result.

## Capture the complete environment

The canonical runner automatically writes `packages.json`,
`source-manifest.json`, `run.json`, and a post-run
`result-manifest.json` under `results/<run-id>`. The source manifest
is the code identity when Git metadata is unavailable. Add the platform and
hardware records below to that same run directory. The example identifier is
`paper-v1`; replace it consistently and never overwrite a published run.

### Cross-platform Python records

```bash
python -m pip freeze --all > results/paper-v1/environment/pip-freeze.txt
python -c "import platform, sys; print(sys.version); print(platform.platform()); print(platform.machine()); print(platform.processor())" > results/paper-v1/environment/python-platform.txt
python -c "import cv2; print(cv2.getBuildInformation())" > results/paper-v1/environment/opencv-build.txt
python -c "from PIL import features; print('JPEG codec:', features.version_codec('jpg'))" > results/paper-v1/environment/pillow-codecs.txt
python -c "from importlib.metadata import distributions; print('\n'.join(sorted('{}=={}'.format(d.metadata.get('Name'), d.version) for d in distributions() if d.metadata.get('Name'))))" > results/paper-v1/environment/installed-packages.txt
python -m pytest > results/paper-v1/environment/test-results.txt
```

Create `results/paper-v1/environment` first with
`New-Item -ItemType Directory -Force
results/paper-v1/environment` in PowerShell or
`mkdir -p results/paper-v1/environment` on Linux/macOS. The installed
package command enumerates what is present and therefore does not fail merely
because an optional historical component such as `ipywidgets` is absent.

When the project is in a Git checkout, also record the revision and worktree
state:

```bash
git rev-parse HEAD > results/paper-v1/environment/git-revision.txt
git status --short >> results/paper-v1/environment/git-revision.txt
```

### Windows hardware record

```powershell
Get-CimInstance Win32_OperatingSystem | Select-Object Caption,Version,OSArchitecture | Format-List | Out-File results/paper-v1/environment/windows-os.txt
Get-CimInstance Win32_Processor | Select-Object Name,NumberOfCores,NumberOfLogicalProcessors | Format-List | Out-File results/paper-v1/environment/windows-cpu.txt
Get-PnpDevice -Class Camera -PresentOnly | Select-Object Status,FriendlyName | Format-Table | Out-File results/paper-v1/environment/windows-cameras.txt
```

### Linux hardware record

```bash
uname -a > results/paper-v1/environment/linux-system.txt
lscpu > results/paper-v1/environment/linux-cpu.txt
ls -l /dev/video* > results/paper-v1/environment/linux-cameras.txt 2>&1
# If v4l2-ctl is installed:
v4l2-ctl --all >> results/paper-v1/environment/linux-cameras.txt
```

### macOS hardware record

```bash
sw_vers > results/paper-v1/environment/macos-system.txt
system_profiler SPHardwareDataType > results/paper-v1/environment/macos-hardware.txt
system_profiler SPCameraDataType > results/paper-v1/environment/macos-cameras.txt
```

Review captured files before publication: OpenCV builds and hardware tools can
include user-specific paths, host names, device identifiers, or serial
numbers. Redact private identifiers without removing the versions and settings
needed to interpret the experiment. After adding or redacting all manual
records, refresh the checksums exactly once:

```bash
python scripts/run_reproduction.py --finalize-only --run-id paper-v1
```

Do not modify the run directory after finalization. If anything must change,
use a new run identifier or explicitly finalize again and document why.
