"""FastAPI application exposing health endpoints."""
from __future__ import annotations

from fastapi import FastAPI

app = FastAPI(title="Trading MVP", version="0.1.0")


@app.get("/healthz")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/version")
def version() -> dict[str, str]:
    return {"version": app.version}


__all__ = ["app"]
