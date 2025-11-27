from fastapi import FastAPI, Request
import uvicorn

app = FastAPI()

@app.post("/deploy")
async def deploy(request: Request):
    form_data = await request.form()
    user_text = form_data.get("text", "")

    print("Deploy command received:", user_text)

    return {
        "response_type": "in_channel",
        "text": f"🚀 Deployment started for service: {user_text}"
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
