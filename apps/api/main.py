"""FastAPI application for the QForge.

Exposes the engine's run() and sweep() APIs over HTTP, plus experiment
registry browsing and stored result retrieval.

Run from repo root:
    venv/bin/python -m uvicorn apps.api.main:app --reload --port 8000
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from apps.api.routes import bloch, experiments, results

app = FastAPI(
    title="Quantum Experiment API",
    version="0.1.0",
    description="REST API for the QForge.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(experiments.router, prefix="/api/experiments", tags=["experiments"])
app.include_router(results.router, prefix="/api/results", tags=["results"])
app.include_router(bloch.router, prefix="/api/bloch", tags=["bloch"])


@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
