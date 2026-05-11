from fastapi import FastAPI
from sqlalchemy import text
from app.db import engine, Base
from app import models
from app.routers import repos

app = FastAPI()

Base.metadata.create_all(bind=engine)

app.include_router(repos.router)

@app.get("/")
def root():
    return {"message": "hello"}

@app.get("/health")
def health():
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return {"status": "ok", "db": "connected"}
    except Exception as e:
        return {"status": "ok", "db": "not connected", "error": str(e)}