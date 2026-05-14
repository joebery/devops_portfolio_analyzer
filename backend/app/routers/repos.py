from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db import get_db
from app.models import Repository
from app.schemas import RepoSubmit, RepoResponse
from app.services.github_service import (
    get_repo_metadata,
    scan_repo_structure,
    get_existing_readme,
    get_recent_commits,
    push_readme_to_github,
    get_key_files,
    get_changed_files_from_last_commit
)
from app.services.ai_service import initial_analyse_repo, update_analyse_repo

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


@router.post("/initial-readme/{owner}/{repo}")
async def generate_initial_readme(owner: str, repo: str):
    metadata = await get_repo_metadata(owner, repo)
    structure = await scan_repo_structure(owner, repo, metadata["default_branch"])
    existing_readme = await get_existing_readme(owner, repo)
    recent_commits = await get_recent_commits(owner, repo)
    key_files = await get_key_files(owner, repo, metadata["default_branch"])
    combined = {**metadata, **structure, "owner": owner, "repo": repo}

    result = await initial_analyse_repo(combined, existing_readme, recent_commits, key_files)

    push_result = await push_readme_to_github(
        owner, repo, result.get("generated_readme", ""), metadata["default_branch"]
    )

    return {
        "mode": "initial",
        "message": push_result["message"],
        "commit_url": push_result["commit_url"],
        "maturity_score": result.get("devops_maturity_score"),
        "maturity_notes": result.get("devops_maturity_notes"),
        "files_read": list(key_files.keys())
    }


@router.post("/update-readme/{owner}/{repo}")
async def generate_update_readme(owner: str, repo: str):
    metadata = await get_repo_metadata(owner, repo)
    structure = await scan_repo_structure(owner, repo, metadata["default_branch"])
    existing_readme = await get_existing_readme(owner, repo)
    recent_commits = await get_recent_commits(owner, repo)
    changed_files = await get_changed_files_from_last_commit(owner, repo)
    combined = {**metadata, **structure, "owner": owner, "repo": repo}

    result = await update_analyse_repo(combined, existing_readme, recent_commits, changed_files)

    push_result = await push_readme_to_github(
        owner, repo, result.get("generated_readme", ""), metadata["default_branch"]
    )

    return {
        "mode": "update",
        "message": push_result["message"],
        "commit_url": push_result["commit_url"],
        "maturity_score": result.get("devops_maturity_score"),
        "maturity_notes": result.get("devops_maturity_notes"),
        "files_changed": list(changed_files.keys())
    }