from pydantic import BaseModel

from app.modules.payments.enums.payment_methods import PaymentMethods


class GeneratePaymentLinkSchema(BaseModel):
    method: PaymentMethods
    order_id: str