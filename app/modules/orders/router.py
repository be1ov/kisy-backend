from fastapi import APIRouter, Depends, HTTPException

from app.core.dependencies.get_current_user import get_current_user
from app.modules.delivery.service import DeliveryService
from app.modules.delivery.enums.delivery_methods import DeliveryMethods
from app.modules.orders.service import OrderCreationError, UndefinedOrder
from app.modules.orders.schemas.create import CreateOrderSchema
from app.modules.orders.schemas.order_schema import OrderSchema
from app.modules.orders.service import OrderService
from app.modules.users.entities import UserEntity

router = APIRouter()


@router.post("/create")
async def create_goods(
    goods: CreateOrderSchema,
    current_user: UserEntity = Depends(get_current_user),
    service: OrderService = Depends(),
):
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
async def get_order(
    id: str,
    current_user: UserEntity = Depends(get_current_user),
    service: OrderService = Depends(),
    delivery_service: DeliveryService = Depends(),
    include_delivery_info: bool = True,
):
    try:
        order = await service.get_by_id(id)
        if order.user_id != current_user.id:
            raise HTTPException(
                status_code=403, detail="Only author of the order can view its details."
            )

        order_schema = order.to_schema()

        # Если запрошена расширенная информация о доставке
        if include_delivery_info:
            order_schema = await delivery_service.fill_order_delivery_info(order_schema)

        return order_schema

    except UndefinedOrder as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/{id}/tracking")
async def get_order_tracking(
    id: str,
    current_user: UserEntity = Depends(get_current_user),
    service: OrderService = Depends(),
    delivery_service: DeliveryService = Depends(),
):
    """Получить информацию для отслеживания заказа"""
    try:
        order = await service.get_by_id(id)
        if order.user_id != current_user.id:
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


@router.get("/{id}/delivery-info")
async def get_order_delivery_info(
    id: str,
    current_user: UserEntity = Depends(get_current_user),
    service: OrderService = Depends(),
    delivery_service: DeliveryService = Depends(),
):
    """Получить информацию о доставке заказа"""
    try:
        order = await service.get_by_id(id)
        if order.user_id != current_user.id:
            raise HTTPException(
                status_code=403, detail="Only author of the order can view its details"
            )

        order_schema = order.to_schema()
        delivery_info = await delivery_service.get_delivery_info(order_schema)

        if not delivery_info:
            raise HTTPException(
                status_code=404, detail="Delivery information not available"
            )

        return delivery_info

    except UndefinedOrder as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/{id}/delivery-point")
async def get_order_delivery_point(
    id: str,
    current_user: UserEntity = Depends(get_current_user),
    service: OrderService = Depends(),
    delivery_service: DeliveryService = Depends(),
):
    """Получить информацию о пункте получения заказа"""
    try:
        order = await service.get_by_id(id)
        if order.user_id != current_user.id:
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
