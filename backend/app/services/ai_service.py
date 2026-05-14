import os
from openai import AsyncOpenAI
import json
import re

client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def extract_images(readme_content: str) -> list:
    markdown_images = re.findall(r'!\[([^\]]*)\]\(([^)]+)\)', readme_content)
    html_images = re.findall(r'<img[^>]+src=["\']([^"\']+)["\'][^>]*>', readme_content)

    images = []
    for alt, url in markdown_images:
        images.append(f"![{alt}]({url})")
    for url in html_images:
        images.append(f'<img src="{url}">')

    return images

def build_image_block(extracted_images: list) -> str:
    if extracted_images:
        return f"""
CRITICAL — The existing README contains these images. You MUST include ALL of them in the new README.
Do not remove, modify, or skip any of these under any circumstances:

{chr(10).join(extracted_images)}

Place them in the most logical position in the new README.
"""
    return "The existing README contains no images."

def safety_net_images(result: dict, extracted_images: list) -> dict:
    if not extracted_images:
        return result

    generated = result.get("generated_readme", "")
    missing = []
    for img in extracted_images:
        url_match = re.search(r'https?://[^\s\)>"]+', img)
        if url_match:
            url = url_match.group(0)
            if url not in generated:
                missing.append(img)

    if missing:
        generated += "\n\n## Screenshots\n\n"
        generated += "\n\n".join(missing)
        result["generated_readme"] = generated

    return result


async def initial_analyse_repo(
    repo_data: dict,
    existing_readme: str,
    recent_commits: list,
    key_files: dict
) -> dict:

    extracted_images = extract_images(existing_readme)
    images_block = build_image_block(extracted_images)

    files_block = ""
    if key_files:
        files_block = "Here are the key files from the repository:\n\n"
        for path, content in key_files.items():
            files_block += f"--- {path} ---\n{content}\n\n"

    prompt = f"""
You are a senior software engineer and DevOps expert doing a FULL analysis of a GitHub repository.
This is an initial README generation — read everything carefully and produce the most accurate,
detailed README possible.

Repository metadata:
{json.dumps(repo_data, indent=2)}

Recent commits:
{json.dumps(recent_commits, indent=2)}

{files_block}

Existing README (previous version):
{existing_readme}

{images_block}

Return a JSON object with exactly these fields:

{{
  "project_summary": "A 2-3 sentence plain English summary of what this project is and what it does.",
  "devops_maturity_score": <integer 0-100>,
  "devops_maturity_notes": "2-3 sentences explaining the score.",
  "generated_readme": "A full professional README.md in GitHub-flavoured markdown."
}}

Scoring guide:
- Has Dockerfile: +20
- Has docker-compose: +10
- Has GitHub Actions: +25
- Has Terraform: +20
- Has Kubernetes: +15
- Has README: +10

For generated_readme:
- Large project title and one-line description
- Shields.io badges for language, license, Docker
- What This Project Does section
- Tech Stack table built from the actual files you read
- Features section with emoji bullets — based on actual code, not guesses
- Getting Started with real prerequisites and commands
- What Changed In This Update section from recent commits
- Architecture section with ASCII diagram
- Screenshots section if images present
- Contributing and License section
- Emojis on all section headers
- ALL extracted images must appear — non negotiable
- Base everything on the actual file contents provided, not assumptions

Return only valid JSON. No markdown, no explanation.
"""

    response = await client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"},
        temperature=0.7
    )

    result = json.loads(response.choices[0].message.content)
    result = safety_net_images(result, extracted_images)
    return result


async def update_analyse_repo(
    repo_data: dict,
    existing_readme: str,
    recent_commits: list,
    changed_files: dict
) -> dict:

    extracted_images = extract_images(existing_readme)
    images_block = build_image_block(extracted_images)

    changed_block = ""
    if changed_files:
        changed_block = "Here are the files that changed in the last commit:\n\n"
        for path, content in changed_files.items():
            changed_block += f"--- {path} ---\n{content}\n\n"
    else:
        changed_block = "No significant file changes detected in the last commit."

    prompt = f"""
You are a senior software engineer updating an existing README based on recent changes to a repository.
The README is already accurate — make only the changes necessary to reflect what changed.
Do not rewrite sections that are still correct.

Repository metadata:
{json.dumps(repo_data, indent=2)}

Recent commits:
{json.dumps(recent_commits, indent=2)}

{changed_block}

Current README (update this — do not start from scratch):
{existing_readme}

{images_block}

Return a JSON object with exactly these fields:

{{
  "project_summary": "Updated 2-3 sentence summary if anything changed, otherwise keep existing.",
  "devops_maturity_score": <integer 0-100>,
  "devops_maturity_notes": "Updated notes if anything changed, otherwise keep existing.",
  "generated_readme": "The updated README.md in GitHub-flavoured markdown."
}}

Scoring guide:
- Has Dockerfile: +20
- Has docker-compose: +10
- Has GitHub Actions: +25
- Has Terraform: +20
- Has Kubernetes: +15
- Has README: +10

For generated_readme:
- Keep all existing sections that are still accurate
- Update only what has changed based on the commit and file diffs
- Update the What Changed In This Update section with the latest commits
- Keep all existing images — ALL of them — non negotiable
- Do not remove any section that was already there

Return only valid JSON. No markdown, no explanation.
"""

    response = await client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"},
        temperature=0.7
    )

    result = json.loads(response.choices[0].message.content)
    result = safety_net_images(result, extracted_images)
    return result