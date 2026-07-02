from fastapi import FastAPI, Request, HTTPException, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from datetime import datetime
import time

app = FastAPI()

orders_db = {
    1: {"id": 1, "code": "SP001", "status": "PENDING"},
    2: {"id": 2, "code": "SP002", "status": "DELIVERED"}
}

# --- GLOBAL EXCEPTION HANDLER ---
async def global_exception_handler(request: Request, exc: Exception):
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    message = "Internal Server Error"
    error_detail = str(exc)

    if isinstance(exc, HTTPException):
        status_code = exc.status_code
        message = exc.detail
    elif isinstance(exc, RequestValidationError):
        status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
        message = "Validation Error"
        error_detail = exc.errors()

    return JSONResponse(
        status_code=status_code,
        content={
            "statusCode": status_code,
            "message": message,
            "data": None,
            "error": error_detail,
            "timestamp": datetime.now().isoformat(),
            "path": request.url.path
        }
    )

# Đăng ký các loại lỗi vào Global Handler
app.add_exception_handler(HTTPException, global_exception_handler)
app.add_exception_handler(RequestValidationError, global_exception_handler)
app.add_exception_handler(Exception, global_exception_handler)

# --- API ENDPOINT ---
@app.delete("/orders/{order_id}")
def cancel_order(order_id: int):
    order = orders_db.get(order_id)
    
    # Bẫy 1: Không tồn tại
    if not order:
        raise HTTPException(status_code=404, detail="Đơn hàng không tồn tại")
    
    # Bẫy 2: Trạng thái không hợp lệ
    if order["status"] == "DELIVERED":
        raise HTTPException(status_code=400, detail="Đơn hàng đã giao, không thể hủy")
    
    # Logic hủy
    order["status"] = "CANCELLED"
    
    return {
        "statusCode": 200,
        "message": "Hủy đơn hàng thành công",
        "data": order,
        "error": None,
        "timestamp": datetime.now().isoformat(),
        "path": f"/orders/{order_id}"
    }
