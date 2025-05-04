# ingestion/main.py
import asyncio
from fastapi import FastAPI
from .fetch_stocks import producer_loop

app = FastAPI(title="Ingestion Service")

@app.on_event("startup")
async def _startup():
    asyncio.create_task(producer_loop())

@app.get("/healthz")
def health():
    return {"status": "ok"}
