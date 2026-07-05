from typing import List, Optional

from app.schemas.schemas import Flight


_FLIGHTS_DB: List[Flight] = []


def initialize_flights_data() -> None:
    global _FLIGHTS_DB
    if _FLIGHTS_DB:
        return
    _FLIGHTS_DB = [
        Flight(id="FL1", origin="NYC", destination="LON", date="2024-10-01", carrier="UTK", price=500.0),
        Flight(id="FL2", origin="NYC", destination="LON", date="2024-10-01", carrier="UTK", price=520.0),
        Flight(id="FL3", origin="SFO", destination="LAX", date="2024-10-05", carrier="UTK", price=120.0),
        Flight(id="FL4", origin="NYC", destination="PAR", date="2024-10-03", carrier="UTK", price=480.0),
        Flight(id="FL5", origin="NYC", destination="LON", date="2024-10-02", carrier="UTK", price=510.0),
    ]


def search_flights(origin: str, destination: str, date: str) -> List[Flight]:
    results: List[Flight] = []
    for flight in _FLIGHTS_DB:
        if flight.origin == origin and flight.destination == destination and flight.date == date:
            results.append(flight)
    return results


def get_flight_by_id(flight_id: str) -> Optional[Flight]:
    for flight in _FLIGHTS_DB:
        if flight.id == flight_id:
            return flight
    return None
