from app.modules.orders.entities import OrderEntity
from app.modules.payments.methods.base import BasePaymentMethod


class CloudPaymentsPaymentMethod(BasePaymentMethod):
    async def get_payment_link(self, order: OrderEntity, payment_id: str = None) -> str:
        return ""

