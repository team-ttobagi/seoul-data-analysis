from __future__ import annotations

import json

from backend.app.domain.analytics.schemas import OverviewInsightContext

# 변경 이력
# v10 — 2026-09-14: Gemini 프롬프트·외부 출력은 100자로 고정하고,
#                   내부 fallback·응답 경계는 120자까지 허용하는 길이 정책을 주석으로 명시했다.
# v9 — 2026-09-14: 프롬프트 구조 최적화 및 슬림화
#                  행동 금지·인과 추정·결측 처리 등 중복 제약 조건을 팩트 기반 제한 사항으로 통합했다.
#                  장황한 지표 해석 가이드와 반복되는 상대 등급 설명, 불필요한 예시 블록을 쳐내어 토큰 소비를 줄이고 지시 이행력을 높였다.
# v8 — 2026-09-14: 상대 등급의 비교 기준을 사용자 문장 안에서 이해할 수 있도록 명시하고,
#                  qoq_growth_rate와 growth_level의 의미 차이를 구분했다.
#                  즉시 실행 과제 표현을 제거하고 상태 진단형 문체로 통일했다.
# v7 — 2026-09-14: 전분기 대비 점포 수 증감 입력과 grounding 규칙을 추가했다.
# v6 — 2026-09-13: 숫자·범주·분기 grounding 책임 분리와 100자 출력 계약을 반영했다.
# v5 — 2026-09-13: patterns·점포 요약의 최종 파생값과 현황·리스크·실행 과제
#                  구조를 추가했다.
# v4 — 2026-09-13: summary 프롬프트에서 원시 필드·점수 규칙을 제거하고,
#                  최종 지표 입력만 존재한다는 전제와 표현 예시를 명시했다.
# v3 — 2026-09-13: summary 입력을 허용 지표 4개로 제한하고, qoq 부호·결측,
#                  등급의 비교 기준, 경쟁 여건의 의미, 한 문장 카피 규칙을 명시했다.
# v2 — 2026-09-13: 근거 범위, 결측값 처리, 금지 주장, 경쟁 점수 의미와
#                  자연스러운 분석 용어를 명시했다.
# v1 — 기존 프롬프트: 길이·평문·숫자 근거 규칙을 제공했다.


SYSTEM_INSTRUCTION = f"""당신은 데이터 기반 서울 상권 저널리즘 에디터입니다.
입력된 JSON 데이터를 바탕으로 overview insight 응답의 `summary` 필드에 들어갈 상태 서술형 문장을 작성하세요.

[핵심 작성 규칙]

1. 형식 & 길이
- 마크다운, 줄바꿈, 목록 없이 한국어 평문 딱 한 문장(60~90자, 최대 100자)으로 작성하세요.
- 문장 앞에 `[핵심 소비 패턴]` 태그를 붙일 수 있으며, 확인된 값(연령대·요일·시간대) 중 최대 3개만 조합하세요. (예: [30대·금요일·11-14시 중심])
- 흐름: `핵심 소비 패턴 태그 → 주요 변화/특징 → 현재 상태 요약`
- trade_area_name, district_name, industry_name은 분석 문맥을 위한 입력값이며 summary에서 반복하지 마세요.
- 상권명·자치구명·업종명보다 핵심 지표와 해석을 우선하세요.

2. 핵심 지표 선택 및 연결 (2~3개 선택)
- 핵심 지표 2~3개만 선택하고 억지로 모든 지표를 넣지 마세요.
- qoq_growth_rate와 growth_level이 함께 존재할 경우 두 값의 의미 차이(실제 매출 증감률 vs 상대적 성장성)가 드러나도록 우선 연결하세요.
  * 예: "매출은 전분기보다 1.53% 증가했지만 성장성은 동일 업종 서울 상권 대비 낮은 수준입니다."
- transaction_level 또는 competition_level은 특징을 더 잘 설명하는 1개만 선택적으로 추가하세요.

3. 용어 고정 및 비교 기준
- 세 등급(growth, transaction, competition)의 비교 기준은 '동일 분기·동일 업종의 서울 전체 상권'이며, 문장 내 1회만 자연스럽게 명시하면 됩니다.
- 지정된 용어로만 서술하세요:
  * transaction_level → '거래 활성도' (높음/보통/낮음)
  * growth_level → '성장성' (높음/보통/낮음)
  * competition_level → '경쟁 여건' (높음: 비교적 유리 / 보통 / 낮음: 비교적 불리)
- qoq_growth_rate가 양수이면 'N% 증가', 음수이면 절댓값을 사용해 'N% 감소', 0이면 '변동 없음'으로 표현하세요.
- '증가'는 양수, '감소'는 음수 의미를 포함하므로 감소 표현 앞에 음수 부호(-)를 붙이지 마세요.

4. 팩트 기반 제한 사항 (절대 금지)
- 제안·권고·행동 지시 금지 (~하세요, ~점검 필요 등)
- 인과관계 추정 및 미래 예측 금지 (~때문에, ~덕분에, 미래 성과 등)
- 입력데이터에 없는 수치 생성/계산/임의 가공 금지
- 결측값(null)은 원칙적으로 언급 제외 (qoq_growth_rate 예외)
"""


_SUMMARY_CONTEXT_FIELDS = (
    "trade_area_name",
    "district_name",
    "industry_name",
    "quarter",
)
_SUMMARY_PATTERN_FIELDS = (
    "strongest_age_group",
    "peak_slot",
    "peak_day",
)
_SUMMARY_RISK_FIELDS = (
    "closing_rate",
    "opening_rate",
    "franchise_ratio_percent",
    "store_count_change",
    "qoq_growth_rate",
)
_SUMMARY_METRIC_FIELDS = (
    "transaction_level",
    "growth_level",
    "competition_level",
)


def build_overview_input(value: OverviewInsightContext) -> str:
    source = value.model_dump(mode="json")
    context = {
        field: source[field]
        for field in (
            *_SUMMARY_CONTEXT_FIELDS,
            *_SUMMARY_PATTERN_FIELDS,
            *_SUMMARY_RISK_FIELDS,
            *_SUMMARY_METRIC_FIELDS,
        )
    }
    payload = {
        "task": "overview.insight.summary",
        "context": context,
    }
    return json.dumps(
        payload, ensure_ascii=False, allow_nan=False, separators=(",", ":")
    )
