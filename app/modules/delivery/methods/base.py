import abc
import typing as tp

from app.modules.delivery.schemas.get_cities import CityFilter, DeliveryPointFilter
from app.modules.goods.entities import GoodVariationEntity
from app.modules.orders.schemas.create import CreateOrderSchema
from app.modules.users.entities import UserEntity


class BaseDeliveryMethod:
    @abc.abstractmethod
    async def get_cities(self, filter: CityFilter):
        pass

    @abc.abstractmethod
    async def get_countries(self):
        pass

    @abc.abstractmethod
    async def get_addresses(self, filter: DeliveryPointFilter):
        pass

    @abc.abstractmethod
    async def get_delivery_point(self, code: str):
        pass

    @abc.abstractmethod
    async def prepare_cdek_data(self, order_data: CreateOrderSchema, variations: tp.Dict[str, tp.Dict], order_id: str, current_user: UserEntity):
        pass

