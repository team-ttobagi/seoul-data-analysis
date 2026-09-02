from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse


class AppException(HTTPException):
    def __init__(self, code: str, message: str, status_code: int = 400):
        super().__init__(status_code=status_code, detail=message)
        self.code = code
        self.message = message


class TradeAreaNotFoundException(AppException):
    def __init__(self, trade_area_code: str):
        super().__init__(
            code="TRADE_AREA_NOT_FOUND",
            message=f"Trade area with code '{trade_area_code}' was not found.",
            status_code=404,
        )


class IndustryNotFoundException(AppException):
    def __init__(self, industry_code: str):
        super().__init__(
            code="INDUSTRY_NOT_FOUND",
            message=f"Industry with code '{industry_code}' was not found.",
            status_code=404,
        )


async def app_exception_handler(request: Request, exc: AppException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": {"code": exc.code, "message": exc.message}},
    )


async def generic_http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": "HTTP_ERROR",
                "message": str(exc.detail),
            }
        },
    )
