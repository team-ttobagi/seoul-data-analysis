from __future__ import annotations

import asyncio
import json
import math
import re
import time
from typing import Any, SupportsFloat, SupportsIndex

from google import genai
from google.genai import types
from pydantic import ValidationError

from backend.app.domain.analytics.schemas import OverviewInsightContext

from .prompts import SYSTEM_INSTRUCTION, build_overview_input
from .schemas import OverviewTakeawayInsight

_NUMBER = re.compile(r"[+-]?\d+(?:,\d{3})*(?:\.\d+)?")
_NUMERIC_WHITELIST_FIELDS = (
    "qoq_growth_rate",
    "closing_rate",
    "opening_rate",
    "franchise_ratio_percent",
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

    return {
        # 원래 값
        _normalize_number(str(value)),
        f"{number:.0f}",
        f"{number:.1f}",
        f"{number:.2f}",
        # 자연어의 "N% 감소", "N개 감소" 표현 허용
        _normalize_number(str(absolute)),
        f"{absolute:.0f}",
        f"{absolute:.1f}",
        f"{absolute:.2f}",
    }


def _build_numeric_whitelist(context: dict[str, Any]) -> set[str]:
    """입력된 지표와 소비 패턴 라벨에서 허용할 숫자 목록을 만든다."""
    whitelist: set[str] = set()
    for field in _NUMERIC_WHITELIST_FIELDS:
        whitelist.update(_numeric_tokens(context.get(field)))
    for field in ("strongest_age_group", "peak_slot", "peak_day"):
        value = context.get(field)
        if isinstance(value, str):
            for token in _NUMBER.findall(value):
                normalized = _normalize_number(token)
                whitelist.add(normalized)
                whitelist.add(normalized.lstrip("-"))
    return whitelist


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
    period_spans = [match.span() for match in _PERIOD_LITERAL.finditer(summary)]
    for number in _NUMBER.finditer(summary):
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
    """핵심 3등급과 숫자 whitelist만 검증한다."""
    context = _load_context(prompt)
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

        output_text = getattr(interaction, "output_text", None)
        if not isinstance(output_text, str) or not output_text.strip():
            raise GeminiInsightResponseError("Gemini 응답에 텍스트 출력이 없습니다.")
        try:
            insight = OverviewTakeawayInsight.model_validate_json(output_text)
        except ValidationError as exc:
            raise GeminiInsightResponseError(
                "Gemini 응답의 구조화된 출력이 올바르지 않습니다."
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
