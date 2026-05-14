import httpx
import sys
import os

def main():
    if len(sys.argv) < 2:
        print("Usage: python scripts/update_readme.py <github_url>")
        print("Example: python scripts/update_readme.py https://github.com/joebery/devops_portfolio_analyzer")
        sys.exit(1)

    github_url = sys.argv[1].rstrip("/")
    parts = github_url.split("/")
    owner = parts[-2]
    repo = parts[-1]

    api_url = f"http://localhost:8000/api/v1/repos/test-ai/{owner}/{repo}"

    print(f"🔍 Analysing {owner}/{repo}...")

    response = httpx.get(api_url, timeout=60)
    response.raise_for_status()

    data = response.json()
    readme_content = data.get("generated_readme", "")

    if not readme_content:
        print("❌ No README generated")
        sys.exit(1)

    readme_path = os.path.join(os.path.dirname(__file__), "..", "README.md")

    with open(readme_path, "w", encoding="utf-8") as f:
        f.write(readme_content)

    print("✅ README.md updated successfully")
    print("\n📊 Maturity Score:", data.get("devops_maturity_score"))
    print("\n📝 CV Bullets:")
    for bullet in data.get("cv_bullets", []):
        print(f"  • {bullet}")

if __name__ == "__main__":
    main()