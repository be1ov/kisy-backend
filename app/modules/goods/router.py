from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from fastapi.params import Query

from app.modules.goods.schemas.create import CreateGoodSchema
from app.modules.goods.service import GoodsService

router = APIRouter()


@router.get("/")
async def get_all(
    page: int = Query(1, ge=1),
    size: int = Query(10, le=100),
    service: GoodsService = Depends(),
):
    goods = await service.get_goods_paginated(page, size)
    return goods


@router.get("/{good_id}")
async def get_by_id(good_id: str, service: GoodsService = Depends()):
    good = await service.get_by_id(good_id)
    if good is None:
        raise HTTPException(
            detail="Good with provided id can not be found", status_code=404
        )
    return good


@router.post("/create")
async def create(data: CreateGoodSchema, service: GoodsService = Depends()):
    return await service.create(data)


@router.get("/variation/{variation_id}")
async def get_variation_by_id(variation_id: str, service: GoodsService = Depends()):
    variation = await service.get_variation_by_id(variation_id)
    if variation is None:
        raise HTTPException(
            detail="Good variation with provided id can not be found", status_code=404
        )
    return variation


@router.post("/variation/{variation_id}")
async def create_variation(
    variation_id: str, data: CreateGoodSchema, service: GoodsService = Depends()
):
    return await service.create_variation(variation_id, data)


@router.post("/variation/{variation_id}/upload-photo")
async def upload_variation_photo(
    variation_id: str, file: UploadFile = File(...), service: GoodsService = Depends()
):
    if file.content_type not in ["image/jpeg", "image/png"]:
        raise HTTPException(detail="File must be an image", status_code=400)

    try:
        variation = await service.upload_photos(variation_id, file)
    except ValueError:
        raise HTTPException(
            detail="Good variation with provided id can not be found", status_code=404
        )
    return variation
