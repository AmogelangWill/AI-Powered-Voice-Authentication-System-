# Voiceprint Authentication System

Production-oriented voiceprint authentication system with a FastAPI backend and React frontend.

## Features

- Voice-based registration and login
- Audio preprocessing (normalization, noise reduction, resampling)
- Feature extraction (MFCC, mel-spectrogram, ZCR, spectral features)
- Per-user Gaussian Mixture Model (GMM) voice model persistence
- JWT access and refresh token flow
- Rate-limited login endpoint
- Dockerized local development with PostgreSQL

## Project Structure

- `backend/`: FastAPI app, services, database models, tests
- `frontend/`: React 18 + Vite UI for registration/login and recording
- `.github/workflows/`: CI and deploy workflows

## Quick Start

### Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt -r requirements-dev.txt
uvicorn app.main:app --reload --port 8000
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

### Docker Compose

```bash
docker compose up --build
```

## Security Notes

- Raw audio is never persisted in database storage.
- Username values are stored hashed with bcrypt.
- JWT secret is environment-driven and never hardcoded.

## API Endpoints

- `POST /api/v1/auth/register`
- `POST /api/v1/auth/login`
- `POST /api/v1/auth/refresh`
- `GET /api/v1/auth/verify`
- `GET /api/v1/health`
