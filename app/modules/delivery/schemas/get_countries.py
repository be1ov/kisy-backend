from pydantic import BaseModel

from app.modules.delivery.enums.delivery_methods import DeliveryMethods


class GetCountriesSchema(BaseModel):
    method: DeliveryMethods