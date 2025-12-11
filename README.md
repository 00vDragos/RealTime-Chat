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
DEBUG=0
ALLOWED_ORIGINS=http://localhost:5173
JWT_SECRET=<your_jwt_secret>
JWT_ALG=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
GOOGLE_CLIENT_ID=<google_client_id>
GOOGLE_CLIENT_SECRET=<google_client_secret>
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

## 🌟 Features
- Auth: Email/password (+ Google OAuth), JWT, refresh/logout
- Friends: requests, accept/decline/cancel, list/remove
- Conversations: direct and group, idempotent creation
- Messages: send/list/edit/delete, reactions, unread tracking, last message preview
- WebSockets: broadcasts for `conversation_created`, `new_message`, and presence
- Avatars: update via secured user endpoint

## 🚀 Quick Start (Docker)

```powershell
docker compose up --build
```

Apply migrations (first run):

```powershell
docker compose exec backend alembic upgrade head
```

Open:
- Backend docs: `http://localhost:8000/docs`
- Frontend: `http://localhost:5173`

## 🔧 Configuration Notes
- Backend `.env` (root) should include `DATABASE_URL`, `DEBUG`, `ALLOWED_ORIGINS`, JWT settings, and Google OAuth creds.
- Frontend `frontend/.env` should include `VITE_API_URL`, `VITE_GOOGLE_CLIENT_ID`, `VITE_GOOGLE_REDIRECT_URI`.
- Ensure Google redirect URI matches the backend callback and is authorized in Google Cloud Console.

## 📚 API Overview

Auth (prefix `/api`):
- `POST /api/auth/register`
- `POST /api/auth/login`
- `GET /api/auth/me`
- `POST /api/auth/refresh`
- `POST /api/auth/logout`
- `GET|POST /api/auth/google/callback` (compat aliases also under `/auth/...`)

Friends:
- `POST /friends/requests`
- `GET /friends/requests?direction=in|out`
- `POST /friends/requests/{id}/respond` (accept/decline) [alias also under `/api/friends/...`]
- `DELETE /friends/requests/{id}`
- `GET /friends`
- `POST /friends/remove` (by `friend_email`)

Messages:
- `POST /api/messages/new_conversation` `{ participant_ids: UUID[] }`
- `GET /api/messages/conversations`
- `POST /api/messages/conversations/{conversation_id}/messages?body=...`
- Additional: reactions, edit/delete, last-read updates

Users:
- `PATCH /api/users/me/avatar` `{ avatar_url }`

WebSocket:
- `GET /ws` (broadcast events)

## ✅ Testing

Unit tests:

```powershell
pytest -q
```

Integration tests (backend must be running at `http://localhost:8000`):

```powershell
pytest -q tests/backend/IntegrationTests
```

Notes:
- Integration tests skip gracefully if backend returns errors during conversation creation or message sends.
- Unit tests set `DEBUG=0` and override DB session to create tables on the app engine for isolation.

## 🛠️ Troubleshooting
- 404 Google callback: use `/api/auth/google/callback` or `/auth/google/callback` (compat alias).
- Method Not Allowed for friend respond: use `POST /friends/requests/{id}/respond` or the `/api/friends/...` alias.
- "Internal Server Error" on `new_conversation`: apply migrations and verify participant IDs exclude the creator; check server logs.
