from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db import get_db
from app.models import Repository
from app.schemas import RepoSubmit, RepoResponse
from app.services.github_service import get_repo_metadata, scan_repo_structure, get_existing_readme, get_recent_commits
from app.services.ai_service import analyse_repo

router = APIRouter(prefix="/api/v1/repos", tags=["repos"])

@router.post("/", response_model=RepoResponse)
def submit_repo(payload: RepoSubmit, db: Session = Depends(get_db)):
    parts = payload.github_url.rstrip("/").split("/")
    owner = parts[-2]
    repo_name = parts[-1]

    repo = Repository(
        github_url=payload.github_url,
        owner=owner,
        repo_name=repo_name,
        status="pending"
    )
    db.add(repo)
    db.commit()
    db.refresh(repo)

    return RepoResponse(
        job_id=str(repo.id),
        github_url=repo.github_url,
        status=repo.status
    )

@router.get("/test-github/{owner}/{repo}")
async def test_github(owner: str, repo: str):
    metadata = await get_repo_metadata(owner, repo)
    structure = await scan_repo_structure(owner, repo, metadata["default_branch"])
    return {**metadata, **structure}

@router.get("/test-ai/{owner}/{repo}")
async def test_ai(owner: str, repo: str):
    metadata = await get_repo_metadata(owner, repo)
    structure = await scan_repo_structure(owner, repo, metadata["default_branch"])
    existing_readme = await get_existing_readme(owner, repo)
    recent_commits = await get_recent_commits(owner, repo)
    combined = {**metadata, **structure, "owner": owner, "repo": repo}
    result = await analyse_repo(combined, existing_readme, recent_commits)
    return result