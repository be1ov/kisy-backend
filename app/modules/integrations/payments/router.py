from webbrowser import Error

from fastapi import APIRouter, Depends, Request


from app.modules.integrations.payments.service import PaymentIntegrationService

router = APIRouter()

@router.post("/integration/payment_success")
async def payment_success(method: str, request: Request, service: PaymentIntegrationService = Depends()):
    try:
        body = await request.body()
        await service.process_payment(method, body)

        return {
            "code": 0
        }
    except ValueError as e:
        print(f"Ошибка получения оплаты: {e}")
        raise e