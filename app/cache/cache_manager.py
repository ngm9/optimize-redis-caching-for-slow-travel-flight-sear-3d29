import json
import time
from typing import Any, Dict, List, Optional, Tuple

from app.redis_client import get_redis_client


POPULAR_SEARCHES: List[Tuple[str, str, str]] = [
    ("NYC", "LON", "2024-10-01"),
    ("SFO", "LAX", "2024-10-05"),
    ("NYC", "PAR", "2024-10-03"),
]


def _build_search_prefix(origin: str, destination: str, date: str) -> str:
    prefix = f"flights_search:{origin}:{destination}:{date}:"
    return prefix


def get_cached_search_results(origin: str, destination: str, date: str) -> Optional[List[Dict[str, Any]]]:
    client = get_redis_client()
    prefix = _build_search_prefix(origin, destination, date)
    cursor = 0
    found_key = None
    while True:
        cursor, keys = client.scan(cursor=cursor, match=prefix + "*", count=50)
        if keys:
            found_key = keys[0]
            break
        if cursor == 0:
            break
    if not found_key:
        return None
    raw = client.get(found_key)
    if raw is None:
        return None
    data = json.loads(raw.decode("utf-8"))
    return data


def set_cached_search_results(origin: str, destination: str, date: str, results: List[Dict[str, Any]]) -> None:
    client = get_redis_client()
    prefix = _build_search_prefix(origin, destination, date)
    suffix = str(int(time.time()))
    key = prefix + suffix
    value = json.dumps(results)
    client.set(key, value)


def prewarm_popular_searches() -> None:
    from app.models.models import search_flights

    for origin, destination, date in POPULAR_SEARCHES:
        existing = get_cached_search_results(origin, destination, date)
        if existing is None:
            results = search_flights(origin, destination, date)
            as_dict = [flight.dict() for flight in results]
            set_cached_search_results(origin, destination, date, as_dict)


PRICE_ALERTS_KEY = "price_alerts"


def get_all_price_alerts() -> List[Dict[str, Any]]:
    client = get_redis_client()
    raw = client.get(PRICE_ALERTS_KEY)
    if raw is None:
        return []
    alerts = json.loads(raw.decode("utf-8"))
    return alerts


def add_price_alert(alert: Dict[str, Any]) -> None:
    client = get_redis_client()
    raw = client.get(PRICE_ALERTS_KEY)
    if raw is None:
        alerts: List[Dict[str, Any]] = []
    else:
        alerts = json.loads(raw.decode("utf-8"))
    alerts.append(alert)
    serialized = json.dumps(alerts)
    client.set(PRICE_ALERTS_KEY, serialized)
