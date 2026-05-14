# DevOps Portfolio Analyzer

A cloud-native SaaS application that analyses public GitHub repositories and uses AI to generate professional project summaries, DevOps maturity scores, README improvement suggestions, and CV-ready bullet points.

> 🚧 **Active development — Day 1 complete**

---

## What This Project Is

Paste a public GitHub URL. The app:

1. Fetches repository metadata via the GitHub API
2. Scans the repo structure for DevOps signals — Dockerfiles, Terraform, GitHub Actions workflows, Kubernetes manifests, and more
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

### ✅ Day 1 — Local Foundation Complete

| # | Milestone | Status |
|---|---|---|
| 1 | Project structure and folder naming conventions | ✅ |
| 2 | FastAPI backend running inside Docker | ✅ |
| 3 | Docker Compose local development environment | ✅ |
| 4 | Root and health check endpoints responding | ✅ |
| 5 | Auto-generated API docs at `/docs` | ✅ |
| 6 | PostgreSQL database connected via Docker Compose | ✅ |
| 7 | `repositories` table created with UUID primary key | ✅ |
| 8 | `POST /api/v1/repos` endpoint accepting and validating GitHub URLs | ✅ |
| 9 | Submitted URLs saving to PostgreSQL with status tracking | ✅ |
| 10 | GitHub service fetching live repo metadata | ✅ |
| 11 | Repository file structure scanner detecting DevOps signals | ✅ |
| 12 | `.gitignore` and `.env` protection configured | ✅ |

### 🔲 Day 2 — Up Next

- [ ] OpenAI integration — generate AI analysis from repo metadata
- [ ] Async worker pattern — decouple analysis from API response
- [ ] AWS SQS queue setup with LocalStack
- [ ] `GET /api/v1/analyses/{job_id}` endpoint
- [ ] Next.js frontend — submit form and results dashboard
- [ ] AWS deployment via Terraform
- [ ] GitHub Actions CI/CD pipeline

---

## Project Structure

```
devops_portfolio_analyzer/
├── .env                          # Local secrets — never committed
├── .gitignore
├── docker-compose.yml
├── README.md
└── backend/
    ├── app/
    │   ├── main.py               # FastAPI entry point
    │   ├── db.py                 # Database engine and session
    │   ├── models.py             # SQLAlchemy ORM models
    │   ├── schemas.py            # Pydantic request/response schemas
    │   ├── routers/
    │   │   └── repos.py          # /api/v1/repos endpoints
    │   └── services/
    │       └── github_service.py # GitHub API integration
    ├── Dockerfile
    └── requirements.txt
```

---

## Running Locally

### Prerequisites

- [Docker Desktop](https://www.docker.com/products/docker-desktop)
- A GitHub Personal Access Token with `public_repo` scope

### Setup

```bash
git clone https://github.com/joebery/devops_portfolio_analyzer.git
cd devops_portfolio_analyzer
```

Create a `.env` file in the root:

```
GITHUB_TOKEN=ghp_yourtoken
DATABASE_URL=postgresql://dev:devpassword@db:5432/portfolio_analyzer
```

Start the stack:

```bash
docker compose up --build
```

### Endpoints

| URL | Method | Description |
|---|---|---|
| `http://localhost:8000` | GET | Root check |
| `http://localhost:8000/health` | GET | Health check — confirms DB connection |
| `http://localhost:8000/docs` | GET | Auto-generated interactive API docs |
| `http://localhost:8000/api/v1/repos` | POST | Submit a GitHub repo URL for analysis |
| `http://localhost:8000/api/v1/repos/test-github/{owner}/{repo}` | GET | Test GitHub API integration directly |

---

## Example API Usage

**Submit a repository:**

```bash
curl -X POST http://localhost:8000/api/v1/repos \
  -H "Content-Type: application/json" \
  -d '{"github_url": "https://github.com/torvalds/linux"}'
```

**Response:**

```json
{
  "job_id": "62b809fd-bffa-41bb-9a57-507747672a08",
  "github_url": "https://github.com/torvalds/linux",
  "status": "pending"
}
```

**Live GitHub scan result:**

```json
{
  "stars": 232799,
  "forks": 62201,
  "primary_language": "C",
  "description": "Linux kernel source tree",
  "has_readme": true,
  "has_dockerfile": false,
  "has_terraform": false,
  "has_github_actions": false,
  "has_kubernetes": false,
  "workflow_count": 0
}
```

---

## Architecture Overview

```
User submits GitHub URL
        ↓
FastAPI validates and saves job (status: pending)
        ↓
Job dropped onto SQS queue
        ↓
Background worker picks up job:
  → Calls GitHub API for metadata
  → Scans repo file tree for DevOps signals
  → Sends structured data to OpenAI
  → Stores AI analysis in PostgreSQL + S3
        ↓
Frontend polls for job completion
        ↓
Results dashboard rendered
```

The API and worker are deliberately decoupled. The API responds instantly with a job ID — the slow work (GitHub + OpenAI calls) happens in the background. This prevents users waiting on a synchronous chain of external API calls.

---

## Architectural Decisions

| Decision | Reason |
|---|---|
| Docker from day one | Consistent environments across local dev and production |
| Async queue pattern | Users never wait on slow external API calls |
| SQS Dead Letter Queue | Failed jobs are preserved and replayable, not silently lost |
| S3 for raw JSON storage | Keeps the database slim — full metadata always retrievable |
| ECS Fargate | No EC2 management, scales to zero when idle |
| UUID primary keys | Avoids sequential ID enumeration — better security posture |
| Pydantic validation | Invalid URLs rejected before they touch the database or queue |

---

## Local Development Notes

- Docker Desktop must be running before `docker compose up --build`
- Hot reload is enabled — code changes reflect inside the container without rebuilding
- The `version` field is omitted from `docker-compose.yml` — it is obsolete in modern Docker
- Never commit the `.env` file — add it manually after cloning

---

## Author

**Joe Bery** — Cybersecurity and Networks graduate transitioning into cloud and software engineering.

Building this project to demonstrate real-world AWS, backend, and DevOps skills through a practical portfolio tool.

[GitHub](https://github.com/joebery)

---

## Licence

MIT
