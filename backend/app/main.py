from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.dashboard import router as dashboard_router
from app.api.participants import router as participants_router

app = FastAPI(title="Congresso 2025 API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5500", "http://127.0.0.1:5500"],
    allow_credentials=False,
    allow_methods=["GET"],
    allow_headers=["*"],
)

app.include_router(participants_router)
app.include_router(dashboard_router)


@app.get("/")
def root():
    return {"status": "ok"}