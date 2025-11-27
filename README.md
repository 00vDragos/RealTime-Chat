# Real-Time Chat

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

# Install dev tools
pip install pre-commit black ruff

# Install Git hooks
pre-commit install

# Run hooks once on every file
pre-commit run --all-files
```

CI: A GitHub Actions workflow runs `pre-commit` for every push and pull request. See `.github/workflows/pre-commit.yml`.

If you prefer to run tools manually:

```powershell
ruff check .
black .
```
