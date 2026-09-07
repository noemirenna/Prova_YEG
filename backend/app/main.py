# placeholder
from fastapi import FastAPI
from app.database import Base, engine

app = FastAPI(title="Congresso 2025 API")

Base.metadata.create_all(bind=engine)


@app.get("/")
def root():
    return {"status": "ok"}