# Dockerfile Examples — Thứ Tự Layers (Go)

Ứng dụng Go đơn giản (HTTP server) dùng để minh họa ảnh hưởng của thứ tự layers trong Dockerfile lên Docker build cache.

```text
Dockerfile_examples/
├── Dockerfile               # Single-stage, COPY . . (chưa tối ưu)
├── Dockerfile.deps-first    # Dependencies trước, source sau (tối ưu)
├── Dockerfile.source-first  # Source trước, dependencies sau (không tối ưu)
├── go.mod
├── main.go
└── README.md
```

---

## 1. Build ba image

Cần Docker đang chạy. Từ thư mục `Dockerfile_examples/`:

```bash
cd Dockerfile_examples

# Image gốc: COPY . . gom tất cả vào một bước
docker build --progress=plain -t myapp:single .

# Tối ưu: dependencies trước, source sau
docker build --progress=plain -f Dockerfile.deps-first -t myapp:deps-first .

# Không tối ưu: source trước, dependencies sau
docker build --progress=plain -f Dockerfile.source-first -t myapp:source-first .

docker image ls myapp
```

## 2. Chạy và test

```bash
docker run --rm -d --name myapp-test -p 127.0.0.1:8080:8080 myapp:deps-first

curl http://localhost:8080/

docker stop myapp-test
```

## 3. Quan sát ảnh hưởng của thứ tự layers

### So sánh ba Dockerfile

```text
Dockerfile              Dockerfile.deps-first        Dockerfile.source-first
──────────────────      ──────────────────────       ────────────────────────
COPY . .                COPY go.mod .                COPY go.mod .
RUN go build            RUN go mod download          COPY main.go .
                        COPY main.go .               RUN go mod download
                        RUN go build                 RUN go build
```

### Thực hành

Build cả ba image thành công, sau đó build lại để thấy tất cả các bước hiện `CACHED`.

Tiếp theo, sửa `main.go` (ví dụ thêm một dòng comment) rồi build lại:

```bash
# Thêm comment vào main.go
echo '// test layer cache' >> main.go

# Build lại cả ba
docker build --progress=plain -f Dockerfile.deps-first -t myapp:deps-first .
docker build --progress=plain -f Dockerfile.source-first -t myapp:source-first .
docker build --progress=plain -t myapp:single .

# Hoàn tác
git checkout main.go
```

### Kết quả khi sửa `main.go`

| Bước | `Dockerfile` | `deps-first` | `source-first` |
|------|:---:|:---:|:---:|
| COPY go.mod | — | CACHED | CACHED |
| go mod download | — | CACHED | chạy lại |
| COPY main.go | — | chạy lại | chạy lại |
| COPY . . | chạy lại | — | — |
| go build | chạy lại | chạy lại | chạy lại |

- **`deps-first`**: `go mod download` vẫn dùng cache vì `go.mod` không đổi. Chỉ copy source và build lại.
- **`source-first`**: `main.go` nằm **trước** `go mod download`, nên mất cache kéo theo `go mod download` chạy lại.
- **`Dockerfile` (COPY . .)**: mọi thay đổi file đều làm chạy lại từ bước `COPY . .`.

### Tổng hợp các trường hợp

| Thay đổi trước lần build tiếp theo | `deps-first` | `source-first` | `Dockerfile` |
|---|---|---|---|
| Không sửa file nào | Dùng cache | Dùng cache | Dùng cache |
| Sửa `main.go` | `go mod download` dùng cache | `go mod download` chạy lại | `go build` chạy lại |
| Sửa `go.mod` | `go mod download` chạy lại | `go mod download` chạy lại | `go build` chạy lại |

## 4. Xem lịch sử image

```bash
docker history myapp:deps-first
docker history myapp:source-first
docker history myapp:single
```

Lịch sử hiển thị từ bước mới nhất về cũ nhất, bao gồm cả metadata (`CMD`, `EXPOSE`) — không chỉ các layer chứa dữ liệu filesystem.

## 5. Nguyên tắc chung

1. **Ít thay đổi → đặt trước**: file khai báo dependencies (`go.mod`, `requirements.txt`, `package.json`) thay đổi ít hơn source code.
2. **Tốn thời gian → tách riêng**: bước cài dependencies (`go mod download`, `pip install`, `npm install`) nên nằm ngay sau COPY file khai báo, trước khi copy source.
3. **Hay thay đổi → đặt sau**: source code thay đổi thường xuyên nhất, đặt cuối cùng trước bước build.
4. **Tránh `COPY . .` sớm**: gom tất cả vào một bước khiến mọi thay đổi đều phá cache các bước phía sau.

---

Xem thêm: [demo Python với FastAPI](../02-docker/layer-order/README.md) để so sánh cùng nguyên tắc với `requirements.txt` + `pip install`.

Tham khảo: [Docker — tối ưu thứ tự layers](https://docs.docker.com/build/cache/optimize/), [cache invalidation](https://docs.docker.com/build/cache/invalidation/).
