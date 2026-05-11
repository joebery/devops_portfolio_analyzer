from pydantic import BaseModel, field_validator
import re

class RepoSubmit(BaseModel):
    github_url: str

    @field_validator("github_url")
    @classmethod
    def validate_github_url(cls, v):
        pattern = r"^https://github\.com/[\w\-]+/[\w\-\.]+$"
        if not re.match(pattern, v):
            raise ValueError("Must be a valid GitHub URL e.g. https://github.com/owner/repo")
        return v

class RepoResponse(BaseModel):
    job_id: str
    github_url: str
    status: str

    class Config:
        from_attributes = True