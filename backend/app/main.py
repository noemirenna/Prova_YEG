from fastapi import FastAPI

from app.api.participants import router as participants_router

app = FastAPI(title="Congresso 2025 API")

app.include_router(participants_router)


@app.get("/")
def root():
    return {"status": "ok"}