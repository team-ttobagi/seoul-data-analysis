# Backend Agent Guidelines (SEOUL DATA PLAYGROUND)

## Structure
- `backend/app/main.py`: FastAPI entry point with CORS and routing.
- `backend/app/core/`: Configuration, database engines, and exception handling.
- `backend/app/domain/trade_area/`: Trade area metadata entity and service.
- `backend/app/domain/industry/`: Service industry category entity and service.
- `backend/app/domain/sales/`: Quarterly sales, hourly, weekday, demographic, and store entities.
- `backend/app/domain/analytics/`: Exploration score logic, recommendations, overview, patterns, and compare services.
- `backend/tests/`: Unit tests and endpoint smoke tests.

## Key Rules
- Pydantic v2 schemas for all request/response models.
- Exploration score calculation must remain deterministic:
  `score = round(0.40 * sales_growth + 0.35 * transaction_volume + 0.25 * competition)`
- Error responses follow standard format: `{"error": {"code": "...", "message": "..."}}`.
