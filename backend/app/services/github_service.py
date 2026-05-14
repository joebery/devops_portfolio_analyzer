import httpx
import os
import base64

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


async def get_existing_readme(owner: str, repo: str) -> str:
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{BASE_URL}/repos/{owner}/{repo}/contents/README.md",
            headers=HEADERS
        )
        if response.status_code == 404:
            return "No existing README found."
        response.raise_for_status()
        data = response.json()
        content = base64.b64decode(data["content"]).decode("utf-8")
        return content


async def get_recent_commits(owner: str, repo: str, count: int = 5) -> list:
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{BASE_URL}/repos/{owner}/{repo}/commits?per_page={count}",
            headers=HEADERS
        )
        response.raise_for_status()
        commits = response.json()

        return [
            {
                "message": c["commit"]["message"],
                "date": c["commit"]["author"]["date"],
                "author": c["commit"]["author"]["name"]
            }
            for c in commits
        ]


async def push_readme_to_github(owner: str, repo: str, content: str, branch: str = "main") -> dict:
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{BASE_URL}/repos/{owner}/{repo}/contents/README.md",
            headers=HEADERS
        )

        if response.status_code == 404:
            sha = None
        else:
            sha = response.json().get("sha")

        encoded_content = base64.b64encode(content.encode("utf-8")).decode("utf-8")

        payload = {
            "message": "docs: auto-generate README via DevOps Portfolio Analyzer",
            "content": encoded_content,
            "branch": branch
        }

        if sha:
            payload["sha"] = sha

        push_response = await client.put(
            f"{BASE_URL}/repos/{owner}/{repo}/contents/README.md",
            headers=HEADERS,
            json=payload
        )
        push_response.raise_for_status()

        return {
            "commit_url": push_response.json()["commit"]["html_url"],
            "message": "README pushed to GitHub successfully"
        }


async def get_key_files(owner: str, repo: str, branch: str = "main") -> dict:
    async with httpx.AsyncClient() as client:
        tree_response = await client.get(
            f"{BASE_URL}/repos/{owner}/{repo}/git/trees/{branch}?recursive=1",
            headers=HEADERS
        )
        tree_response.raise_for_status()
        tree = tree_response.json().get("tree", [])
        paths = [item["path"] for item in tree if item["type"] == "blob"]

        selected = []

        priority_files = [
            "requirements.txt", "package.json", "Dockerfile",
            "docker-compose.yml", "docker-compose.yaml", "Makefile"
        ]
        for f in priority_files:
            if f in paths:
                selected.append(f)

        workflows = [p for p in paths if p.startswith(".github/workflows")]
        selected.extend(workflows)

        entry_points = [
            p for p in paths
            if "/" not in p and (p.endswith(".py") or p.endswith(".ts") or p.endswith(".js"))
        ]
        selected.extend(entry_points[:3])

        file_contents = {}
        for path in selected:
            try:
                response = await client.get(
                    f"{BASE_URL}/repos/{owner}/{repo}/contents/{path}",
                    headers=HEADERS
                )
                if response.status_code == 200:
                    data = response.json()
                    if isinstance(data, dict) and data.get("content"):
                        content = base64.b64decode(data["content"]).decode("utf-8", errors="ignore")
                        file_contents[path] = content[:3000]
            except Exception:
                continue

        return file_contents


async def get_changed_files_from_last_commit(owner: str, repo: str) -> dict:
    async with httpx.AsyncClient() as client:
        commits_response = await client.get(
            f"{BASE_URL}/repos/{owner}/{repo}/commits?per_page=1",
            headers=HEADERS
        )
        commits_response.raise_for_status()
        commits = commits_response.json()

        if not commits:
            return {}

        latest_sha = commits[0]["sha"]

        commit_response = await client.get(
            f"{BASE_URL}/repos/{owner}/{repo}/commits/{latest_sha}",
            headers=HEADERS
        )
        commit_response.raise_for_status()
        commit_data = commit_response.json()

        changed_files = commit_data.get("files", [])
        file_contents = {}

        for file in changed_files:
            filename = file.get("filename", "")
            status = file.get("status", "")

            if status == "removed":
                continue
            if not any(filename.endswith(ext) for ext in [
                ".py", ".ts", ".js", ".yml", ".yaml", ".txt", ".md", ".json", ".tf"
            ]):
                continue

            try:
                response = await client.get(
                    f"{BASE_URL}/repos/{owner}/{repo}/contents/{filename}",
                    headers=HEADERS
                )
                if response.status_code == 200:
                    data = response.json()
                    if isinstance(data, dict) and data.get("content"):
                        content = base64.b64decode(data["content"]).decode("utf-8", errors="ignore")
                        file_contents[filename] = content[:2000]
            except Exception:
                continue

        return file_contents