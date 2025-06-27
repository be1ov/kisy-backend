from fastapi import APIRouter

router = APIRouter()

@router.get("/methods")
def get_delivery_methods():
    pass