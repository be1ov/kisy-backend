from fastapi import FastAPI
from sqladmin import Admin, ModelView

from app.core.db.session import Base, engine
from app.modules.cart.entities import GoodsInCart
from app.modules.goods.entities import GoodEntity, GoodVariationEntity, GoodVariationPhotoEntity
from app.modules.orders.entities import OrderEntity, OrderDetailsEntity
from app.modules.prices.entities import GoodVariationPriceEntity

from app.modules.users import router as users
from app.modules.auth import router as auth
from app.modules.goods import router as goods
from app.modules.prices import router as prices
from app.modules.cart import router as cart

from app.modules.users.entities import UserEntity

_ = [
    UserEntity,
    GoodEntity,
    GoodVariationEntity,
    GoodVariationPhotoEntity,
    GoodVariationPriceEntity,
    GoodsInCart,
    OrderEntity,
    OrderDetailsEntity
]

app = FastAPI(title="KISY Shop Backend", version="1.0.0", contact={
    "Name": "Alex",
    "Telegram": "t.me/be1ov_v"
})

app.include_router(users.router, prefix="/api/v1/users", tags=["Users"])
app.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(goods.router, prefix="/api/v1/goods", tags=["Goods"])
app.include_router(prices.router, prefix="/api/v1/prices", tags=["Prices"])
app.include_router(cart.router, prefix="/api/v1/cart", tags=["Cart"])


async def init_db():
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)


@app.on_event("startup")
async def startup():
    # await init_db()
    pass


admin = Admin(app, engine, templates_dir="app/core/templates/sqladmin/")

admin.title = "KISY Shop Admin"


class UserAdmin(ModelView, model=UserEntity):
    name_plural = "Пользователи"


class GoodsAdmin(ModelView, model=GoodEntity):
    name_plural = "Товары"


class GoodsVariationAdmin(ModelView, model=GoodVariationEntity):
    name_plural = "Вариации товаров"


class GoodVariationPhotoEntityAdmin(ModelView, model=GoodVariationPhotoEntity):
    name_plural = "Фотографии"


class GoodVariationPriceEntityAdmin(ModelView, model=GoodVariationPriceEntity):
    name_plural = "Установка цен"


admin.add_view(UserAdmin)
admin.add_view(GoodsAdmin)
admin.add_view(GoodsVariationAdmin)
admin.add_view(GoodVariationPhotoEntityAdmin)
admin.add_view(GoodVariationPriceEntityAdmin)
