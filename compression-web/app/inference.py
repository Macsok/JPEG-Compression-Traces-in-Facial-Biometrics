"""Inference matching TEST-quality-and-jfif-or-ppm.ipynb, without training."""
from pathlib import Path
import hashlib
import json
import warnings

import joblib
import numpy as np
import pandas as pd
from sklearn.exceptions import InconsistentVersionWarning

from index_script import detect_jpeg_compression
from input_errors import InputError

BASE = Path(__file__).resolve().parent


class Predictor:
    def __init__(self):
        # Check the exact artifacts distributed with this application.
        manifest = json.loads((BASE / 'artifacts.json').read_text())
        for name, expected in manifest.items():
            with (BASE / name).open('rb') as artifact:
                digest = hashlib.file_digest(artifact, 'sha256').hexdigest()
            if digest != expected:
                raise RuntimeError(f'Artifact checksum mismatch: {name}')
        with warnings.catch_warnings():
            warnings.simplefilter('error', InconsistentVersionWarning)
            self.classifier = joblib.load(BASE / 'models/best_model_svm_(rbf).pkl')
            self.regressor = joblib.load(BASE / 'models/best_compression_model.pkl')
            self.scaler = joblib.load(BASE / 'models/scaler.pkl')
            self.features = list(joblib.load(BASE / 'models/feature_columns.pkl'))
        self.quality_features = [c for c in self.features if c != 'estimated_quality']
        for model, columns in [(self.scaler, self.features), (self.regressor, self.quality_features)]:
            if model.n_features_in_ != len(columns):
                raise RuntimeError('Model feature count mismatch')
            if hasattr(model, 'feature_names_in_') and list(model.feature_names_in_) != columns:
                raise RuntimeError('Model feature order differs from notebook')
        if set(self.classifier.classes_) != {0, 1}:
            raise RuntimeError('Expected classifier labels 0=JFIF, 1=PPM')
        # One inference at a time; avoid duplicating the large forest per process.
        self.regressor.n_jobs = 1

    def predict(self, path):
        indicators = detect_jpeg_compression(str(path))
        if not isinstance(indicators, dict):
            raise InputError('invalid_image')
        invalid = [c for c in self.features if indicators.get(c) is None
                   or not np.isfinite(indicators[c])]
        if invalid:
            raise InputError('invalid_features', features=', '.join(invalid))
        frame = pd.DataFrame([{c: indicators[c] for c in self.features}])
        scaled = self.scaler.transform(frame)
        label = int(self.classifier.predict(scaled)[0])
        raw_probabilities = self.classifier.predict_proba(scaled)[0]
        probabilities = {('PPM' if int(c) == 1 else 'JFIF'): float(p)
                         for c, p in zip(self.classifier.classes_, raw_probabilities)}
        quality = float(self.regressor.predict(frame[self.quality_features])[0])
        return {
            'format': 'PPM' if label == 1 else 'JFIF',
            'prediction': label,
            'confidence': float(max(raw_probabilities) * 100),
            'probabilities': probabilities,
            'predicted_quality': quality,
            'indicators': indicators,
        }
