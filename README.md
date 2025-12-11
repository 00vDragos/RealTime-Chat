# Real-Time Chat

## 🔑 Environment Setup

This project uses two separate environment files:

- Backend: create a `.env` at the repo root (used by FastAPI/Pydantic).
- Frontend: create a `frontend/.env` for Vite (only `VITE_*` vars are exposed).

Create both files manually and fill in values:

```powershell
# Backend
New-Item -ItemType File .env -Force

# Frontend
New-Item -ItemType File frontend/.env -Force
```

Backend `.env` example content:

```
POSTGRES_USER=<POSTGRES_USER>
POSTGRES_PASSWORD=<POSTGRES_PASSWORD>
POSTGRES_DB=<POSTGRES_DB>
POSTGRES_HOST=<DB_HOST>
POSTGRES_PORT=<DB_PORT>


DATABASE_URL=postgresql+asyncpg://<POSTGRES_USER>:<POSTGRES_PASSWORD>@<DB_HOST>:<DB_PORT>/<POSTGRES_DB>
```

Frontend `frontend/.env` example content:

```
VITE_GOOGLE_CLIENT_ID=<GOOGLE_OAUTH_WEB_CLIENT_ID>
VITE_API_URL=<BACKEND_BASE_URL>
VITE_GOOGLE_REDIRECT_URI=<BACKEND_GOOGLE_CALLBACK_URL>
```

Notes for authentication:
- Email/password login calls `POST /auth/login` and expects an existing user (register via `/auth/register` or seed data).
- Google login exchanges the auth code against `POST /auth/google/callback`. The value of `VITE_GOOGLE_REDIRECT_URI` must match both your backend `GOOGLE_REDIRECT_URI` and the OAuth client's authorized redirect URIs in Google Cloud Console.

Notes:
- Keep secrets out of Git. `.env` files are already gitignored.
- Ensure `VITE_API_URL` points to your backend base URL.
- The Google client ID must be the OAuth Web client ID.

## ⚙️ Build & Run (Backend only)

### 1️⃣ Build image

From the project root:

```powershell
docker build -t realtime-chat-backend -f Dockerfile_backend .
```

### 2️⃣ Run the container

```powershell
docker run --name realtime-chat-backend -p 8000:8000 realtime-chat-backend
```

Access the health endpoint at `http://localhost:8000/healthz`.

## Formatting & Linting

This project uses Black for formatting and Ruff for linting. A `pre-commit` hook runs both locally and the project has a CI workflow to validate PRs.

Setup (local):

```powershell
# Activate your virtualenv
.\.venv\\Scripts\\Activate.ps1

# Install Git hooks
pre-commit install

# Install pre-commit hooks
pre-commit install --install-hooks

# Run hooks once on every file
pre-commit run --all-files
```

CI: A GitHub Actions workflow runs `pre-commit` for every push and pull request. See `.github/workflows/pre-commit.yml`.

If you prefer to run tools manually:

```powershell
ruff check .
black .
```
