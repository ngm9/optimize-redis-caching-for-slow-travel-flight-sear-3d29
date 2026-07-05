from typing import List

from pydantic import BaseModel, Field


class Flight(BaseModel):
    id: str = Field(...)
    origin: str = Field(...)
    destination: str = Field(...)
    date: str = Field(...)
    carrier: str = Field(...)
    price: float = Field(...)


class FlightSearchQuery(BaseModel):
    origin: str
    destination: str
    date: str


class FlightSearchResponse(BaseModel):
    flights: List[Flight]
    from_cache: bool


class PriceAlertCreate(BaseModel):
    user_id: str
    origin: str
    destination: str
    date: str
    max_price: float


class PriceAlert(BaseModel):
    user_id: str
    origin: str
    destination: str
    date: str
    max_price: float
