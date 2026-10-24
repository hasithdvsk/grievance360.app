# 🐳 Container Configurations (`docker/`)

Multi-stage container definitions optimized for minimal image sizes and rapid build times.

---

## 🛠️ Docker Images

- **Dockerfile.api**:
  - Base: `python:3.11-slim`
  - Installs system dependencies for PostgreSQL driver and PDF compilation
  - Launches ASGI server with `uvicorn` on port 8000
- **Dockerfile.web**:
  - Base: `node:20-alpine`
  - 3-stage build: `deps` -> `builder` -> `runner`
  - Runs unprivileged as `nextjs` user on port 3000

---

## 🚀 Building Manually

```bash
# Build API image
docker build -t grievance360-api -f docker/Dockerfile.api .

# Build Web image
docker build -t grievance360-web -f docker/Dockerfile.web .
```
