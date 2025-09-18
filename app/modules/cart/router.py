from fastapi import APIRouter, Depends, HTTPException

from app.core.dependencies.get_current_user import get_current_user
from app.modules.cart.schemas.add_to_cart import AddToCartSchema
from app.modules.cart.service import CartService
from app.modules.goods.service import GoodsService
from app.modules.users.entities import UserEntity
from app.modules.users.service import UserService

router = APIRouter()


@router.get("/")
async def get(
    cart_service: CartService = Depends(),
    current_user: UserEntity = Depends(get_current_user),
):
    return await cart_service.get(current_user)


@router.post("/add")
async def add(
    data: AddToCartSchema,
    cart_service: CartService = Depends(),
    goods_service: GoodsService = Depends(),
    current_user: UserEntity = Depends(get_current_user),
):
    variation = await goods_service.get_variation_by_id(data.variation_id)
    if variation is None:
        raise HTTPException(detail="Undefined variation", status_code=404)

    if data.quantity < 1:
        raise HTTPException(detail="Quantity must be at least 1", status_code=400)

    await cart_service.add_to_cart(current_user, variation, data.quantity)

    return {
        "status": "success",
    }


@router.delete("/delete")
async def delete(
    data: AddToCartSchema,
    cart_service: CartService = Depends(),
    goods_service: GoodsService = Depends(),
    current_user: UserEntity = Depends(get_current_user),
):
    variation = await goods_service.get_variation_by_id(data.variation_id)
    if variation is None:
        raise HTTPException(detail="Undefined variation", status_code=404)

    await cart_service.delete_from_cart(current_user, variation, data.quantity)
    return {"status": "success"}
