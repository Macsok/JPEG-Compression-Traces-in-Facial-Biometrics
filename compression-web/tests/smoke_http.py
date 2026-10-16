"""Test a running container over HTTP using a local image folder (stdlib only)."""
import argparse
import json
from pathlib import Path
import urllib.request
import uuid


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('directory', type=Path)
    parser.add_argument('--url', default='http://127.0.0.1:8000')
    args = parser.parse_args()
    for route in ('/health', '/', '/static/app.js', '/static/style.css'):
        with urllib.request.urlopen(args.url + route, timeout=30) as response:
            assert response.status == 200
            print(route, response.status)
    count = 0
    for path in sorted(args.directory.iterdir()):
        if path.suffix.lower() not in {'.jpg', '.jpeg', '.jfif', '.png', '.ppm', '.bmp', '.tif', '.tiff', '.webp'}:
            continue
        boundary = uuid.uuid4().hex
        # An ASCII transport name avoids encoding ambiguities in multipart headers.
        body = (f'--{boundary}\r\nContent-Disposition: form-data; name="file"; filename="image{path.suffix}"\r\n'
                'Content-Type: application/octet-stream\r\n\r\n').encode()
        body += path.read_bytes() + f'\r\n--{boundary}--\r\n'.encode()
        request = urllib.request.Request(args.url + '/api/predict', data=body,
                                         headers={'Content-Type': f'multipart/form-data; boundary={boundary}'})
        with urllib.request.urlopen(request, timeout=300) as response:
            result = json.load(response)
        assert result['success'], result
        count += 1
        print(json.dumps({'filename': path.name, **{key: result[key] for key in (
            'format', 'confidence', 'classification_diagnostics', 'predicted_quality', 'elapsed_seconds')}}, ensure_ascii=False))
    assert count, 'No images found'
    print(f'HTTP smoke test passed: {count} images.')


if __name__ == '__main__':
    main()
