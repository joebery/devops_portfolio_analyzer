import httpx
import os

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

HEADERS = {
    "Authorization": f"Bearer {GITHUB_TOKEN}",
    "Accept": "application/vnd.github+json"
}

BASE_URL = "https://api.github.com"

async def get_repo_metadata(owner: str, repo: str) -> dict:
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{BASE_URL}/repos/{owner}/{repo}",
            headers=HEADERS
        )
        response.raise_for_status()
        data = response.json()

        return {
            "stars": data.get("stargazers_count", 0),
            "forks": data.get("forks_count", 0),
            "primary_language": data.get("language"),
            "description": data.get("description"),
            "topics": data.get("topics", []),
            "license": data.get("license", {}).get("name") if data.get("license") else None,
            "default_branch": data.get("default_branch", "main")
        }

async def scan_repo_structure(owner: str, repo: str, branch: str = "main") -> dict:
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{BASE_URL}/repos/{owner}/{repo}/git/trees/{branch}?recursive=1",
            headers=HEADERS
        )
        response.raise_for_status()
        tree = response.json().get("tree", [])

        paths = [item["path"] for item in tree]

        return {
            "has_readme": any("readme" in p.lower() for p in paths),
            "has_dockerfile": any("dockerfile" in p.lower() for p in paths),
            "has_compose": any("docker-compose" in p.lower() for p in paths),
            "has_terraform": any(p.endswith(".tf") for p in paths),
            "has_github_actions": any(p.startswith(".github/workflows") for p in paths),
            "has_kubernetes": any(
                "k8s" in p.lower() or
                "kubernetes" in p.lower() or
                p.endswith(".yaml") and "manifest" in p.lower()
                for p in paths
            ),
            "workflow_count": sum(1 for p in paths if p.startswith(".github/workflows") and p.endswith(".yml"))
        }