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


@router.get("/history/{variation_id}")
async def get_price_history(variation_id: str, service: PricingService = Depends()):
    history = await service.get_price_history(variation_id)
    return {
        "status": "success",
        "data": history,
    }
