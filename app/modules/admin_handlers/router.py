from datetime import datetime
from typing import Annotated, Optional

from fastapi import APIRouter, Depends, HTTPException, Body, Query, File, Form, UploadFile
from fastapi.responses import StreamingResponse, JSONResponse

from app.modules.admin_handlers.service import ExcelService, SendingMessages

router = APIRouter()

@router.get("/get_excel_orders")
async def get_excel_orders(start_date: Optional[datetime] = Query(None, description="Start date in YYYY-MM-DD format"),
    end_date: Optional[datetime] = Query(None, description="End date in YYYY-MM-DD format"),
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

@router.post("/send_messages", response_model=None)
async def send_messages(photo: UploadFile = File(...), caption: str = Form(...), service: SendingMessages = Depends()):
    try:
        file_url: str = ""
        print('handler')
        print(photo)
        if photo:
            file_url  = await service.save_uploaded_file(photo)

        await service.send_message(file_url, caption)
        return JSONResponse(
            status_code=200,
            content={"status": "success"}
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))