from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse

from app.modules.admin_handlers.service import ExcelService

router = APIRouter()

@router.get("/get_excel_orders")
async def get_excel_orders(start_date: datetime,
    end_date: datetime,
    service:ExcelService = Depends()):

    try:
        excel_file = await service.create_excel(start_date, end_date)

        return StreamingResponse(
            excel_file,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={
                "Content-Disposition": f"attachment; filename=orders_export_{start_date.date()}_to_{end_date.date()}.xlsx"
            }
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))