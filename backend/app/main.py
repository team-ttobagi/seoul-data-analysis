from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from backend.app.core.config import settings
from backend.app.core.exceptions import (
    AppException,
    app_exception_handler,
    generic_http_exception_handler,
)
from backend.app.domain.trade_area.router import router as trade_area_router
from backend.app.domain.industry.router import router as industry_router
from backend.app.domain.sales.router import router as sales_router
from backend.app.domain.analytics.router import router as analytics_router
from backend.app.domain.district.router import router as district_router

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="SEOUL DATA PLAYGROUND - Commercial district analytics API for aspiring entrepreneurs in Seoul.",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all for development flexibility
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Exception handlers
app.add_exception_handler(AppException, app_exception_handler)
app.add_exception_handler(HTTPException, generic_http_exception_handler)

# Include Domain API Routers
app.include_router(trade_area_router, prefix=settings.API_V1_STR)
app.include_router(industry_router, prefix=settings.API_V1_STR)
app.include_router(sales_router, prefix=settings.API_V1_STR)
app.include_router(analytics_router, prefix=settings.API_V1_STR)
app.include_router(district_router, prefix=settings.API_V1_STR)


@app.get("/health", tags=["System"])
@app.get(f"{settings.API_V1_STR}/health", tags=["System"])
async def health_check():
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
    }
