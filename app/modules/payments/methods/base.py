from abc import abstractmethod

from app.modules.orders.entities import OrderEntity


class BasePaymentMethod:
    @abstractmethod
    async def get_payment_link(self, order: OrderEntity, payment_id: str=None):
        pass