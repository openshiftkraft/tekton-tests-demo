from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os
import time

app = FastAPI(title="Tekton Allure Demo API", version="1.0.0")
START_TIME = time.time()

class AddRequest(BaseModel):
    a: float
    b: float

class AddResponse(BaseModel):
    result: float

@app.get("/health")
def health():
    return {"status": "ok", "uptime_seconds": round(time.time() - START_TIME, 3)}

@app.get("/version")
def version():
    return {"version": os.getenv("APP_VERSION", "dev")}

@app.post("/add", response_model=AddResponse)
def add(payload: AddRequest):
    result = payload.a + payload.b
    if abs(result) > 1_000_000:
        raise HTTPException(status_code=400, detail="result is too large for this demo")
    return AddResponse(result=result)
