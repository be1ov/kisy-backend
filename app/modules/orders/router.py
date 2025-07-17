from fastapi import APIRouter, Depends, HTTPException

from app.core.dependencies.get_current_user import get_current_user
from app.modules.orders.service import OrderCreationError
from app.modules.orders.schemas.create import CreateOrderSchema
from app.modules.orders.service import OrderService
from app.modules.users.entities import UserEntity

router = APIRouter()

@router.post("/create")
async def create_goods(goods: CreateOrderSchema, current_user: UserEntity = Depends(get_current_user), service: OrderService = Depends()):
    try:
        order_data = await service.create_order(goods, current_user)
        return {
            "status": "success",
            "order": order_data["order"],
            "cdek_data": order_data["cdek_data"],
        }
    except OrderCreationError as e:
        raise HTTPException(status_code=403, detail=str(e))
