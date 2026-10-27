from fastapi import FastAPI

import models
from database import Base, engine

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Job Application Tracker")


@app.get("/")
def health():
    return {"status": "ok"}