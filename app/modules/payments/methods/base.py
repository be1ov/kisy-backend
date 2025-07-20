from abc import abstractmethod

from app.modules.orders.entities import OrderEntity
import typing as tp

class BasePaymentMethod:
    @abstractmethod
    async def get_payment_link(self, order: OrderEntity, payment_id: str=None) -> str:
        pass

    @abstractmethod
    async def process_payment(self, body: tp.Any) -> str:
        pass