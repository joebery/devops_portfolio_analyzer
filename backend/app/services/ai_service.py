import os
from openai import AsyncOpenAI
import json

client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

async def analyse_repo(repo_data: dict, existing_readme: str, recent_commits: list) -> dict:
    prompt = f"""
You are a senior software engineer and DevOps expert reviewing a GitHub repository.

Here is the repository data:
{json.dumps(repo_data, indent=2)}

Here is the existing README (this is the previous version):
{existing_readme}

Here are the most recent commits (what has changed since the last README update):
{json.dumps(recent_commits, indent=2)}

Analyse this repository and return a JSON object with exactly these fields:

{{
  "project_summary": "A 2-3 sentence plain English summary of what this project is and what it does.",
  "devops_maturity_score": <integer 0-100>,
  "devops_maturity_notes": "2-3 sentences explaining the score. What does the repo do well? What is missing?",
  "cv_bullets": [
    "Built X using Y, achieving Z",
    "Built X using Y, achieving Z",
    "Built X using Y, achieving Z"
  ],
  "generated_readme": "A full professional README.md file in GitHub-flavoured markdown."
}}

Scoring guide for devops_maturity_score:
- Has Dockerfile: +20
- Has docker-compose: +10
- Has GitHub Actions workflows: +25
- Has Terraform: +20
- Has Kubernetes manifests: +15
- Has README: +10

CV bullets must follow this format: "Built X using Y, achieving Z"

For generated_readme, produce a complete README.md that:
- Starts with a large project title and one-line description
- Includes shields.io badges for language, license, Docker if applicable
- Has a What This Project Does section
- Has a Tech Stack table
- Has a Features section with emoji bullet points
- Has a Getting Started section with prerequisites and commands in code blocks
- Has a What Changed In This Update section — summarise the recent commits in plain English, explaining what was added or improved
- Has an Architecture section with ASCII diagram
- Has a Contributing and License section
- Uses emojis for all section headers
- Uses tables where appropriate
- All terminal commands must be in code blocks
- Do not use placeholder text — use the actual repo data, commit messages, and existing README content to write accurate real content

Return only valid JSON. No markdown, no explanation, just the JSON object.
"""

    response = await client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "user", "content": prompt}
        ],
        response_format={"type": "json_object"},
        temperature=0.7
    )

    result = json.loads(response.choices[0].message.content)
    return result