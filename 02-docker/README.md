# Section 2 — Docker: Đóng Gói Agent Thành Container

## Mục tiêu học
- Hiểu container là gì và tại sao cần nó
- Viết Dockerfile đúng cách (single vs multi-stage)
- Dùng Docker Compose để chạy multi-service stack
- Tối ưu image size và layer cache

---

## Tổng quan các folder

```
02-docker/
├── develop/          # Basic — Dockerfile đơn giản (Python)
├── layer-order/      # So sánh thứ tự layers ảnh hưởng cache (Go)
├── multi-stages/     # So sánh single-stage vs multi-stage build (Go)
└── production/       # Advanced — Multi-stage + Docker Compose (Python)
```

---

## Ví dụ Basic — Dockerfile Đơn Giản

```
develop/
├── app.py
├── Dockerfile          # Single-stage, dễ hiểu
├── .dockerignore
└── requirements.txt
```

### Chạy thử
```bash
# IMPORTANT: Build from project root!
cd ../..  # Go to project root

# Build image
docker build -f 02-docker/develop/Dockerfile -t agent-develop .

# Xem size
docker images agent-develop

# Chạy container
# -p 8000:8000 : map port 8000 của máy host → port 8000 trong container
# -d           : chạy ở chế độ detached (nền), terminal không bị block
# agent-develop: tên image đã build ở bước trên
docker run -p 8000:8000 -d agent-develop

# Xem container đang chạy
docker ps

# Truy cập vào bên trong container đang chạy (mở shell tương tác)
# -i: giữ kết nối stdin mở | -t: cấp terminal giả (pseudo-TTY)
# Hữu ích để debug, kiểm tra file, xem log, hoặc chạy lệnh trực tiếp trong container

docker exec -it <container-id> sh

# Test
curl http://localhost:8000/health
```

---


**Hai loại cache khác nhau:** `pip install --no-cache-dir` tắt cache tải package của pip, không tắt Docker layer cache. `docker build --no-cache` mới yêu cầu build lại các bước; không dùng cờ này khi đang thử quan sát cache.

Tham khảo: [Docker — tối ưu thứ tự layers](https://docs.docker.com/build/cache/optimize/#order-your-layers), [quy tắc cache invalidation](https://docs.docker.com/build/cache/invalidation/), [Dockerfile reference](https://docs.docker.com/reference/dockerfile/).

---

## Layer Order — Thứ Tự Layers Ảnh Hưởng Cache

```
layer-order/
├── main.go
├── go.mod
├── Dockerfile              # COPY . . gộp — mọi thay đổi invalidate cache
├── Dockerfile.deps-first   # ✅ Copy go.mod trước → cache deps layer
└── Dockerfile.source-first # ❌ Copy source trước → deps luôn rebuild
```

### Chạy thử
```bash
cd layer-order

# So sánh: sửa main.go rồi build lại với mỗi Dockerfile
docker build -f Dockerfile.deps-first -t layer-deps .
docker build -f Dockerfile.source-first -t layer-source .

# Quan sát: deps-first dùng cache cho bước go build deps
# source-first phải rebuild tất cả
```

> Chi tiết: xem [layer-order/README.md](layer-order/README.md)

---

## Multi-Stage — So Sánh Single vs Multi-Stage Build

```
multi-stages/
├── main.go
├── go.mod
├── Dockerfile               # Single-stage (~800 MB)
└── Dockerfile-multistage    # Multi-stage (~15 MB)
```

### Chạy thử
```bash
cd multi-stages

docker build -f Dockerfile -t myapp-single .
docker build -f Dockerfile-multistage -t myapp-multi .

# So sánh size
docker images | grep myapp
```

> Chi tiết: xem [multi-stages/README.md](multi-stages/README.md)

---

## Ví dụ Advanced — Multi-Stage + Docker Compose

```
production/
├── app.py
├── Dockerfile              # Multi-stage build → image nhỏ hơn nhiều
├── docker-compose.yml      # Full stack: agent + vector store + redis
├── nginx/
│   └── nginx.conf          # Reverse proxy
├── .dockerignore
└── requirements.txt
```

### Chạy thử
```bash
# From project root
cd ../..  # if not already there

# Khởi động toàn bộ stack (1 lệnh!)
docker compose -f 02-docker/production/docker-compose.yml up

# Xem các service đang chạy
docker compose -f 02-docker/production/docker-compose.yml ps

# Test agent qua Nginx
curl http://localhost/health

# Dừng toàn bộ
docker compose -f 02-docker/production/docker-compose.yml down
```

### So sánh image size:

```bash
# Basic vs Advanced
docker images | grep agent
# agent-basic    ~  800 MB  ← python:3.11 base
# agent-advanced ~  160 MB  ← python:3.11-slim + multi-stage
```

---

## Lý thuyết: Tại Sao Multi-Stage?

```dockerfile
# Stage 1: Builder — có đầy đủ tools để compile deps
FROM python:3.11 AS builder   # 1 GB
RUN pip install ...            # thêm deps vào layer này

# Stage 2: Runtime — chỉ copy những gì cần chạy
FROM python:3.11-slim          # 150 MB ← bắt đầu từ image sạch
COPY --from=builder ...        # copy chỉ /site-packages
```

**Kết quả:** Final image chỉ có runtime, không có pip, không có build tools → nhỏ và an toàn hơn.

---

## Câu hỏi thảo luận

1. Tại sao `COPY requirements.txt .` rồi `RUN pip install` TRƯỚC khi `COPY . .`?
2. `.dockerignore` nên chứa những gì? Tại sao `venv/` và `.env` quan trọng?
3. Nếu agent cần đọc file từ disk, làm sao mount volume vào container?
