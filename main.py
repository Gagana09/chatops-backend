from fastapi import FastAPI, Request
import os
import http.client
import json

app = FastAPI()

# GitHub repo details
REPO_OWNER = "Gagana09"
REPO_NAME = "chatops-backend"
WORKFLOW_FILE = "deploy.yml"  # .github/workflows/deploy.yml

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")


@app.post("/deploy")
async def deploy(request: Request):
    # Text after /deploy in Slack, e.g. "/deploy backend"
    form_data = await request.form()
    service = form_data.get("text") or "backend"

    if not GITHUB_TOKEN:
        # Server misconfiguration – helpful message
        return {
            "response_type": "ephemeral",
            "text": "❌ Server error: GITHUB_TOKEN is not configured in Render."
        }

    # GitHub Actions workflow dispatch endpoint
    path = f"/repos/{REPO_OWNER}/{REPO_NAME}/actions/workflows/{WORKFLOW_FILE}/dispatches"

    body = {
        "ref": "main",          # branch
        "inputs": {
            "service": service  # input to workflow
        }
    }

    # Prepare HTTP request to GitHub
    conn = http.client.HTTPSConnection("api.github.com")
    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "User-Agent": "chatops-backend",
        "Accept": "application/vnd.github+json",
    }
    conn.request("POST", path, body=json.dumps(body), headers=headers)
    resp = conn.getresponse()
    resp_text = resp.read().decode()

    # 204 = success for workflow_dispatch
    if resp.status == 204:
        return {
            "response_type": "in_channel",
            "text": f"🚀 GitHub Actions deployment triggered for `{service}` (workflow `{WORKFLOW_FILE}`)."
        }
    else:
        # Show error details so we can debug if needed
        return {
            "response_type": "ephemeral",
            "text": (
                f"❌ Failed to trigger GitHub Actions.\n"
                f"Status: {resp.status} {resp.reason}\n"
                f"Response: ```{resp_text[:200]}```"
            )
        }
