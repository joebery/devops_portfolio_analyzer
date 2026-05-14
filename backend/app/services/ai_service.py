import os
from openai import AsyncOpenAI
import json

client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

async def analyse_repo(repo_data: dict) -> dict:
    prompt = f"""
You are a senior software engineer and DevOps expert reviewing a GitHub repository.

Here is the repository data:
{json.dumps(repo_data, indent=2)}

Analyse this repository and return a JSON object with exactly these fields:

{{
  "project_summary": "A 2-3 sentence plain English summary of what this project is and what it does.",
  "devops_maturity_score": <integer 0-100>,
  "devops_maturity_notes": "2-3 sentences explaining the score. What does the repo do well? What is missing?",
  "readme_suggestions": ["suggestion 1", "suggestion 2", "suggestion 3"],
  "cv_bullets": ["bullet 1", "bullet 2", "bullet 3"]
}}

Scoring guide for devops_maturity_score:
- Has Dockerfile: +20
- Has docker-compose: +10
- Has GitHub Actions workflows: +25
- Has Terraform: +20
- Has Kubernetes manifests: +15
- Has README: +10

CV bullets should follow this format: "Built X using Y, achieving Z"
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