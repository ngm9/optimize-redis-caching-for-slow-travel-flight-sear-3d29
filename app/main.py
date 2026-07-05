from fastapi import FastAPI

from app.routes.api import router as api_router
from app.models.models import initialize_flights_data
from app.cache.cache_manager import prewarm_popular_searches


app = FastAPI(title="Travel Flight Search API")


@app.on_event("startup")
async def startup_event() -> None:
    initialize_flights_data()
    prewarm_popular_searches()


@app.get("/health")
async def health() -> dict:
    return {"status": "ok"}


app.include_router(api_router, prefix="/api")
