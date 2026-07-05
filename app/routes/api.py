from typing import List

from fastapi import APIRouter, HTTPException

from app.schemas.schemas import Flight, FlightSearchResponse, FlightSearchQuery, PriceAlert, PriceAlertCreate
from app.models.models import search_flights, get_flight_by_id
from app.cache.cache_manager import get_cached_search_results, set_cached_search_results, get_all_price_alerts, add_price_alert


router = APIRouter(prefix="/travel", tags=["travel"])


@router.get("/flights/search", response_model=FlightSearchResponse)
async def search_flights_endpoint(origin: str, destination: str, date: str) -> FlightSearchResponse:
    query = FlightSearchQuery(origin=origin, destination=destination, date=date)

    cached = get_cached_search_results(query.origin, query.destination, query.date)
    if cached is not None:
        flights = [Flight(**item) for item in cached]
        return FlightSearchResponse(flights=flights, from_cache=True)

    results = search_flights(query.origin, query.destination, query.date)
    as_dict = [flight.dict() for flight in results]
    set_cached_search_results(query.origin, query.destination, query.date, as_dict)

    return FlightSearchResponse(flights=results, from_cache=False)


@router.get("/flights/{flight_id}", response_model=Flight)
async def get_flight_endpoint(flight_id: str) -> Flight:
    flight = get_flight_by_id(flight_id)
    if flight is None:
        raise HTTPException(status_code=404, detail="Flight not found")
    return flight


@router.post("/price-alerts", response_model=PriceAlert)
async def create_price_alert(alert: PriceAlertCreate) -> PriceAlert:
    alert_data = alert.dict()
    add_price_alert(alert_data)
    return PriceAlert(**alert_data)


@router.get("/price-alerts", response_model=List[PriceAlert])
async def list_price_alerts() -> List[PriceAlert]:
    alerts_data = get_all_price_alerts()
    alerts = [PriceAlert(**item) for item in alerts_data]
    return alerts
