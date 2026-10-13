from contextlib import redirect_stdout
from io import BytesIO, StringIO
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

import cv2
import numpy as np
from PIL import Image

import notebook_reference as reference
from index_script import detect_jpeg_compression
import server


def sample(extension='.jpg'):
    rng = np.random.default_rng(123)
    pixels = rng.integers(0, 256, size=(80, 96, 3), dtype=np.uint8)
    ok, data = cv2.imencode(extension, pixels)
    assert ok
    return data.tobytes()


class ApplicationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = server.app.test_client()
        reference.loaded_model = server.predictor.classifier
        reference.loaded_scaler = server.predictor.scaler
        reference.loaded_feature_columns = server.predictor.features
        reference.loaded_compression_model = server.predictor.regressor

    def upload(self, data, filename='image.jpg'):
        return self.client.post('/api/predict', data={'file': (BytesIO(data), filename)})

    def test_web_page_and_assets(self):
        page = self.client.get('/')
        self.assertEqual(page.status_code, 200)
        self.assertIn(b'<html lang="en">', page.data)
        for path in ('/static/app.js', '/static/i18n.js', '/static/histogram.js', '/static/style.css', '/health'):
            with self.client.get(path) as response:
                self.assertEqual(response.status_code, 200)
        self.assertTrue(self.client.get('/health').json['models_loaded'])

    def test_predictions_match_original_notebook(self):
        for extension in ('.jpg', '.ppm', '.png', '.bmp', '.tiff', '.webp'):
            with self.subTest(extension=extension):
                data = sample(extension)
                with TemporaryDirectory() as folder:
                    path = Path(folder) / ('image' + extension)
                    path.write_bytes(data)
                    indicators = detect_jpeg_compression(str(path))
                    with redirect_stdout(StringIO()):
                        expected_format = reference.check_image(indicators, verbose=False)
                        expected_quality = reference.predict_compression_quality(indicators)
                response = self.upload(data, 'image' + extension)
                self.assertEqual(response.status_code, 200, response.json)
                actual = response.json
                self.assertEqual(actual['format'], expected_format['format'])
                self.assertEqual(actual['probabilities'], expected_format['probabilities'])
                self.assertAlmostEqual(actual['confidence'], expected_format['confidence'], places=10)
                self.assertAlmostEqual(actual['predicted_quality'], expected_quality['predicted_quality'], places=10)
                self.assertEqual(actual['indicators'], indicators)
                self.assertEqual((actual['width'], actual['height']), (96, 80))
                self.assertTrue(actual['thumbnail'].startswith('data:image/jpeg;base64,'))

    def test_classification_does_not_depend_on_extension(self):
        data = sample('.jpg')
        first = self.upload(data, 'input.jfif').json
        second = self.upload(data, 'input.png').json
        self.assertEqual(first['indicators'], second['indicators'])
        self.assertEqual(first['format'], second['format'])

    def test_bad_file_does_not_break_next_prediction(self):
        self.assertEqual(self.upload(b'not an image').status_code, 422)
        self.assertEqual(self.upload(sample()).status_code, 200)

    def test_request_validation(self):
        response = self.client.post('/api/predict')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json['error_code'], 'required')
        self.assertIn('Upload exactly one image', response.json['error'])
        self.assertEqual(self.upload(b'bad', 'model.pkl').status_code, 415)
        self.assertEqual(self.upload(b'').status_code, 422)
        data = {'file': [(BytesIO(sample()), 'a.jpg'), (BytesIO(sample()), 'b.jpg')]}
        self.assertEqual(self.client.post('/api/predict', data=data).status_code, 400)

    def test_limits(self):
        with patch.dict(server.app.config, MAX_CONTENT_LENGTH=100):
            self.assertEqual(self.upload(sample()).status_code, 413)
        with patch.object(server, 'MAX_IMAGE_PIXELS', 100):
            self.assertEqual(self.upload(sample()).status_code, 422)
        image = BytesIO()
        Image.new('RGB', (8, 8)).save(image, format='PNG')
        self.assertEqual(self.upload(image.getvalue(), 'small.png').status_code, 422)

    def test_upload_larger_than_multipart_buffer(self):
        pixels = np.random.default_rng(7).integers(0, 256, (640, 480, 3), dtype=np.uint8)
        _, data = cv2.imencode('.ppm', pixels)
        self.assertGreater(len(data), 500000)
        response = self.upload(data.tobytes(), 'large.ppm')
        self.assertEqual(response.status_code, 200, response.json)

    def test_constant_image_returns_explanation(self):
        image = BytesIO()
        Image.new('RGB', (64, 64), color=(128, 128, 128)).save(image, format='PNG')
        response = self.upload(image.getvalue(), 'constant.png')
        self.assertEqual(response.status_code, 422)
        self.assertIn('psnr', response.json['error'])
        self.assertEqual(response.json['error_code'], 'invalid_features')
        self.assertIn('psnr', response.json['error_params']['features'])

    def test_busy_server_and_health(self):
        with server.inference_lock:
            response = self.upload(sample())
            self.assertEqual(response.status_code, 429)
            self.assertEqual(response.headers['Retry-After'], '2')
            self.assertEqual(self.client.get('/health').status_code, 200)

    def test_temporary_upload_is_removed(self):
        paths = []
        original = server.predictor.predict
        def record(path):
            paths.append(path)
            return original(path)
        with patch.object(server.predictor, 'predict', side_effect=record):
            self.assertEqual(self.upload(sample()).status_code, 200)
        self.assertTrue(paths)
        self.assertFalse(paths[0].exists())
