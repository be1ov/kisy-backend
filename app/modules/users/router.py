from fastapi import APIRouter

router = APIRouter()

# @router.get("/")
# async def get_all(service: UserService = Depends()):
#     return await service.get_all()

# @router.post("/create")
# async def create_user(data: CreateUserSchema, service: UserService = Depends()):
#     return await service.signup(data)