import typing as tp
from pydantic import BaseModel, Field
from datetime import datetime


class GoodVariationSchema(BaseModel):
    id: str = Field(...)
    good_id: str = Field(...)

    title: str = Field(...)
    description: str = Field(...)

    latest_price: tp.Optional[float] = Field(None)
    latest_price_date: tp.Optional[datetime] = Field(None)

    weight: float = Field(...)
    length: float = Field(...)
    width: float = Field(...)
    height: float = Field(...)

    photos: tp.List = []

    remaining_stock: tp.Optional[int] = Field(None)
