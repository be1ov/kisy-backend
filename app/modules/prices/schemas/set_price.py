from pydantic import BaseModel


class SetPriceSchema(BaseModel):
    variation_id: str
    price: float