# DevOps Portfolio Analyzer

A cloud-native SaaS application that analyses GitHub repositories and uses AI to generate professional project summaries, DevOps maturity scores, README improvements, and CV-ready bullet points.

>**Currently in active development — this is iteration 1**

---

## What This Project Is

You paste a public GitHub URL. The app:

1. Fetches the repository metadata via the GitHub API
2. Scans the repo structure for DevOps signals (Dockerfile, Terraform, GitHub Actions, Kubernetes manifests, etc.)
3. Sends the findings to an AI model
4. Returns:
   - A plain English project summary
   - A DevOps maturity score
   - README improvement suggestions
   - CV-ready bullet points

Built to demonstrate real-world cloud engineering patterns — not a tutorial app.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | Next.js |
| Backend | Python / FastAPI |
| Database | PostgreSQL |
| Queue | AWS SQS |
| Storage | AWS S3 |
| AI | OpenAI API |
| Infrastructure | AWS (ECS Fargate, RDS, S3, SQS, ECR) |
| IaC | Terraform |
| Containers | Docker / Docker Compose |
| CI/CD | GitHub Actions |

---

## Current Status

### ✅ Iteration 1 — Local Foundation
- [x] Project structure created
- [x] FastAPI backend running inside Docker
- [x] Docker Compose local development environment
- [x] `/` and `/health` endpoints responding
- [x] Auto-generated API docs at `/docs`
- [x] PostgreSQL database connected
- [x] `repositories` table created
- [x] `POST /api/v1/repos` endpoint accepting GitHub URLs
- [x] URL validation
- [x] Rows saving to PostgreSQL with UUID and status
- [x] GitHub service fetching live repo metadata
- [x] Repository file structure scanner
- [x] `.gitignore` and `.env` protection set up

### 🔲 Up Next
- [ ] PostgreSQL database + Alembic migrations
- [ ] `POST /api/v1/repos` endpoint
- [ ] GitHub API integration
- [ ] Repository file structure scanner
- [ ] AWS SQS queue + async worker
- [ ] OpenAI integration
- [ ] Next.js frontend
- [ ] AWS deployment via Terraform
- [ ] GitHub Actions CI/CD pipeline

---

## Project Structure

```
devops_portfolio_analyzer/
├── backend/
│   ├── app/
│   │   └── main.py          # FastAPI entry point
│   ├── Dockerfile
│   └── requirements.txt
└── docker-compose.yml
```

---

## Running Locally

### Prerequisites

- [Docker Desktop](https://www.docker.com/products/docker-desktop)

### Start the backend

```bash
git clone https://github.com/YOUR_USERNAME/devops_portfolio_analyzer.git
cd devops_portfolio_analyzer
docker compose up --build
```

### Endpoints

| URL | Description |
|---|---|
| `http://localhost:8000` | Root — returns `{"message": "hello"}` |
| `http://localhost:8000/health` | Health check |
| `http://localhost:8000/docs` | Auto-generated API docs |

---

## Architecture Overview

```
User submits GitHub URL
        ↓
FastAPI backend receives request
        ↓
Job dropped onto SQS queue (async)
        ↓
Background worker picks up job:
  → Calls GitHub API
  → Scans repo file tree
  → Sends metadata to OpenAI
  → Stores results in PostgreSQL + S3
        ↓
Frontend polls for completion
        ↓
Results dashboard rendered
```

The API and worker are deliberately decoupled. The API responds instantly with a job ID. The slow work (GitHub + OpenAI calls) happens in the background. This is the correct pattern for operations that take 10–30 seconds.

---

## Why This Architecture

This project is designed to resemble a junior-to-mid level real-world cloud engineering project, not a tutorial. Key decisions:

- **Docker from day one** — consistent environments across local and production
- **Async queue pattern** — users never wait on a synchronous chain of slow API calls
- **SQS Dead Letter Queue** — failed jobs are preserved and replayable, not silently dropped
- **S3 for raw storage** — keeps the database slim, full metadata always retrievable
- **ECS Fargate** — no EC2 management, scales to zero when idle
- **Secrets Manager** — no credentials ever in environment variables or code
- **OIDC for CI/CD** — no long-lived AWS keys stored in GitHub

---

## Local Development Notes

- Docker Desktop must be running before `docker compose up --build`
- The `version` field has been removed from `docker-compose.yml` (obsolete in modern Docker)
- Hot reload is enabled — code changes reflect without rebuilding the container

---

## Author

JOE BERY

---

## Licence

MIT
