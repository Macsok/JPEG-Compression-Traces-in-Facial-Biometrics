"""Stable error codes let the UI translate existing results without re-uploading."""
MESSAGES = {
    'required': 'Upload exactly one image in the file field.',
    'extension': 'Unsupported image extension.',
    'busy': 'The server is busy. Please try again later.',
    'format': 'Unsupported image format.',
    'small': 'The minimum image size is 16 × 16 pixels.',
    'pixels': 'The image exceeds the limit of {limit} pixels.',
    'frames': 'Choose a single-frame / single-page image.',
    'invalid_image': 'The image could not be read. Choose a valid, supported image.',
    'invalid_features': 'Cannot calculate features: {features}. The image may be uniform or too small.',
    'upload_limit': 'The upload exceeds the request size limit.',
    'http': 'HTTP error {status}.',
    'server': 'Analysis failed. Details are available in the server logs.',
}


class InputError(ValueError):
    def __init__(self, code, **params):
        self.code = code
        self.params = params
        super().__init__(MESSAGES[code].format(**params))


def error_payload(code, **params):
    return dict(success=False, error_code=code, error_params=params,
                error=MESSAGES[code].format(**params))
