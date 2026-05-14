from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db import get_db
from app.models import Repository
from app.schemas import RepoSubmit, RepoResponse
from app.services.github_service import get_repo_metadata, scan_repo_structure

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


from app.services.ai_service import analyse_repo

@router.get("/test-ai/{owner}/{repo}")
async def test_ai(owner: str, repo: str):
    metadata = await get_repo_metadata(owner, repo)
    structure = await scan_repo_structure(owner, repo, metadata["default_branch"])
    combined = {**metadata, **structure, "owner": owner, "repo": repo}
    result = await analyse_repo(combined)
    return result