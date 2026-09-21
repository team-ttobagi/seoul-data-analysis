from __future__ import annotations

import asyncio
import json
import math
import re
import time
from decimal import Decimal, ROUND_HALF_UP
from typing import Any, SupportsFloat, SupportsIndex

from google import genai
from google.genai import types
from pydantic import ValidationError

from backend.app.domain.analytics.schemas import OverviewInsightContext

from .prompts import SYSTEM_INSTRUCTION, build_overview_input
from .schemas import OverviewTakeawayInsight

_NUMBER = re.compile(r"[+-]?\d+(?:,\d{3})*(?:\.\d+)?")
_AMOUNT_PART_PATTERN = (
    r"[+-]?\d+(?:,\d{3})*(?:\.\d+)?\s*(?:억|만|천|원)"
)
_AMOUNT_EXPRESSION = re.compile(
    rf"(?P<expression>{_AMOUNT_PART_PATTERN}"
    rf"(?:\s*{_AMOUNT_PART_PATTERN})*)(?:\s*원)?"
)
_AMOUNT_PART = re.compile(
    r"(?P<number>[+-]?\d+(?:,\d{3})*(?:\.\d+)?)\s*"
    r"(?P<unit>억|만|천|원)"
)
_AMOUNT_MULTIPLIERS = {
    "억": Decimal("100000000"),
    "만": Decimal("10000"),
    "천": Decimal("1000"),
    "원": Decimal("1"),
}
_AMOUNT_FIELDS = (
    "current_sales",
    "previous_sales",
    "sales_change_amount",
    "sales_per_transaction_current",
    "sales_per_transaction_previous",
)
_FORBIDDEN_INTERNAL_MESSAGES = re.compile(
    r"원천\s*(?:집계|데이터|값)\s*(?:확인|검토)|"
    r"데이터\s*품질\s*(?:검토|확인)|"
    r"극단적\s*변동\s*(?:경고|주의)|"
    r"신중한\s*검토|"
    r"현장\s*(?:확인|방문)|"
    r"확인\s*권고",
)
_FORBIDDEN_CAUSAL_EXPRESSIONS = re.compile(
    r"견인|이끌(?:다|어|며|고|었|ㄴ)|직결|때문|덕분|주요\s*요인",
)
_PERCENT_FIELDS = (
    "qoq_growth_rate",
    "transaction_qoq_rate",
    "sales_per_transaction_qoq_rate",
    "transactions_per_store_qoq_rate",
    "closing_rate",
    "opening_rate",
    "franchise_ratio_percent",
)
_COUNT_FIELDS = (
    "transaction_count",
    "previous_transaction_count",
    "transaction_change_count",
    "transactions_per_store_current",
    "transactions_per_store_previous",
    "store_count",
    "previous_store_count",
    "store_count_change",
)
_CATEGORY_LABEL_FIELDS = {
    "성장성": "growth_level",
    "거래 활성도": "transaction_level",
    "경쟁 여건": "competition_level",
}
_CATEGORY_MENTION = re.compile(
    r"(?P<label>성장성|거래 활성도|경쟁 여건)(?P<tail>[^.!?。！？\n]{0,30})"
)
_PERIOD_LITERAL = re.compile(r"(?<!\d)\d{4}\s*(?:[Qq]\s*\d+|년\s*\d+\s*분기)(?!\d)")
_CATEGORY_VALUE = re.compile(
    r"높(?:음|은\s*(?:편|수준)|고|지만|으며|습니다|다)"
    r"|보통"
    r"|낮(?:음|은\s*(?:편|수준)|고|지만|으며|습니다|다)"
    r"|좋(?:음|은\s*(?:편|수준)|고|지만|으며|습니다|다)"
    r"|나쁨|나쁜\s*(?:편|수준)|나쁘(?:고|지만|며|습니다|다)"
    r"|비교적\s*유리(?:한|하다|합니다)?"
    r"|비교적\s*불리(?:한|하다|합니다)?"
)


class GeminiInsightError(RuntimeError):
    """Gemini 어댑터 경계에서 노출하는 기본 오류."""


class GeminiInsightRequestError(GeminiInsightError):
    """Interactions API 요청이 실패한 경우의 오류."""


class GeminiInsightResponseError(GeminiInsightError):
    """Gemini가 누락되었거나 잘못되었거나 근거가 없는 출력을 반환한 경우의 오류."""


class GeminiInsightClientClosedError(GeminiInsightError):
    """비동기 클라이언트를 닫은 뒤 어댑터를 사용한 경우의 오류."""


def _load_context(prompt: str) -> dict[str, Any]:
    try:
        payload = json.loads(prompt)
        context = payload["context"]
    except (TypeError, KeyError, json.JSONDecodeError) as exc:
        raise GeminiInsightResponseError(
            "Gemini 요약 근거 검증용 입력이 올바르지 않습니다."
        ) from exc
    if not isinstance(context, dict):
        raise GeminiInsightResponseError(
            "Gemini 요약 근거 검증용 입력이 올바르지 않습니다."
        )
    return context


def _category_value_level(value: str, field: str) -> str | None:
    normalized = value.replace(" ", "")
    if field == "competition_level":
        if normalized.startswith("좋") or "유리" in normalized:
            return "좋음"
        if normalized == "보통":
            return "보통"
        if normalized == "나쁨" or normalized.startswith("나쁘") or "불리" in normalized:
            return "나쁨"
        return None
    if "유리" in normalized:
        return None
    if "불리" in normalized:
        return None
    if normalized.startswith("높"):
        return "높음"
    if normalized == "보통":
        return "보통"
    if normalized.startswith("낮"):
        return "낮음"
    return None


def _validate_category_grounding(summary: str, context: dict[str, Any]) -> None:
    """성장성·거래 활성도·경쟁 여건 등급이 입력 등급과 일치하는지 검증한다."""
    for label_match in _CATEGORY_MENTION.finditer(summary):
        label = label_match.group("label")
        field = _CATEGORY_LABEL_FIELDS[label]
        value_match = _CATEGORY_VALUE.search(label_match.group("tail"))
        if value_match is None:
            continue
        actual = _category_value_level(value_match.group(), field)
        expected = context.get(field)
        if actual is None or expected is None or actual != expected:
            raise GeminiInsightResponseError(
                f"범주 등급이 입력값과 일치하지 않습니다: label={label!r}, "
                f"field={field!r}, actual={actual!r}, expected={expected!r}, "
                f"summary={summary!r}"
            )


def _normalize_number(token: str) -> str:
    return token.replace(",", "").lstrip("+")


def _numeric_tokens(value: object) -> set[str]:
    """숫자의 원본·반올림·절댓값 표현을 whitelist에 추가한다."""
    if value is None or isinstance(value, bool):
        return set()

    # ``object``는 float()에 전달 가능한 타입이라는 보장이 없으므로,
    # Python의 float 변환 계약에 해당하는 타입으로 먼저 좁힌다.
    if not isinstance(
        value,
        (str, bytes, bytearray, SupportsFloat, SupportsIndex),
    ):
        return set()

    try:
        number = float(value)
    except (TypeError, ValueError, OverflowError):
        return set()

    if not math.isfinite(number):
        return set()

    absolute = abs(number)
    truncated_one_decimal = math.trunc(absolute * 10) / 10
    truncated_two_decimals = math.trunc(absolute * 100) / 100

    return {
        # 원래 값
        _normalize_number(str(value)),
        # 자연어에서 소수점을 버린 정수 표현
        str(int(absolute)),
        f"{number:.0f}",
        f"{number:.1f}",
        f"{number:.2f}",
        # 자연어의 "N% 감소", "N개 감소" 표현 허용
        _normalize_number(str(absolute)),
        f"{absolute:.0f}",
        f"{absolute:.1f}",
        f"{absolute:.2f}",
        # 자연어에서 소수점을 버린 절삭 표현
        f"{truncated_one_decimal:.1f}",
        f"{truncated_two_decimals:.2f}",
    }


def _build_numeric_whitelist(context: dict[str, Any]) -> set[str]:
    """정해진 표시 단위와 반올림 기준으로 허용할 숫자를 만든다."""
    whitelist: set[str] = set()
    for field in _PERCENT_FIELDS:
        number = _as_numeric(context.get(field))
        if number is None:
            continue
        rounded = _format_half_up(abs(number), 1)
        whitelist.add(rounded)
        if rounded.endswith(".0"):
            whitelist.add(rounded[:-2])
        if number < 0:
            whitelist.add(f"-{rounded}")
            if rounded.endswith(".0"):
                whitelist.add(f"-{rounded[:-2]}")
    for field in _COUNT_FIELDS:
        number = _as_numeric(context.get(field))
        if number is None:
            continue
        rounded = str(int(abs(number)))
        whitelist.add(rounded)
        if number < 0:
            whitelist.add(f"-{rounded}")
    for field in ("tag_candidates",):
        value = context.get(field)
        if isinstance(value, list):
            values = value
        else:
            values = [value]
        for item in values:
            if not isinstance(item, str):
                continue
            for token in _NUMBER.findall(item):
                normalized = _normalize_number(token)
                whitelist.add(normalized)
                whitelist.add(normalized.lstrip("-"))
    return whitelist


def _as_numeric(value: object) -> float | None:
    if value is None or isinstance(value, bool):
        return None
    if not isinstance(
        value,
        (str, bytes, bytearray, SupportsFloat, SupportsIndex),
    ):
        return None
    try:
        number = float(value)
    except (TypeError, ValueError, OverflowError):
        return None
    return number if math.isfinite(number) else None


def _format_half_up(value: float, decimal_places: int) -> str:
    quantum = Decimal("1").scaleb(-decimal_places)
    rounded = Decimal(str(value)).quantize(quantum, rounding=ROUND_HALF_UP)
    return f"{rounded:.{decimal_places}f}"


def _parse_amount_expression(expression: str) -> tuple[Decimal, Decimal]:
    """금액 표현의 실제 값과 가장 작은 표시 단위를 계산한다."""
    total = Decimal("0")
    precision: Decimal | None = None
    for part in _AMOUNT_PART.finditer(expression):
        number = Decimal(_normalize_number(part.group("number")))
        multiplier = _AMOUNT_MULTIPLIERS[part.group("unit")]
        total += number * multiplier
        decimal_places = max(0, -number.as_tuple().exponent)
        part_precision = multiplier / (Decimal("10") ** decimal_places)
        precision = (
            part_precision
            if precision is None
            else min(precision, part_precision)
        )
    if precision is None:
        raise ValueError(f"금액 표현을 해석할 수 없습니다: {expression!r}")
    return total, precision


def _amount_matches_source(
    displayed_amount: Decimal,
    display_precision: Decimal,
    source: float,
) -> bool:
    source_amount = Decimal(str(abs(source)))
    rounded_source = (
        (source_amount / display_precision)
        .quantize(Decimal("1"), rounding=ROUND_HALF_UP)
        * display_precision
    )
    return abs(displayed_amount) == rounded_source


def _validate_amount_grounding(
    summary: str, context: dict[str, Any]
) -> list[tuple[int, int]]:
    """한국어 금액 표현을 해석해 입력 금액과 반올림 기준을 검증한다."""
    amount_spans: list[tuple[int, int]] = []
    for match in _AMOUNT_EXPRESSION.finditer(summary):
        expression = match.group("expression")
        displayed_amount, display_precision = _parse_amount_expression(expression)
        if not any(
            _amount_matches_source(displayed_amount, display_precision, source)
            for field in _AMOUNT_FIELDS
            if (source := _as_numeric(context.get(field))) is not None
        ):
            raise GeminiInsightResponseError(
                "금액 근거 검증에 실패했습니다: "
                f"expression={expression!r}, summary={summary!r}"
            )
        amount_spans.append(match.span())
    return amount_spans


def _validate_tag_grounding(summary: str, context: dict[str, Any]) -> None:
    """문장 앞 태그가 백엔드 허용 후보에만 포함되는지 확인한다."""
    candidates = {
        candidate.strip()
        for candidate in context.get("tag_candidates", [])
        if isinstance(candidate, str) and candidate.strip()
    }
    tag_matches = list(re.finditer(r"\[[^\]\n]+\]", summary))
    if not tag_matches:
        if "[" in summary or "]" in summary:
            raise GeminiInsightResponseError(
                "summary의 소비 패턴 태그 형식이 올바르지 않습니다."
            )
        return
    if len(tag_matches) != 1 or tag_matches[0].start() != 0:
        raise GeminiInsightResponseError(
            "summary에는 문장 앞 소비 패턴 태그 하나만 사용할 수 있습니다."
        )
    match = tag_matches[0]
    if match.end() >= len(summary) or summary[match.end()] != " ":
        raise GeminiInsightResponseError(
            "소비 패턴 태그와 본문 사이에는 공백 한 칸이 필요합니다."
        )
    if not candidates:
        raise GeminiInsightResponseError(
            "백엔드가 허용한 소비 패턴 후보가 없는데 태그가 생성되었습니다."
        )
    raw_parts = match.group()[1:-1].split("·")
    if not 1 <= len(raw_parts) <= 3:
        raise GeminiInsightResponseError(
            "소비 패턴 태그는 최대 3개 항목만 포함할 수 있습니다."
        )
    for part in raw_parts:
        normalized = re.sub(r"\s*중심$", "", part.strip())
        if normalized not in candidates:
            raise GeminiInsightResponseError(
                f"허용되지 않은 소비 패턴 태그입니다: {normalized!r}"
            )


def _numeric_grounding_error(
    *, token: str, whitelist: set[str], summary: str
) -> GeminiInsightResponseError:
    return GeminiInsightResponseError(
        f"숫자 근거 검증에 실패했습니다(whitelist): token={token!r}, "
        f"허용 숫자={sorted(whitelist)!r}, summary={summary!r}"
    )


def _validate_numeric_whitelist(summary: str, context: dict[str, Any]) -> None:
    """요약의 숫자가 입력 컨텍스트의 허용 숫자 목록에 포함되는지 확인한다."""
    whitelist = _build_numeric_whitelist(context)
    amount_spans = _validate_amount_grounding(summary, context)
    period_spans = [match.span() for match in _PERIOD_LITERAL.finditer(summary)]
    for number in _NUMBER.finditer(summary):
        if any(
            number.start() >= start and number.end() <= end
            for start, end in amount_spans
        ):
            # 금액 표현은 이미 단위 조합 전체를 환산해 검증했다.
            continue
        if any(
            number.start() >= start and number.end() <= end
            for start, end in period_spans
        ):
            # 분기는 일치 여부를 검증하지 않고, 지표 숫자 whitelist 대상에서만 제외한다.
            continue
        token = number.group()
        if _normalize_number(token) not in whitelist:
            raise _numeric_grounding_error(
                token=token,
                whitelist=whitelist,
                summary=summary,
            )


def _ensure_grounding(summary: str, prompt: str) -> None:
    """허용 태그·핵심 3등급·숫자 whitelist를 함께 검증한다."""
    if _FORBIDDEN_INTERNAL_MESSAGES.search(summary):
        raise GeminiInsightResponseError(
            "summary에 내부 검토용 메시지가 포함되어 있습니다."
        )
    if _FORBIDDEN_CAUSAL_EXPRESSIONS.search(summary):
        raise GeminiInsightResponseError(
            "summary에 근거 없는 인과 표현이 포함되어 있습니다."
        )
    context = _load_context(prompt)
    _validate_tag_grounding(summary, context)
    _validate_category_grounding(summary, context)
    _validate_numeric_whitelist(summary, context)


class GeminiInsightGenerator:
    """종합 인사이트 문장을 위한 비동기 Google Gen AI Interactions 어댑터."""

    def __init__(
        self,
        *,
        api_key: str,
        model: str,
        sdk_client: Any | None = None,
        timeout_seconds: float = 2.0,
        max_retries: int = 2,
        max_concurrent_requests: int = 2,
        min_request_interval_seconds: float = 0.0,
    ):
        if not api_key.strip():
            raise ValueError("API 키는 비어 있을 수 없습니다.")
        if not model.strip():
            raise ValueError("모델 이름은 비어 있을 수 없습니다.")
        if timeout_seconds <= 0:
            raise ValueError("제한 시간은 0보다 커야 합니다.")
        if max_retries < 0:
            raise ValueError("재시도 횟수는 음수일 수 없습니다.")
        if max_concurrent_requests < 1:
            raise ValueError("동시 요청 수는 1 이상이어야 합니다.")
        if min_request_interval_seconds < 0:
            raise ValueError("최소 요청 간격은 음수일 수 없습니다.")
        self._model = model.strip()
        self._timeout_seconds = timeout_seconds
        self._max_retries = max_retries
        self._request_slots = asyncio.Semaphore(max_concurrent_requests)
        self._rate_limit_lock = asyncio.Lock()
        self._min_request_interval_seconds = min_request_interval_seconds
        self._last_request_started = 0.0
        self._sdk_client = sdk_client or genai.Client(
            api_key=api_key,
            http_options=types.HttpOptions(
                retry_options=types.HttpRetryOptions(attempts=1),
            ),
        )
        self._async_client = self._sdk_client.aio
        self._closed = False

    async def generate(self, context: OverviewInsightContext) -> str:
        """백엔드의 OverviewInsightGenerator 프로토콜과 호환되는 메서드."""
        if not isinstance(context, OverviewInsightContext):
            raise TypeError("context는 OverviewInsightContext여야 합니다.")
        insight = await self._create_interaction(build_overview_input(context))
        return insight.summary

    async def _create_interaction(self, prompt: str) -> OverviewTakeawayInsight:
        if self._closed:
            raise GeminiInsightClientClosedError(
                "Gemini 비동기 클라이언트가 이미 닫혔습니다."
            )
        request = {
            "model": self._model,
            "input": prompt,
            "system_instruction": SYSTEM_INSTRUCTION,
            "response_format": {
                "type": "text",
                "mime_type": "application/json",
                "schema": OverviewTakeawayInsight.model_json_schema(),
            },
            "generation_config": {"max_output_tokens": 256},
            "store": False,
            # Interactions.create는 초 단위를 받으며, 서비스 수준의
            # asyncio.wait_for 대체 제한 시간과는 별개다.
            "timeout": self._timeout_seconds,
        }
        interaction: object | None = None
        try:
            async with self._request_slots:
                for attempt in range(self._max_retries + 1):
                    try:
                        async with self._rate_limit_lock:
                            wait_for = self._min_request_interval_seconds - (
                                time.monotonic() - self._last_request_started
                            )
                            if wait_for > 0:
                                await asyncio.sleep(wait_for)
                            self._last_request_started = time.monotonic()
                        interaction = await self._async_client.interactions.create(
                            **request
                        )
                        break
                    except Exception:
                        if attempt >= self._max_retries:
                            raise
                        await asyncio.sleep(0.05 * (2**attempt))
        except Exception as exc:
            raise GeminiInsightRequestError(
                "Gemini Interactions API 요청에 실패했습니다."
            ) from exc

        if interaction is None:
            raise GeminiInsightResponseError("Gemini 응답 객체가 없습니다.")
        output_text = getattr(interaction, "output_text", None)
        if not isinstance(output_text, str) or not output_text.strip():
            raise GeminiInsightResponseError("Gemini 응답에 텍스트 출력이 없습니다.")
        try:
            insight = OverviewTakeawayInsight.model_validate_json(output_text)
        except ValidationError as exc:
            validation_errors = "; ".join(
                f"type={error.get('type')}, loc={error.get('loc')}, msg={error.get('msg')}"
                for error in exc.errors()
            )
            raise GeminiInsightResponseError(
                "Gemini 응답의 구조화된 출력이 올바르지 않습니다. "
                f"response_length={len(output_text)}, validation_errors={validation_errors}"
            ) from exc
        _ensure_grounding(insight.summary, prompt)
        return insight

    async def aclose(self) -> None:
        if self._closed:
            return
        self._closed = True
        try:
            await self._async_client.aclose()
        finally:
            close = getattr(self._sdk_client, "close", None)
            if callable(close):
                close()

    async def __aenter__(self) -> "GeminiInsightGenerator":
        if self._closed:
            raise GeminiInsightClientClosedError(
                "Gemini 비동기 클라이언트가 이미 닫혔습니다."
            )
        return self

    async def __aexit__(self, exc_type: Any, exc: Any, traceback: Any) -> None:
        await self.aclose()


GeminiInsightClient = GeminiInsightGenerator
