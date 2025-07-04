from app.modules.delivery.methods.cdek import CDEKDeliveryMethod
from app.modules.delivery.methods.base import BaseDeliveryMethod
from app.modules.delivery.enums.delivery_methods import DeliveryMethods
from app.modules.delivery.schemas.get_cities import CityFilter, DeliveryPointFilter
from app.modules.delivery.schemas.get_countries import GetCountriesSchema


class DeliveryService:

    @staticmethod
    def get_delivery_method(method: DeliveryMethods) -> BaseDeliveryMethod:
        return {
            DeliveryMethods.CDEK: CDEKDeliveryMethod
        }[method]()

    @staticmethod
    def get_all_methods():
        return [method for method in DeliveryMethods]

    async def get_cities(self, body: CityFilter):
        method = self.get_delivery_method(body.method)
        return await method.get_cities(body)

    async def get_countries(self, body: GetCountriesSchema):
        method = self.get_delivery_method(body.method)
        return await method.get_countries()

    async def get_addresses(self, body: DeliveryPointFilter):
        method = self.get_delivery_method(body.method)
        return await method.get_addresses(body)


