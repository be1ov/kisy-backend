from fastapi import APIRouter, Depends, HTTPException

from app.core.dependencies.get_current_user import get_current_user
from app.modules.delivery.service import DeliveryService
from app.modules.delivery.enums.delivery_methods import DeliveryMethods
from app.modules.lk.schemas.responses.lk_data_response_schema import (
    LKDataResponseSchema,
)
from app.modules.lk.service import LKService
from app.modules.orders.service import OrderService, UndefinedOrder
from app.modules.users.entities import UserEntity

router = APIRouter()


@router.get("/")
async def lk_root(
    service: LKService = Depends(), user: UserEntity = Depends(get_current_user)
) -> LKDataResponseSchema:
    response = await service.get_info(user)
    return response


@router.get("/orders/{order_id}/tracking")
async def get_order_tracking_lk(
    order_id: str,
    user: UserEntity = Depends(get_current_user),
    order_service: OrderService = Depends(),
    delivery_service: DeliveryService = Depends(),
):
    """Получить информацию для отслеживания заказа в личном кабинете"""
    try:
        order = await order_service.get_by_id(order_id)
        if order.user_id != user.id:
            raise HTTPException(
                status_code=403, detail="Only author of the order can view its details"
            )

        order_schema = order.to_schema()
        tracking_info = await delivery_service.get_tracking_info(order_schema)

        if not tracking_info:
            raise HTTPException(
                status_code=404, detail="Tracking information not available"
            )

        return tracking_info

    except UndefinedOrder as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/orders/{order_id}/delivery-point")
async def get_order_delivery_point_lk(
    order_id: str,
    user: UserEntity = Depends(get_current_user),
    order_service: OrderService = Depends(),
    delivery_service: DeliveryService = Depends(),
):
    """Получить информацию о пункте получения заказа в личном кабинете"""
    try:
        order = await order_service.get_by_id(order_id)
        if order.user_id != user.id:
            raise HTTPException(
                status_code=403, detail="Only author of the order can view its details"
            )

        delivery_method = DeliveryMethods(order.delivery_method)
        delivery_point_info = await delivery_service.get_delivery_point_info(
            delivery_method, order.delivery_point
        )

        if not delivery_point_info:
            raise HTTPException(
                status_code=404, detail="Delivery point information not available"
            )

        return delivery_point_info

    except UndefinedOrder as e:
        raise HTTPException(status_code=404, detail=str(e))
