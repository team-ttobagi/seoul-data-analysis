# SEOUL DATA PLAYGROUND Backend

FastAPI backend for the Seoul Data Playground project.

## Overview

This service provides API endpoints for district and trade area lookup, industry evaluation, sales metrics, and analytics scoring.

## Domain responsibilities

- `district`: 자치구 기준 정보와 `GET /api/v1/districts`, `GET /api/v1/districts/{district_code}` 조회 API
- `trade_area`: `district.signgu_cd`를 참조하는 상권 기준 정보와 상권 조회 API
- `sales`: `trade_area`와 `service_industry`를 참조하는 매출 데이터
- `analytics`: district/trade_area/sales 데이터를 조합한 추천·상세·비교 분석

데이터 관계는 `district → trade_area → sales_data`이며, 업종 관계는 `service_industry → sales_data`입니다.

## Development

```bash
uv sync
uv run uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload
```
