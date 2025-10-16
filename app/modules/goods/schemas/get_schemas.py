import typing as tp
from fastapi import Query
from pydantic import BaseModel


class GetGoodsSchema(BaseModel):
    id: tp.Optional[str] = Query(None)
    page: tp.Optional[int] = Query(1, ge=1)
    size: tp.Optional[int] = Query(10, le=100)
    show_hidden: tp.Optional[bool] = Query(False)
