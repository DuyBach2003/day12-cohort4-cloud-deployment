# ============================================================
# Dockerfile — Cloud Run agent (multi-stage)
#
# Build (từ thư mục production-cloud-run/, theo cloudbuild.yaml):
#   docker build -t ai-agent .
# ============================================================

FROM python:3.11-slim AS builder

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt


FROM python:3.11-slim AS runtime

RUN groupadd -r appuser && useradd -r -g appuser appuser

WORKDIR /app

COPY --from=builder /root/.local /home/appuser/.local
COPY app.py .
COPY utils/ utils/

RUN chown -R appuser:appuser /app

USER appuser

ENV PATH=/home/appuser/.local/bin:$PATH
ENV PYTHONPATH=/app

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" || exit 1

# Cloud Run inject PORT — uvicorn đọc qua app.py, nhưng expose 8000 mặc định
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
