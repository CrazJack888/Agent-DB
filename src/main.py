from fastapi import FastAPI
from src.api.router import api_router

app = FastAPI(title="Agent DB", version="1.0.0")
app.include_router(api_router)


@app.get("/health")
async def health():
    return {"status": "ok"}
