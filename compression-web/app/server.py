"""Small stateless web API. Uploaded originals exist only during a request."""
import base64
from io import BytesIO
import os
from pathlib import Path
from tempfile import TemporaryDirectory
from threading import Lock
import time
import warnings

import cv2
from flask import Flask, jsonify, render_template, request
from PIL import Image, UnidentifiedImageError
from werkzeug.exceptions import HTTPException

from inference import Predictor
from input_errors import InputError, error_payload

app = Flask(__name__)
MAX_UPLOAD_MB = int(os.environ.get('MAX_UPLOAD_MB', '64'))
MAX_IMAGE_PIXELS = int(os.environ.get('MAX_IMAGE_PIXELS', '24000000'))
app.config.update(MAX_CONTENT_LENGTH=MAX_UPLOAD_MB * 1024 * 1024,
                  MAX_FORM_PARTS=4, MAX_FORM_MEMORY_SIZE=500000)
Image.MAX_IMAGE_PIXELS = MAX_IMAGE_PIXELS
EXTENSIONS = {'.jpg', '.jpeg', '.jfif', '.ppm', '.png', '.bmp', '.tif', '.tiff', '.webp'}
FORMATS = {'JPEG', 'PPM', 'PNG', 'BMP', 'TIFF', 'WEBP'}
cv2.setNumThreads(1)
predictor = Predictor()
inference_lock = Lock()


@app.get('/')
def index():
    template = 'index-classic.html' if request.args.get('view') == 'classic' else 'index.html'
    return render_template(template)


@app.get('/health')
def health():
    return jsonify(status='ok', models_loaded=True, max_upload_mb=MAX_UPLOAD_MB,
                   max_image_pixels=MAX_IMAGE_PIXELS)


@app.post('/api/predict')
def predict():
    uploads = request.files.getlist('file')
    if len(uploads) != 1 or not uploads[0].filename:
        return jsonify(error_payload('required')), 400
    upload = uploads[0]
    filename = upload.filename.replace('\\', '/').split('/')[-1]
    suffix = Path(filename).suffix.lower()
    if suffix not in EXTENSIONS:
        return jsonify(error_payload('extension')), 415
    if not inference_lock.acquire(blocking=False):
        response = jsonify(error_payload('busy'))
        response.headers['Retry-After'] = '2'
        return response, 429
    started = time.monotonic()
    try:
        with TemporaryDirectory(prefix='compression-') as directory:
            path = Path(directory) / ('image' + suffix)
            upload.save(path)
            with warnings.catch_warnings():
                warnings.simplefilter('error', Image.DecompressionBombWarning)
                with Image.open(path) as source:
                    width, height = source.size
                    if source.format not in FORMATS:
                        raise InputError('format')
                    if min(width, height) < 16:
                        raise InputError('small')
                    if width * height > MAX_IMAGE_PIXELS:
                        raise InputError('pixels', limit=MAX_IMAGE_PIXELS)
                    if getattr(source, 'n_frames', 1) != 1:
                        raise InputError('frames')
                    # Thumbnail only; inference always receives untouched original bytes.
                    source.thumbnail((360, 240))
                    preview = BytesIO()
                    source.convert('RGB').save(preview, format='JPEG', quality=80)
            result = predictor.predict(path)
            result.update(success=True, filename=filename, width=width, height=height,
                          elapsed_seconds=round(time.monotonic() - started, 3),
                          thumbnail='data:image/jpeg;base64,' + base64.b64encode(preview.getvalue()).decode())
            return jsonify(result)
    except InputError as exc:
        return jsonify(filename=filename, **error_payload(exc.code, **exc.params)), 422
    except (ValueError, UnidentifiedImageError, OSError, Image.DecompressionBombError,
            Image.DecompressionBombWarning, cv2.error):
        return jsonify(filename=filename, **error_payload('invalid_image')), 422
    finally:
        inference_lock.release()


@app.errorhandler(HTTPException)
def http_error(error):
    payload = error_payload('upload_limit') if error.code == 413 else error_payload('http', status=error.code)
    return jsonify(payload), error.code


@app.errorhandler(Exception)
def unexpected_error(error):
    app.logger.exception('Prediction request failed')
    return jsonify(error_payload('server')), 500


@app.after_request
def headers(response):
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['Cache-Control'] = 'no-store'
    response.headers['Content-Security-Policy'] = "default-src 'self'; img-src 'self' data:; style-src 'self'; script-src 'self'; frame-ancestors 'none'; base-uri 'self'; form-action 'self'"
    return response
