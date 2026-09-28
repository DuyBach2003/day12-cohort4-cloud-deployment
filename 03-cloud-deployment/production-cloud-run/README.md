# production-cloud-run/ — GCP Cloud Run + CI/CD

Production-grade deployment: tests → build image → push registry → deploy Cloud Run, tất cả tự động qua Cloud Build.

```
production-cloud-run/
├── app.py              # Agent (Cloud Run-ready)
├── requirements.txt
├── utils/mock_llm.py   # Mock LLM dùng chung
├── tests/test_app.py   # Chạy trong bước "test" của cloudbuild.yaml
├── Dockerfile          # Multi-stage build
├── cloudbuild.yaml     # CI/CD pipeline (test → build → push → deploy)
└── service.yaml        # Cloud Run service definition (IaC)
```

## Chạy thử local

```bash
cd 03-cloud-deployment/production-cloud-run
pip install -r requirements.txt
pytest tests/ -v

python app.py
# hoặc: uvicorn app:app --host 0.0.0.0 --port 8000

curl http://localhost:8000/health
curl -X POST http://localhost:8000/ask -H "Content-Type: application/json" -d '{"question": "Hello"}'
```

## Build & deploy qua Cloud Build (CI/CD)

```bash
# Từ thư mục production-cloud-run/
gcloud builds submit --config cloudbuild.yaml .
```

`cloudbuild.yaml` chạy tuần tự: `pytest` → `docker build` → push lên Artifact/Container Registry → `gcloud run deploy`.

## Deploy trực tiếp bằng service.yaml (Infrastructure as Code)

```bash
# Thay PROJECT_ID trong service.yaml trước
gcloud run services replace service.yaml --region=asia-southeast1
```

## Environment variables

| Biến | Nguồn | Ghi chú |
|------|-------|---------|
| `PORT` | Cloud Run inject | Agent phải bind đúng port này |
| `ENVIRONMENT` | `service.yaml` | `production` |
| `OPENAI_API_KEY` | Secret Manager (`openai-key`) | Không hardcode |
| `AGENT_API_KEY` | Secret Manager (`agent-api-key`) | Không hardcode |

## Câu hỏi thảo luận

1. Tại sao Cloud Run cần cả `/health` (liveness) và `/ready` (startup probe)?
2. `minScale: 1` trong `service.yaml` đánh đổi điều gì giữa cost và cold start?
3. Vì sao secrets được inject qua Secret Manager thay vì `envVars` thường?
