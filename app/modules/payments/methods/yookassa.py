from yookassa.domain.common import ConfirmationType
from yookassa.domain.models import Currency
from yookassa.domain.request import PaymentRequestBuilder
from yookassa.domain.response import PaymentResponse

from app.core.config import settings
from app.modules.goods.enums.vat_rates import VATRate
from app.modules.orders.entities import OrderEntity
from app.modules.payments.enums.currencies import Currencies
from app.modules.payments.methods.base import BasePaymentMethod
from yookassa import Configuration, Payment


class YookassaPaymentMethod(BasePaymentMethod):
    def __init__(self):
        Configuration.configure(
            account_id=settings.YOOKASSA.SHOP_ID,
            secret_key=settings.YOOKASSA.SECRET_KEY
        )

    @staticmethod
    def _map_currency(currency: Currencies) -> Currency:
        return {
            Currencies.RUB: Currency.RUB
        }[currency]

    @staticmethod
    def _map_vat_rate(rate: VATRate) -> str:
        return {
            VATRate.NONE: "1",
            VATRate.VAT_0: "2",
            VATRate.VAT_10: "3",
            VATRate.VAT_20: "4"
        }[rate]

    def _get_order_items(self, order: OrderEntity):
        return [
            {
                "description": detail.variation.receipt_description,
                "quantity": detail.quantity,
                "amount": {
                    "value": detail.amount,
                    "currency": self._map_currency(order.currency)
                },
                "vat_code": self._map_vat_rate(detail.variation.good.vat_rate),
                "payment_mode": "full_payment",
                "payment_subject": "commodity"
            } for detail in order.details
        ]

    async def _create_payment(self, order: OrderEntity, idempotency_key: str) -> PaymentResponse:
        return Payment.create({
            "amount": {
                "value": order.amount,
                "currency": self._map_currency(order.currency)
            },
            "confirmation": {
                "type": "redirect",
                "return_url": settings.YOOKASSA.RETURN_URL,
            },
            "capture": True,
            "description": order.description,
            "metadata": {
                "order_id": order.id
            },
            "receipt": {
                "customer": {
                    "full_name": order.user.full_name,
                    "email": order.user.email,
                    "phone": order.user.phone,
                },
                "items": self._get_order_items(order),
            }
        }, idempotency_key)

    async def get_payment_link(self, order: OrderEntity, payment_id: str=None) -> str:
        payment = await self._create_payment(order, payment_id)
        return f"{payment.confirmation.confirmation_url}"