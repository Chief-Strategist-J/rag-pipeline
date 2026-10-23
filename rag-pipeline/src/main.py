"""
Root Application Bootstrap and Health Delivery.
"""
from contextlib import asynccontextmanager
from typing import AsyncGenerator, Dict, Any
from fastapi import FastAPI, status

from src.infra.config.settings import settings


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    yield


app = FastAPI(
    title="RAG Pipeline API",
    version=settings.API_VERSION,
    lifespan=lifespan,
    docs_url=f"/api/{settings.API_VERSION}/docs",
    openapi_url=f"/api/{settings.API_VERSION}/openapi.json",
)


@app.get(
    "/healthz",
    status_code=status.HTTP_200_OK,
    summary="Liveness Probe",
    tags=["Health"]
)
async def healthz() -> Dict[str, Any]:
    return {
        "status": "pass",
        "service": settings.SERVICE_NAME,
        "environment": settings.ENVIRONMENT
    }


@app.get(
    "/readyz",
    status_code=status.HTTP_200_OK,
    summary="Readiness Probe",
    tags=["Health"]
)
async def readyz() -> Dict[str, Any]:
    return {
        "status": "ready",
        "service": settings.SERVICE_NAME,
        "environment": settings.ENVIRONMENT
    }


@app.get("/", status_code=status.HTTP_200_OK)
async def root() -> Dict[str, str]:
    return {
        "message": "Production RAG Pipeline API",
        "version": settings.API_VERSION,
        "docs": f"/api/{settings.API_VERSION}/docs"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "src.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=(settings.ENVIRONMENT == "development")
    )
