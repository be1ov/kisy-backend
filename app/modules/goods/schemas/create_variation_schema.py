from app.modules.goods.schemas.create import CreateGoodSchema


class CreateVariationSchema(CreateGoodSchema):
    width: float | None = None
    height: float | None = None
    length: float | None = None
    weight: float | None = None
