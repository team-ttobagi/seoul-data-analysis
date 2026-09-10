# SPOT LADER (스팟 레이더)

> **서울시 상권분석 오픈데이터를 기반으로 예비 창업자가 원하는 업종의 유망 상권과 소비 패턴을 직관적으로 탐색할 수 있는 데이터 저널리즘 스타일의 풀스택 상권 분석 서비스**

- 기획: https://chatgpt.com/share/6a97ca24-5b58-83ee-ae73-3d98534e55c5

---

## 📸 Overview & Design Philosophy

SEOUL DATA PLAYGROUND는 데이터 저널리즘 에디토리얼 스타일(Swiss grid, Restrained Neo-brutalism)을 적용하여, 정보의 위계와 가독성을 극대화한 상권 탐색 인터페이스를 제공합니다.

- **색상 시스템**: 따뜻한 오프화이트 캔버스 (`#F8F7F2`), 고대비 블랙 텍스트 (`#121212`), 네온 라임 액센트 (`#CCFF00`), 리스크 경고 레드 (`#FF3B30`)
- **타이포그래피**: 국문 본문 및 제목용 **Pretendard**, 수치 및 메타데이터용 **Space Grotesk** / **JetBrains Mono**
- **그리드 & 레이아웃**: 명확한 1~2px 블랙 구분선, 둥근 모서리 배제, 불필요한 드롭섀도우 지양

---

## 🚀 Key Features & Pages

### 1. 상권 탐색 화면 (`/explore` - Reference 1)
- **상단 필터**: 업종(커피·음료, 한식 등), 지역(서울 전체, 성동구, 마포구 등), 분기(2026 Q2 등) 선택
- **탐색 추천 상권 랭킹**: 서울시 상권 데이터를 기반으로 계산된 **데이터 탐색 점수** 기준 1~5위 추천
- **상권 탐색 이유 (Why Explore)**: 매출 성장성, 거래 활성도, 경쟁 강도 신호 및 세부 퍼센타일 분해
- **주의 요인(Risk Warning)**: 공급 과밀 및 경쟁 경고 안내
- **비교함 담기**: 관심 상권을 체크박스로 선택하여 상권 비교함에 추가

### 2. 상권 상세 분석 화면 (`/district/:tradeAreaCode` - Reference 2)
- **KPI 지표 요약**: 추정 매출(12.8억), 거래 건수(45만), 서울 상권 순위(7위), 전분기 대비 성장률(+8.2%)
- **상권 순위 비교 (어디가 강할까?)**: 매출순, 거래건수순, 성장률순, 탐색점수순 정렬 막대 차트
- **소비 시간대 분석 (언제 가장 많이 팔릴까?)**: 06-11시, 11-14시, 14-17시, 17-21시(피크), 21-24시 매출 분포
- **주요 고객층 분석 (누가 가장 많이 살까?)**: 연령대/성별 소비 비중
- **요일별 매출 분석 (어느 요일이 강할까?)**: 주중 평균 대비 금요일(+21%) 등 피크 요일 시각화
- **경쟁 강도 & 종합 점수 (경쟁은 어떨까? / Overall Insight)**: 경쟁 강도(매우 높음), 종합 탐색 점수(SCORE 82/100) 및 데이터 테이크어웨이

### 3. 상권 다각 비교 분석 (`/compare`)
- 최대 3개 후보 상권을 나란히 배치하여 탐색 점수, 분기 매출, 거래 건수, 성장률, 주요 타겟층, 피크 시간/요일, 경쟁 수준을 매트릭스로 비교

---

## 🛠 Tech Stack & Architecture

### Frontend
- **Framework**: React 18, TypeScript, Vite
- **State Management**: TanStack Query v5 (서버 상태 캐싱), Zustand (비교함 클라이언트 상태)
- **Styling**: Tailwind CSS v4, Lucide React Icons
- **Visualization**: Recharts, Custom High-contrast Data Bars
- **Architecture**: Domain / Feature-oriented 구조 (`src/pages`, `src/shared/ui`, `src/shared/api`, `src/shared/types`)
- **Resilience**: API 서버 미가동 시에도 즉각 동작하는 무중단 Mock 데이터 Fallback 레이어 탑재

### Backend
- **Framework**: Python 3.10+, FastAPI, Pydantic v2, SQLAlchemy 2.x (Async)
- **Architecture**: DDD(Domain-Driven Design) 기반 구조
  - `backend/app/domain/trade_area`: 상권 기본 정보 도메인
  - `backend/app/domain/industry`: 업종 도메인
  - `backend/app/domain/sales`: 매출/거래/시간대/요일/연령 도메인
  - `backend/app/domain/analytics`: 탐색 스코어링 알고리즘 및 추천 엔진
  - `backend/app/domain/district`: 자치구 기본 정보 도메인
- **Testing**: `pytest` 및 `httpx` 기반 서비스 단위 테스트 및 API 스모크 테스트

---

## 🏃‍♂️ Quick Start Guide

### 1. Frontend 실행
```bash
# 의존성 설치
npm install

# 로컬 개발 서버 실행 (포트 3000)
npm run dev
```

### 2. Backend 실행 (선택 사항)
```bash
cd backend

# 가상환경 생성 및 활성화
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# 패키지 설치
pip install -r requirements.txt

# uv
uv sync
uv run uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload

# DB 시드 데이터 초기화
python -m backend.app.seed

# API 서버 실행 (포트 8000)
uvicorn backend.app.main:app --reload --port 8000
```

### 3. Backend 테스트 실행
```bash
cd backend
pytest
```

```bash
uv run --project backend uvicorn backend.app.main:app \
  --host 0.0.0.0 \
  --port 8000 \
  --reload
```

---

## 📊 Exploration Score Algorithm

상권 탐색 점수(Exploration Score)는 예비 창업자가 단순 매출액뿐 아니라 성장성과 진입 리스크를 균형 있게 고려할 수 있도록 가중치를 산정합니다:

$$\text{Score} = 0.40 \times \text{매출성장성 정규화값} + 0.35 \times \text{거래건수 정규화값} + 0.25 \times \text{경쟁완화도 정규화값}$$

---

## 📜 License
Apache-2.0 License. Powered by Seoul Open Data Platform & Google AI Studio.
