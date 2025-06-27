from fastapi import APIRouter, Depends, HTTPException
from fastapi.params import Query

from app.modules.goods.schemas.create import CreateGoodSchema
from app.modules.goods.service import GoodsService

router = APIRouter()


@router.get("/")
async def get_all(page: int = Query(1, ge=1), size: int = Query(10, le=100), service: GoodsService = Depends()):
    goods = await service.get_goods_paginated(page, size)
    return goods


@router.get("/{good_id}")
async def get_by_id(good_id: str, service: GoodsService = Depends()):
    good = await service.get_by_id(good_id)
    if good is None:
        raise HTTPException(detail="Good with provided id can not be found", status_code=404)
    return good


@router.post("/create")
async def create(data: CreateGoodSchema, service: GoodsService = Depends()):
    return await service.create(data)
