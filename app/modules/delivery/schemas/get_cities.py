from pydantic import BaseModel

from app.modules.delivery.entities import DeliveryMethods


class GetCitiesSchema(BaseModel):
    method: DeliveryMethods