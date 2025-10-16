from fastapi import APIRouter, Depends, HTTPException

from app.core.dependencies.get_current_user import get_current_user
from app.modules.orders.service import OrderCreationError, UndefinedOrder
from app.modules.orders.schemas.create import CreateOrderSchema
from app.modules.orders.schemas.order_schema import OrderSchema
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
            # "cdek_data": order_data["cdek_data"],
        }
    except OrderCreationError as e:
        raise HTTPException(status_code=403, detail=str(e))

@router.get("/{id}")
async def get_order(id: str, current_user: UserEntity = Depends(get_current_user), service: OrderService = Depends()):
    try:
        order = await service.get_by_id(id)
        if order.user_id != current_user.id:
            raise HTTPException(status_code=403, detail="Only author of the order can view its details")
        return order.to_schema()
    
    except UndefinedOrder as e:
        raise HTTPException(status_code=404, detail=str(e))