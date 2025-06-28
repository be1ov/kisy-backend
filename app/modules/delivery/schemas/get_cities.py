from typing import List, Optional, Union

from pydantic import BaseModel, Field

from app.modules.delivery.entities import DeliveryMethods


class GetCitiesSchema(BaseModel):
    method: DeliveryMethods

class CountryResponse(BaseModel):
    code: str = Field(..., description="Код страны (ISO 3166-1 alpha-2)")
    name: str = Field(..., description="Название страны")
    currency: Optional[str] = Field(None, description="Валюта страны")
    currency_code: Optional[str] = Field(None, description="Код валюты")

class CityResponse(BaseModel):
    code: int = Field(..., description="Уникальный код города в СДЭК")
    name: str = Field(..., description="Название города")
    country_code: str = Field(..., description="Код страны")
    region: Optional[str] = Field(None, description="Регион")
    postal_codes: Optional[List[str]] = Field(None, description="Почтовые индексы")
    longitude: Optional[float] = Field(None, description="Долгота")
    latitude: Optional[float] = Field(None, description="Широта")

class DeliveryPointResponse(BaseModel):
    code: str = Field(..., description="Уникальный код пункта")
    name: str = Field(..., description="Название пункта")
    address: str = Field(..., description="Полный адрес")
    city_code: int = Field(..., description="Код города")
    work_time: Optional[str] = Field(None, description="График работы")
    phone: Optional[str] = Field(None, description="Телефон")
    is_handout: bool = Field(..., description="Флаг выдачи")

class ListResponse(BaseModel):
    data: List[Union[CountryResponse, CityResponse, DeliveryPointResponse]]
    count: int = Field(..., description="Общее количество элементов")


class DeliveryPointFilter(BaseModel):
    city_code: Optional[int] = Field(
        None,
        description="Код города для фильтрации"
    )

class CityFilter(BaseModel):
    country_code: Optional[Union[str, List[str]]] = Field(
        None,
        description="Код страны или список кодов для фильтрации"
    )