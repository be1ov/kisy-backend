from fastapi import APIRouter, Depends

from app.core.dependencies.get_current_user import get_current_user
from app.modules.orders.entities import OrderEntity
from app.modules.payments.schemas.generate_payment_link import GeneratePaymentLinkSchema
from app.modules.payments.service import PaymentService, PaymentLinkGenerationError
from app.modules.users.entities import UserEntity

router = APIRouter()


@router.get("/methods")
async def get_methods(service: PaymentService = Depends()):
    return [
        method.model_dump() for method in service.get_payment_methods()
    ]

@router.post("/generate_payment_link")
async def generate_payment_link(body: GeneratePaymentLinkSchema, service: PaymentService = Depends(), current_user:UserEntity = Depends(get_current_user)):
    try:
        link = await service.generate_payment_link(body, current_user)
        return {
            "status": "success",
            "data": {
                "link": link
            }
        }
    except PaymentLinkGenerationError as e:
        return {
            "status": "error",
            "message": str(e)
        }
