# ⚙️ Build & Run (Backend only)

### 1️⃣ Build imaginea Docker ###

Execută din rădăcina proiectului:
    docker build -t realtime-chat-backend -f Dockerfile_backend 
Ruleaza containerul:
    docker run --name realtime-chat-backend -p 8000:8000 realtime-chat-backend

Acceseaza endpointul http://localhost:8000/healthz

---

# ⚙️ Build & Run (Backend & Frontend with Docker Compose)

## 1 Build & Run All Services

From the project root, run:

    docker-compose up --build

This will build and start:
- Backend (FastAPI, port 8000)
- Frontend (Vite, port 5173)
- PostgreSQL (port 5432)

## 2 Access the Apps

- Backend: http://localhost:8000/healthz
- Frontend: http://localhost:5173/

---
# RealTime-Chat
