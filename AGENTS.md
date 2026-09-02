# AGENTS.md

## Project Overview
**SEOUL DATA PLAYGROUND** is a production-oriented commercial district exploration service for aspiring entrepreneurs in Seoul. Built with an editorial Korean data journalism aesthetic (Swiss grid, restrained neo-brutalism, warm off-white `#F8F7F2`, high-contrast black typography, and `#CCFF00` neon lime accents).

## Monorepo Architecture
- **Frontend**: React 18, TypeScript, Vite, Tailwind CSS, TanStack Query, Zustand, Recharts, Lucide React.
  - Domain-oriented / Feature-Sliced structure: `src/pages`, `src/features`, `src/entities`, `src/shared`.
  - Fallback-safe API layer (`src/shared/api/client.ts` -> `mockData.ts`).
- **Backend**: Python 3.10+, FastAPI, Pydantic v2, SQLAlchemy 2.x.
  - DDD-inspired structure: `backend/app/domain/{trade_area, industry, sales, analytics}`.
  - Deterministic score engine with weights:
    - Sales growth: 0.40
    - Transaction volume: 0.35
    - Competition: 0.25

## Engineering Guidelines for AI Agents
1. **Preserve Editorial Design System**:
   - Maintain the Swiss grid layout with high-contrast borders (`border-black`), minimal border-radius, warm off-white canvas (`#F8F7F2`), and neon lime highlights (`#CCFF00`).
   - Reserve red (`#FF3B30`) strictly for risk warnings and severe competition badges.
2. **Deterministic Data Integrity**:
   - Keep mock and backend API responses identical in shape and naming conventions.
   - All financial and ratio metrics must match official Seoul Open Data definitions.
3. **Clean Architecture**:
   - Keep business logic in services (`service.py` / `src/shared/api`).
   - Keep UI components presentational and modular.
