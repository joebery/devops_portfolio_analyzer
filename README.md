# DevOps Portfolio Analyzer

![Python](https://img.shields.io/badge/language-Python-blue.svg) ![License](https://img.shields.io/badge/license-MIT-green.svg) ![Docker](https://img.shields.io/badge/docker-enabled-blue.svg)

A cloud-native SaaS tool that analyzes GitHub repositories and uses AI to generate DevOps maturity scores, project summaries, and CV-ready bullet points.

---

## 🚀 What This Project Does

The DevOps Portfolio Analyzer allows users to paste a public GitHub URL, which the app then analyzes by fetching repository metadata via the GitHub API, scanning the repo structure for DevOps signals, sending findings to an AI model, and returning:
- A plain English project summary
- A DevOps maturity score
- README improvement suggestions
- CV-ready bullet points

Built to demonstrate real-world cloud engineering patterns — not a tutorial app.

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Frontend | Next.js |
| Backend | Python / FastAPI |
| Database | PostgreSQL |
| Queue | AWS SQS |
| Storage | AWS S3 |
| AI | OpenAI API |
| Infrastructure | AWS (ECS Fargate, RDS, S3, SQS, ECR) |
| Containers | Docker / Docker Compose |
| CI/CD | GitHub Actions |

---

## ✨ Features

- 🚀 Quick GitHub repository analysis
- 📊 AI-generated project summaries
- 🔍 DevOps maturity scoring
- 💡 README improvement suggestions

---

## 🏁 Getting Started

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

---

## 🔄 What Changed In This Update

Recent updates include enhanced integration with OpenAI, which now generates project summaries and DevOps maturity scores from the analyzed repository metadata. The README has been improved for clarity and completeness, ensuring that new features are well-documented.

---

## 🏗️ Architecture Overview

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

## 🤝 Contributing

Contributions are welcome! Please feel free to open issues or submit pull requests.

---

## 📝 License

This project is licensed under the MIT License.