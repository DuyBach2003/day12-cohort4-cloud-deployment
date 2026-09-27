# ==========================================
# SINGLE STAGE: Build & Run in One Image
# ==========================================
# Everything happens in one image — simple, but the final image is LARGE
# because the entire Go toolchain (~800MB+) stays in the image.
#
# COPY . . gom tất cả vào một layer: sửa bất kỳ file nào cũng làm
# go build chạy lại. Xem Dockerfile.deps-first và Dockerfile.source-first
# để so sánh thứ tự layers tối ưu vs không tối ưu.
FROM golang:1.22

WORKDIR /app

# Copy the rest of the source code
COPY . .

# Compile the application into a single binary named "myapp"
RUN CGO_ENABLED=0 go build -o myapp .

# Expose port and define the command to run the app
EXPOSE 8080
CMD ["./myapp"]