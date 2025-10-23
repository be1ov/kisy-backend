from app.modules.delivery.enums.delivery_statuses import DeliveryStatusesEnum
from app.modules.delivery.methods.cdek import CDEKDeliveryMethod
from app.modules.delivery.methods.base import BaseDeliveryMethod
from app.modules.delivery.enums.delivery_methods import DeliveryMethods
from app.modules.delivery.schemas.get_cities import CityFilter, DeliveryPointFilter
from app.modules.delivery.schemas.get_countries import GetCountriesSchema
from app.modules.delivery.schemas.delivery_info import (
    DeliveryInfo,
    TrackingInfo,
    DeliveryPoint,
)
from app.modules.orders.entities import OrderEntity

import typing as tp

from app.modules.orders.schemas.order_schema import OrderSchema


class DeliveryService:
    @staticmethod
    def get_delivery_method(method: DeliveryMethods) -> BaseDeliveryMethod:
        return {DeliveryMethods.CDEK: CDEKDeliveryMethod}[method]()

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

    async def get_order_status(
        self, order: OrderSchema
    ) -> tp.Optional[DeliveryStatusesEnum]:
        method = self.get_delivery_method(DeliveryMethods(order.delivery_method))
        return await method.get_status(order)

    async def fill_order_delivery_info(self, order: OrderSchema) -> OrderSchema:
        """Заполнить заказ полной информацией о доставке"""
        try:
            method = self.get_delivery_method(DeliveryMethods(order.delivery_method))
            return await method.fill_schema(order)
        except Exception as e:
            # Если не удалось получить информацию через основной метод,
            # пытаемся хотя бы получить информацию о ПВЗ
            try:
                method = self.get_delivery_method(
                    DeliveryMethods(order.delivery_method)
                )
                delivery_point_info = await method.get_delivery_point_info(
                    order.delivery_point
                )
                if delivery_point_info:
                    order.delivery_point_info = delivery_point_info
                    # Создаем базовую информацию о доставке
                    order.delivery_info = DeliveryInfo(
                        track_number=order.track_number,
                        delivery_point_code=order.delivery_point,
                        delivery_point_address=delivery_point_info.address,
                        delivery_point_name=delivery_point_info.name,
                        delivery_point_working_hours=delivery_point_info.working_hours,
                        delivery_point_phone=delivery_point_info.phone,
                        estimated_delivery_date=None,
                    )
            except Exception:
                pass  # Не удалось получить даже информацию о ПВЗ

            return order

    async def get_delivery_info(self, order: OrderSchema) -> tp.Optional[DeliveryInfo]:
        try:
            method = self.get_delivery_method(DeliveryMethods(order.delivery_method))
            return await method.get_delivery_info(order)
        except Exception:
            return None

    async def get_tracking_info(self, order: OrderSchema) -> tp.Optional[TrackingInfo]:
        try:
            method = self.get_delivery_method(DeliveryMethods(order.delivery_method))
            return await method.get_tracking_info(order)
        except Exception:
            return None

    async def get_delivery_point_info(
        self, delivery_method: DeliveryMethods, delivery_point_code: str
    ) -> tp.Optional[DeliveryPoint]:
        try:
            method = self.get_delivery_method(delivery_method)
            return await method.get_delivery_point_info(delivery_point_code)
        except Exception:
            return None
