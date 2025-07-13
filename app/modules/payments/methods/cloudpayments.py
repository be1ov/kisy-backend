import uuid
import httpx

from app.core.config import settings
from app.modules.orders.entities import OrderEntity
from app.modules.payments.methods.base import BasePaymentMethod


class LinkException(ValueError):
    pass

class CloudPaymentsPaymentMethod(BasePaymentMethod):
    async def get_payment_link(self, order: OrderEntity, payment_id: str = None) -> str:

        payload = {
            "Amount": order.amount,
            "Currency": order.currency,
            "Description": order.description,
            "InvoiceId": order.id,
            "AccountId": order.user_id,
            "SendEmail": True,
            "JsonData":{
                "PaymentId": payment_id,
                "cloudpayments":{
                    "receipt":{
                        "items":[
                            {
                                "product": item.variation.title,
                                "quantity": item.quantity,
                                "price": item.price
                            } for item in order.details
                        ]
                    }
                }

            }
        }

        auth = (settings.CLOUDPAYMENTS.CLOUDPAYMENTS_PUBLIC_ID, settings.CLOUDPAYMENTS.CLOUDPAYMENTS_API_SECRET)

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



