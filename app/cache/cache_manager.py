import json
from typing import Any, Dict, List, Optional, Tuple

from app.redis_client import get_redis_client


POPULAR_SEARCHES: List[Tuple[str, str, str]] = [
    ("NYC", "LON", "2024-10-01"),
    ("SFO", "LAX", "2024-10-05"),
    ("NYC", "PAR", "2024-10-03"),
]


FLIGHT_SEARCH_TTL_SECONDS = 300


def _build_search_key(origin: str, destination: str, date: str) -> str:
    return f"flights_search:{origin}:{destination}:{date}"


def get_cached_search_results(origin: str, destination: str, date: str) -> Optional[List[Dict[str, Any]]]:
    client = get_redis_client()
    key = _build_search_key(origin, destination, date)
    raw = client.get(key)
    if raw is None:
        return None
    return json.loads(raw)


def set_cached_search_results(origin: str, destination: str, date: str, results: List[Dict[str, Any]]) -> None:
    client = get_redis_client()
    key = _build_search_key(origin, destination, date)
    value = json.dumps(results)
    client.set(key, value, ex=FLIGHT_SEARCH_TTL_SECONDS)


def prewarm_popular_searches() -> None:
    from app.models.models import search_flights

    client = get_redis_client()
    keys = [_build_search_key(o, d, dt) for o, d, dt in POPULAR_SEARCHES]

    pipe = client.pipeline(transaction=False)
    for key in keys:
        pipe.get(key)
    cached_values = pipe.execute()

    missing: List[Tuple[str, str, str, List[Dict[str, Any]]]] = []
    for (origin, destination, date), cached in zip(POPULAR_SEARCHES, cached_values):
        if cached is None:
            results = search_flights(origin, destination, date)
            missing.append((origin, destination, date, [flight.dict() for flight in results]))

    if not missing:
        return

    write_pipe = client.pipeline(transaction=False)
    for origin, destination, date, as_dict in missing:
        key = _build_search_key(origin, destination, date)
        write_pipe.set(key, json.dumps(as_dict), ex=FLIGHT_SEARCH_TTL_SECONDS)
    write_pipe.execute()


PRICE_ALERTS_KEY = "price_alerts"


def get_all_price_alerts() -> List[Dict[str, Any]]:
    client = get_redis_client()
    raw_items = client.lrange(PRICE_ALERTS_KEY, 0, -1)
    return [json.loads(item) for item in raw_items]


def add_price_alert(alert: Dict[str, Any]) -> None:
    client = get_redis_client()
    client.lpush(PRICE_ALERTS_KEY, json.dumps(alert))