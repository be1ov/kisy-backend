from fastapi import FastAPI
from fastapi_login import LoginManager
from sqladmin import Admin, ModelView, expose, BaseView
from sqlalchemy import select
from starlette.responses import RedirectResponse
from starlette.templating import Jinja2Templates

from starlette.staticfiles import StaticFiles
from starlette.requests import Request

from app.core.config import settings
from app.core.db.session import Base, engine, get_session, AsyncSessionLocal
from app.modules.cart.entities import GoodsInCart
from app.modules.goods.entities import GoodEntity, GoodVariationEntity, GoodVariationPhotoEntity
from app.modules.orders.entities import OrderEntity, OrderDetailsEntity
from app.modules.prices.entities import GoodVariationPriceEntity

from app.modules.users import router as users
from app.modules.auth import router as auth
from app.modules.goods import router as goods
from app.modules.prices import router as prices
from app.modules.cart import router as cart
from app.modules.orders import router as orders
from app.modules.delivery import router as delivery
from app.modules.payments import router as payments
from app.modules.integrations.payments import router as integrations_payments
from app.modules.admin_handlers import router as admin_handlers

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

app.mount("/api/static", StaticFiles(directory="static"), name="static")

app.include_router(users.router, prefix="/api/v1/users", tags=["Users"])
app.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(goods.router, prefix="/api/v1/goods", tags=["Goods"])
app.include_router(prices.router, prefix="/api/v1/prices", tags=["Prices"])
app.include_router(cart.router, prefix="/api/v1/cart", tags=["Cart"])
app.include_router(orders.router, prefix="/api/v1/orders", tags=["Orders"])
app.include_router(delivery.router, prefix="/api/v1/delivery", tags=["Delivery"])
app.include_router(payments.router, prefix="/api/v1/payments", tags=["Payments"])
app.include_router(integrations_payments.router, prefix="/api/v1", tags=["Integrations"])
app.include_router(admin_handlers.router, prefix="/api/v1/admin_routers", tags=["admin_routers"])


async def init_db():
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)


@app.on_event("startup")
async def startup():
    # await init_db()
    pass

class UserAdmin(ModelView, model=UserEntity):
    name_plural = "Пользователи"

    column_list = [UserEntity.telegram_id, UserEntity.username, UserEntity.first_name, UserEntity.last_name, UserEntity.birth_date]
    column_details_list = [UserEntity.telegram_id, UserEntity.username, UserEntity.first_name, UserEntity.last_name, UserEntity.birth_date]
    column_searchable_list = [UserEntity.telegram_id, UserEntity.username, UserEntity.first_name, UserEntity.last_name, UserEntity.birth_date]
    column_sortable_list = [UserEntity.telegram_id, UserEntity.username, UserEntity.first_name, UserEntity.last_name, UserEntity.birth_date]


class GoodsAdmin(ModelView, model=GoodEntity):
    name_plural = "Товары"

    column_list = [GoodEntity.title]
    column_details_list = [GoodEntity.title]
    column_searchable_list = [GoodEntity.title]
    column_sortable_list = [GoodEntity.title]

    # column_exclude_list = [GoodEntity.vat_rate]


class GoodsVariationAdmin(ModelView, model=GoodVariationEntity):
    name_plural = "Вариации товаров"
    
    column_list = [GoodVariationEntity.title, GoodVariationEntity.latest_price]
    column_details_list = [GoodVariationEntity.title, GoodVariationEntity.latest_price]
    column_searchable_list = [GoodVariationEntity.title, GoodVariationEntity.latest_price]
    column_sortable_list = [GoodVariationEntity.title, GoodVariationEntity.latest_price]


class GoodVariationPhotoEntityAdmin(ModelView, model=GoodVariationPhotoEntity):
    name_plural = "Фотографии"

    column_list = [
        GoodVariationPhotoEntity.id,
        "variation_title",
        GoodVariationPhotoEntity.is_main,
    ]
    column_details_list = column_list
    column_searchable_list = column_list
    column_sortable_list = [GoodVariationPhotoEntity.id, "variation_title"]

    def variation_title(self, obj):
        return obj.variation.title if obj.variation else None


class ExportView(BaseView):
    name = "Экспорт заказов"
    icon = "fa-solid fa-file-excel"

    @expose("/export-admin", methods=["GET"])
    async def export_page(self, request):
        return await self.templates.TemplateResponse(
            request=request,
            name="export1.html"
            # context={"title": "Экспорт в Excel"}
        )

class MessageView(BaseView):
    name = "Рассылка сообщений"
    icon = "fa-solid fa-file-excel"

    @expose("/messages", methods=["GET"])
    async def messages(self, request):
        return await self.templates.TemplateResponse(
            request=request,
            name="message.html"
            # context={"title": "Экспорт в Excel"}
        )

##Админка
manager = LoginManager(settings.SECRET_KEY, token_url="/auth/login", use_cookie=True)
manager.cookie_name = "auth_token"

templates = Jinja2Templates(directory=settings.TEMPLATES)

@manager.user_loader()
async def load_user(phone: str):
    async with AsyncSessionLocal() as db:
        stmt = select(UserEntity).where(UserEntity.phone == phone)
        result = await db.execute(stmt)
        return result.scalar()

from sqladmin.authentication import AuthenticationBackend
from starlette.requests import Request

from jose import JWTError, jwt

def verify_token(token: str) -> bool:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        phone: str = payload.get("sub")
        if phone is None:
            return False
        return True
    except JWTError:
        return False

class CustomAuthBackend(AuthenticationBackend):
    async def authenticate(self, request: Request) -> bool:
        token = request.cookies.get(manager.cookie_name)
        if not token:
            return False
        return verify_token(token)

    async def login(self, request: Request) -> bool:
        form = await request.form()
        phone = form.get("username")
        password = form.get("password")

        user = await load_user(phone)
        print(user)
        if not user or password != phone[::-1]:
            return False

        if not user.is_admin:
            return False

        access_token = manager.create_access_token(data={"sub": phone})
        response = RedirectResponse(url="/admin", status_code=302)
        manager.set_cookie(response, access_token)
        await response(scope=request.scope, receive=request.receive, send=request._send)

        return True

    async def logout(self, request: Request) -> None:
        # можно очистить куку, если хочешь
        pass

auth_backend = CustomAuthBackend(settings.SECRET_KEY)

admin = Admin(app, engine, templates_dir=settings.TEMPLATES, authentication_backend=auth_backend)

admin.title = "KISY Shop Admin"

admin.add_view(UserAdmin)
admin.add_view(GoodsAdmin)
admin.add_view(GoodsVariationAdmin)
admin.add_view(GoodVariationPhotoEntityAdmin)
admin.add_view(ExportView)
admin.add_view(MessageView)

# admin.add_view(OrdersExcelAdmin)
