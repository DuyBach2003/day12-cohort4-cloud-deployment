# Multi-Stage Docker Build Demo

So sánh **single-stage** vs **multi-stage** build bằng một Go web server đơn giản.

## Cấu trúc

```
multi-stages/
├── main.go                  # Go HTTP server (port 8080)
├── go.mod                   # Go module
├── Dockerfile               # Single-stage — image lớn (~800 MB)
└── Dockerfile-multistage    # Multi-stage — image nhỏ (~15 MB)
```

## Chạy thử

### Single-stage build

```bash
docker build -f Dockerfile -t myapp-single .

# Kiểm tra size
docker images myapp-single
docker run -p 8080:8080 myapp-single
curl http://localhost:8080/
```

### Multi-stage build

```bash
docker build -f Dockerfile-multistage -t myapp-multi .

# Kiểm tra size
docker images myapp-multi

docker run -p 8080:8080 myapp-multi
curl http://localhost:8080/
```

## So sánh kết quả


| | Single-stage | Multi-stage |
|---|---|---|
| Base image | `golang:1.22` (~800 MB) | `alpine:3.19` (~7 MB) |
| Chứa Go compiler | Co | Khong |
| Final size | ~800 MB | ~15 MB |
| Security | Attack surface lon | Chi co binary, an toan hon |
| Non-root user | Khong | Co (`appuser`) |

## Tai sao Multi-Stage?

1. **Image nho hon** — chi copy binary da compile, bo het build tools
2. **An toan hon** — final image khong co compiler, package manager, source code
3. **Non-root user** — `Dockerfile-multistage` tao user `appuser` de chay app, khong dung root
4. **Deploy nhanh hon** — image nho = push/pull nhanh hon, tiet kiem bandwidth

## Cach hoat dong

```
Stage 1 (builder)              Stage 2 (production)
┌─────────────────────┐        ┌─────────────────────┐
│ golang:1.22         │        │ alpine:3.19         │
│                     │        │                     │
│ COPY source code    │        │ adduser appuser     │
│ go build -o myapp   │───────>│ COPY --from=builder │
│                     │  only  │      /app/myapp     │
│ ~800 MB             │ binary │ ~15 MB              │
└─────────────────────┘        └─────────────────────┘
      (bi loai bo)                (final image)
```
