from typing import List, Optional, TypeVar, Generic

from pydantic import BaseModel, Field

from app.modules.delivery.enums.delivery_methods import DeliveryMethods

T = TypeVar('T')

class CityResponse(BaseModel):
    code: int = Field(..., description="Уникальный код города в СДЭК")
    city: str = Field(..., description="Название города")
    city_uuid: str = Field(..., description="uuid города")
    country_code: str = Field(..., description="Код страны")
    region: Optional[str] = Field(None, description="Регион")
    longitude: Optional[float] = Field(None, description="Долгота")
    latitude: Optional[float] = Field(None, description="Широта")

class Location(BaseModel):
    address: str
    address_full: str

class DeliveryPointResponse(BaseModel):
    code: str = Field(..., description="Уникальный код пункта")
    name: str = Field(..., description="Название пункта")
    location: Location


class ListResponse(BaseModel, Generic[T]):
    data: List[T]
    count: int = Field(..., description="Общее количество элементов")


class DeliveryPointFilter(BaseModel):
    method: DeliveryMethods
    city_code: int


class CityFilter(BaseModel):
    method: DeliveryMethods
    country_code: str