import abc
import typing as tp

from app.modules.delivery.enums.delivery_statuses import DeliveryStatusesEnum
from app.modules.delivery.schemas.get_cities import CityFilter, DeliveryPointFilter
from app.modules.delivery.schemas.delivery_info import (
    DeliveryInfo,
    TrackingInfo,
    DeliveryPoint,
)
from app.modules.goods.entities import GoodVariationEntity
from app.modules.orders.entities import OrderEntity
from app.modules.orders.schemas.create import CreateOrderSchema
from app.modules.orders.schemas.order_schema import OrderSchema
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

    @abc.abstractmethod  # todo: refactor
    async def prepare_cdek_data(
        self, order_data: CreateOrderSchema, order_id: str, current_user: UserEntity
    ):
        pass

    @abc.abstractmethod
    async def map_delivery_status(self, status: str) -> DeliveryStatusesEnum:
        pass

    @abc.abstractmethod
    async def get_status(self, order: OrderSchema) -> tp.Optional[DeliveryStatusesEnum]:
        pass

    @abc.abstractmethod
    async def fill_schema(self, schema: OrderSchema) -> OrderSchema:
        """Заполнить схему заказа информацией о доставке"""
        pass

    @abc.abstractmethod
    async def get_delivery_info(self, order: OrderSchema) -> tp.Optional[DeliveryInfo]:
        """Получить информацию о доставке"""
        pass

    @abc.abstractmethod
    async def get_tracking_info(self, order: OrderSchema) -> tp.Optional[TrackingInfo]:
        """Получить информацию для отслеживания"""
        pass

    @abc.abstractmethod
    async def get_delivery_point_info(
        self, delivery_point_code: str
    ) -> tp.Optional[DeliveryPoint]:
        """Получить детальную информацию о пункте получения"""
        pass
