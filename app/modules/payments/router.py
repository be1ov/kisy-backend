from fastapi import APIRouter, Depends

from app.modules.payments.schemas.generate_payment_link import GeneratePaymentLinkSchema
from app.modules.payments.service import PaymentService, PaymentLinkGenerationError

router = APIRouter()


@router.get("/methods")
async def get_methods(service: PaymentService = Depends()):
    return [
        method.model_dump() for method in service.get_payment_methods()
    ]

@router.post("/generate_payment_link")
async def generate_payment_link(body: GeneratePaymentLinkSchema, service: PaymentService = Depends()):
    try:
        link = await service.generate_payment_link(body)
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