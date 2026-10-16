# Reuse the original, checksum-verified weights without keeping binaries in Git.
FROM ghcr.io/macsok/compression-inspector@sha256:0c378dc5bc38c7f388cc570c2f0546ce2adeedc8cb836dc789c906d7b413aaad AS model-artifacts

FROM python:3.11-slim-bookworm AS runtime
LABEL org.opencontainers.image.source="https://github.com/Macsok/JPEG-Compression-Traces-in-Facial-Biometrics" \
      org.opencontainers.image.title="Compression Inspector" \
      org.opencontainers.image.version="1.1.1"
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 \
    MPLCONFIGDIR=/tmp/matplotlib OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
WORKDIR /opt/compression
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY --from=model-artifacts /opt/compression/models/ ./models/
COPY app/ ./
RUN useradd --uid 10001 --create-home appuser
USER appuser
RUN python -c "from inference import Predictor; Predictor(); print('Embedded models validated')"
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=5s --start-period=60s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health', timeout=4)"
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "1", "--threads", "2", "--timeout", "300", "--access-logfile", "-", "server:app"]

FROM runtime AS test
COPY tests/ /opt/compression/tests/
RUN python -m unittest discover -s tests -v

FROM runtime AS final
