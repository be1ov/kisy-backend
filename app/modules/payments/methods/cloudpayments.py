import uuid
import httpx
import typing as tp

from app.core.config import settings
from app.modules.orders.entities import OrderEntity
from app.modules.payments.methods.base import BasePaymentMethod


class LinkException(ValueError):
    pass


class CloudPaymentsPaymentMethod(BasePaymentMethod):
    async def process_payment(self, body: tp.Any) -> str:
        return body["InvoiceId"]

    async def get_payment_link(self, order: OrderEntity, payment_id: str = None) -> str:
        print('test test TEST1')

        payload = {
            "Amount": order.amount + 350,
            "Currency": order.currency,
            "Description": order.description,
            "InvoiceId": payment_id,
            "AccountId": order.user_id,
            "SendEmail": True,
            "JsonData": {
                "PaymentId": payment_id,
                "cloudpayments": {
                    "CustomerReceipt": {
                        "items": [
                            {
                                "label": item.variation.title,
                                "quantity": item.quantity,
                                "price": item.price,
                                "vat": 5,
                                "amount": item.quantity * item.price
                            } for item in order.details
                        ]
                    }
                }

            }
        }
        print('test test TEST2')
        print(payload)

        auth = (settings.CLOUDPAYMENTS.PUBLIC_ID, settings.CLOUDPAYMENTS.API_SECRET)

        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    "https://api.cloudpayments.ru/orders/create",
                    json=payload,
                    auth=auth,
                    timeout=30.0
                )
                response.raise_for_status()
                result = response.json()

                return result.get("Model", {}).get("Url")

            except httpx.HTTPStatusError as e:
                raise LinkException(f"CloudPayments API error: {e.response.text}")

            except Exception as e:
                raise LinkException(f"Internal server error: {str(e)}")
