from pydantic import BaseModel, Field


class SetRemainingStockSchema(BaseModel):
    variation_id: str = Field(...)
    remaining_stock: int = Field(...)
