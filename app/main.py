from fastapi import FastAPI

from app import models
from app.database import Base, engine

# Creates the tables at startup if they do not exist
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Prêts de matériel du laboratoire")

@app.get("/")
def root():
    return {"ok": True}