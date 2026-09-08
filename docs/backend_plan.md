# Analytics 도메인 Mock 제거 구현 계획

- **문서명**: Analytics 도메인 Mock 제거 구현 계획
- **목적**: `상권 분석 지표 산출 정의서.md`의 산식을 적용해 `analytics` 도메인에 남아있는 하드코딩 Mock 데이터를 실제 Supabase 계산값으로 전환한다.
- **작성 배경**: 이슈 #6/#7/#9 작업(Supabase 연결, Repository 실데이터 전환, FK 검증)은 완료됨. `trade_area`/`industry`/`sales` Repository는 실제 데이터를 반환하지만, `analytics/service.py`의 추천·순위·비교·경쟁도 로직은 여전히 고정값을 사용 중.
- **문서 상태**: Draft — PM 컨펌 대기
- **참고 문서**: [상권 분석 지표 산출 정의서](./상권%20분석%20지표%20산출%20정의서.md)

---

## 1. 현재 상태 — 남아있는 Mock 목록

| 위치 | 함수 | 문제 |
| --- | --- | --- |
| `backend/app/domain/analytics/service.py` | `get_recommendations()` | 추천 상권 5곳(성수동/홍대/샤로수길/건대/강남역)의 성장률·거래량·경쟁도가 전부 고정값 |
| 〃 | `get_overview()`의 `rankings` | `by_sales`/`by_volume`/`by_growth`/`by_score` 4개 순위표가 고정. `GAROSU`, `EULJIRO`는 실제 DB에 없는 코드 |
| 〃 | `get_overview()`의 `takeaway.score` | `"SEONGSU"`/`"HONGDAE"` 문자열 비교(실제 코드는 숫자라 매치 안 됨) + 82/78/74 고정값 |
| 〃 | `get_overview()`의 `industry_name` | 항상 `"커피·음료"`로 고정 |
| 〃 | `get_compare()` | 비교 상권 5곳의 모든 필드가 완전 고정 딕셔너리 |
| 〃 | `get_overview()` / `get_competition()`의 경쟁도 필드 | 점포 수 데이터가 없어 현재 `null` 처리 중 — 산출 정의서의 `CompetitionScore` Proxy로 대체 가능 |
| `backend/app/domain/sales/repository.py` | `get_sales_by_age_gender()` | "20대 여성 45%"처럼 연령×성별을 결합 표현 — 산출 정의서 10.3에서 금지한 패턴(DB에 연령×성별 교차 데이터 없음) |
| `backend/app/domain/district/repository.py` | `get_all()` | DB 조회 실패 시 서울 8개 구만 반환하는 in-memory fallback (팀원 작성분, 범위 외로 별도 확인 필요) |

---

## 2. 목표

산출 정의서의 산식을 그대로 적용해 위 Mock을 실제 `sales_data` 집계로 교체한다.

- 모든 파생 지표(GrowthScore, TransactionScore, CompetitionScore, ExplorationScore, 순위, percentile)는 **동일 분기 + 동일 업종** 집단 내에서 계산 (산출 정의서 2.3)
- 동일 지표는 KPI / Why Explore / Ranking / Compare / Exploration Score 어디서든 **한 번 계산한 값을 재사용** (산출 정의서 13장 원칙)
- 점포 수가 없는 한계는 유지하되, 경쟁도는 `CompetitionScore` Proxy(객단가 50% + 성장균형 30% + 수요다양성 20%)로 간접 추정하고 그 사실을 명시
- 연령×성별 교차처럼 원천적으로 불가능한 지표는 결합 표현하지 않는다 (`20대 (45%)` + `여성 61%` 형태로 분리)

---

## 3. 단계별 구현 계획

### 3.1 공통 지표 집계 계층 (선행 작업)

`sales/repository.py`에 신규 메서드 추가:

```
get_metrics(quarter: str, industry_code: str) -> list[dict]
```

- 동일 분기+업종의 서울 전체 상권에 대해 SQL 한 번으로 집계:
  - `sales`, `transaction_count` (당기)
  - `previous_sales`, `previous_transaction_count` (직전 분기, self-join)
  - `growth_rate`, `transaction_growth`, `avg_ticket`, `growth_pressure`
- HHI(수요 다양성) 계산용 별도 쿼리:
  - 업종 필터 없이 **상권 단위 전체 업종 매출 비중**을 집계해야 하므로 위 쿼리와 분리
- 1,596개 상권 × 63개 업종 조합을 매 요청마다 스캔하는 비용은 3.3절에서 별도 검증

### 3.2 순수 계산 함수 분리

신규 모듈 `backend/app/domain/analytics/scoring.py`:

| 함수 | 산식 근거 |
| --- | --- |
| `growth_score()` | 산출 정의서 4.4 — P5~P95 Winsorize 후 Min-Max |
| `transaction_score()` | 4.5 — log1p 변환 후 Min-Max |
| `ticket_score()` | 4.6.1 |
| `growth_balance_score()` | 4.6.2 |
| `demand_diversity_score()` | 4.6.3 (HHI 기반) |
| `competition_score()` | 4.6 — 위 3개 가중합 (0.50/0.30/0.20) |
| `exploration_score()` | 4.7 — Growth/Transaction/Competition 가중합 (0.40/0.35/0.25) |
| `percentile_and_rank()` | 5장 — 동일 분기·업종 집단 내 순위/percentile |
| `seoul_rank()` | 5.5 — 4개 Benchmark Percentile 평균 기반 종합 순위 |

DB 세션에 의존하지 않는 순수 함수로 작성해 단위 테스트 가능하도록 분리.

### 3.3 의존성 결정 필요 — pandas 도입 여부

산출 정의서 12장의 참고 구현은 pandas 기반. 현재 백엔드에는 pandas가 없음.

- **옵션 A**: SQL 윈도우 함수(`RANK()`, `PERCENT_RANK()`)로 순위/percentile 처리, HHI·Winsorize는 Python 순수 코드로 구현
- **옵션 B**: pandas/numpy 의존성 추가, 산출 정의서 예시 코드를 거의 그대로 이식

→ PM/팀 논의 필요. 이 문서에서는 **옵션 A(무의존성)** 를 기본값으로 제안 (배포 환경 단순화, 이미 asyncpg 기반 쿼리 스타일과 일관).

### 3.4 엔드포인트 교체 순서

1. **`get_overview()`** — KPI는 이미 실계산 중이므로:
   - `competition_level`/`sales_level`/`volume_level`을 `CompetitionScore` 기반으로 채움
   - `rankings`를 실제 상권 순위(`get_metrics` 결과 기반)로 교체
   - `industry_name`을 기존 `IndustryRepository.get_by_code()` 조회로 교체
2. **`get_competition()`** — `CompetitionScore` 및 하위 요소(TicketScore/GrowthBalanceScore/DemandDiversityScore) 노출
3. **`get_compare()`** — 요청받은 상권 코드 목록에 대해 위 지표 실계산
4. **`get_recommendations()`** — 서울 전체 상권 대상 `ExplorationScore` 계산 후 상위 N개 추출 (가장 연산 비용이 큰 엔드포인트라 마지막 순서)

### 3.5 소비 패턴 수정

`sales/repository.py get_sales_by_age_gender()`:
- 현재: 전체 성별 비율을 모든 연령대에 동일하게 복제해 "20대 여성" 식으로 표현
- 변경: `age_group`별 비중과 전체 `dominant_gender`/`female_ratio`/`male_ratio`를 분리된 필드로 응답 (산출 정의서 6.7, 10.3)
- 프론트엔드 표시 방식에 영향 있으므로 API 필드 변경 범위를 프론트와 사전 조율 필요

---

## 4. PM 컨펌이 필요한 결정 사항

1. **범위**: 4단계(추천/순위/비교/경쟁도) 전부 이번 작업에 포함할지, 혹은 Overview/Compare만 우선 처리하고 추천(`get_recommendations`)은 별도 이슈로 분리할지
2. **pandas 도입 여부** (3.3절): 무의존성 SQL 방식 vs pandas 기반 방식
3. **API 응답 필드 변경**:
   - `competition_level` 등 문자열 등급("높음"/"보통")을 유지할지, 산출 정의서 권장대로 점수 위주로 노출 방식을 바꿀지
   - `sales_by_age_gender` 응답에서 연령×성별 결합 표현을 제거하는 것에 대한 프론트 영향 검토
4. **성능 기준**: 매 요청마다 1,596개 상권 전체를 스캔해 점수를 계산하는 방식이 초기 MVP에서 허용 가능한 응답 속도인지, 아니면 산출 정의서 15장의 `mv_trade_area_scores`(구체화 뷰) 도입을 앞당길지

---

## 5. 범위 외 — 별도 확인 필요

- `district/repository.py`의 in-memory fallback (서울 8개 구 하드코딩) — 팀원 작성 코드, 이번 작업과 무관하게 별도 확인 권장
- `trade_area`, `industry`, `sales` 기본 CRUD Repository는 이미 실데이터 전환 완료 (이슈 #6/#7/#9), 이번 계획의 대상 아님
