from typing import Optional
from pydantic import BaseModel, Field


class DeliveryInfo(BaseModel):
    """Универсальная информация о доставке"""

    track_number: Optional[str] = Field(None, description="Трек-номер для отслеживания")
    delivery_point_code: Optional[str] = Field(None, description="Код пункта получения")
    delivery_point_address: Optional[str] = Field(
        None, description="Адрес пункта получения"
    )
    delivery_point_name: Optional[str] = Field(
        None, description="Название пункта получения"
    )
    delivery_point_working_hours: Optional[str] = Field(
        None, description="Режим работы пункта"
    )
    delivery_point_phone: Optional[str] = Field(None, description="Телефон пункта")
    estimated_delivery_date: Optional[str] = Field(
        None, description="Ожидаемая дата доставки"
    )


class TrackingInfo(BaseModel):
    """Информация для отслеживания заказа"""

    track_number: Optional[str] = Field(None, description="Трек-номер")
    track_url: Optional[str] = Field(None, description="URL для отслеживания")
    delivery_service: Optional[str] = Field(None, description="Служба доставки")
    current_status: Optional[str] = Field(None, description="Текущий статус доставки")
    status_description: Optional[str] = Field(None, description="Описание статуса")
    last_updated: Optional[str] = Field(
        None, description="Последнее обновление статуса"
    )


class DeliveryPoint(BaseModel):
    """Информация о пункте получения"""

    code: str = Field(..., description="Уникальный код пункта")
    name: str = Field(..., description="Название пункта")
    address: str = Field(..., description="Полный адрес")
    city: Optional[str] = Field(None, description="Город")
    working_hours: Optional[str] = Field(None, description="Режим работы")
    phone: Optional[str] = Field(None, description="Телефон")
    coordinates: Optional[dict] = Field(
        None, description="Координаты (latitude, longitude)"
    )
    additional_info: Optional[str] = Field(
        None, description="Дополнительная информация"
    )
