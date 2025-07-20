from app.modules.delivery.methods.cdek import CDEKDeliveryMethod
from app.modules.delivery.methods.base import BaseDeliveryMethod
from app.modules.delivery.enums.delivery_methods import DeliveryMethods
from app.modules.delivery.schemas.get_cities import CityFilter, DeliveryPointFilter
from app.modules.delivery.schemas.get_countries import GetCountriesSchema
from app.modules.goods.entities import GoodVariationEntity
from app.modules.orders.schemas.create import CreateOrderSchema

import typing as tp

from app.modules.users.entities import UserEntity


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

    async def get_delivery_point(self, code: str, method: DeliveryMethods):
        method = self.get_delivery_method(method)
        return await method.get_delivery_point(code)

    async def prepare_cdek_data(self, order_data: CreateOrderSchema, variations: tp.Dict[str, tp.Dict], order_id: str, current_user: UserEntity):
        method = self.get_delivery_method(order_data.delivery_method)
        return await method.prepare_cdek_data(order_data, variations, order_id, current_user)


