from fastapi import APIRouter, Depends

from app.modules.prices.schemas.set_price import SetPriceSchema
from app.modules.prices.service import PricingService

router = APIRouter()


@router.post("/set")
async def set_price(data: SetPriceSchema, service: PricingService = Depends()):
    await service.set_price(data)
    return {
        "status": "success",
    }
