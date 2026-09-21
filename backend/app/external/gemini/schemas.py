from __future__ import annotations

import re

from pydantic import BaseModel, ConfigDict, Field, field_validator

_PLAIN_TEXT_MARKUP = re.compile(
    r"(?:^|\n)\s*(?:#{1,6}\s|[-*+]\s+|>\s?|\d+[.)]\s+)"
    r"|`{1,3}|\*\*|__|~~|\[[^\]\n]+\]\([^\n)]+\)",
    re.MULTILINE,
)
_JSON_LIKE = re.compile(r"^\s*(?:\{.*\}|\[.*\])\s*$", re.DOTALL)
_SENTENCE_TERMINATOR = re.compile(r"(?<!\d)[.!?。！？]")
_FORBIDDEN_CLAIMS = re.compile(
    r"창업\s*성공|성공(?:을|이)?\s*(?:보장|확신)|"
    r"(?:수익|이익)(?:을|이)?\s*보장|투자(?:금)?\s*회수|"
    r"미래\s*(?:매출|성과|수익)|(?:반드시|무조건)|확실(?:히|한)|"
    r"(?:최고|최적|대박|유망)|강력\s*추천|추천합니다|"
    r"매출(?:이|은)?\s*(?:오를|늘|증가할|상승할)",
)
_MISLEADING_COMPETITION = re.compile(
    r"경쟁\s*(?:강도|수준)\s*(?:가|은|이)?\s*(?:높|낮|강|약)|"
    r"경쟁(?:이|은)\s*(?:치열|심하|높)|"
    r"경쟁\s*여건(?:이|은)\s*(?:치열|심하)",
)


def is_misleading_competition(summary: str) -> bool:
    return _MISLEADING_COMPETITION.search(summary) is not None


class _StrictModel(BaseModel):
    model_config = ConfigDict(
        allow_inf_nan=False,
        extra="forbid",
        frozen=True,
        strict=True,
        str_strip_whitespace=True,
    )


class OverviewTakeawayInsight(_StrictModel):
    # prompt는 100자 이내를 목표로 하며, 내부 응답 검증은 120자까지 허용한다.
    summary: str = Field(
        min_length=1,
        max_length=120,
        description=(
            "overview insight에 사용할 태그 포함 120자 이내의 한국어 평문 최대 두 문장. "
            "핵심 관계와 현재 상태를 연결하며, "
            "점수·등급을 새로 계산하거나 성공을 단정하지 않는다."
        ),
    )

    @field_validator("summary")
    @classmethod
    def validate_plain_korean_summary(cls, value: str) -> str:
        summary = value.strip()
        if not 1 <= len(summary) <= 120:
            raise ValueError("summary must be between 1 and 120 characters")
        if (
            "\n" in summary
            or "\r" in summary
            or _PLAIN_TEXT_MARKUP.search(summary)
            or _JSON_LIKE.match(summary)
        ):
            raise ValueError("summary must be plain text on one line")
        if not re.search(r"[가-힣]", summary):
            raise ValueError("summary must contain Korean text")
        terminators = list(_SENTENCE_TERMINATOR.finditer(summary))
        if not 1 <= len(terminators) <= 2 or not summary.endswith(
            terminators[-1].group()
        ):
            raise ValueError("summary must contain one or two sentences")
        if _FORBIDDEN_CLAIMS.search(summary):
            raise ValueError("summary must not make promotional or guaranteed claims")
        if is_misleading_competition(summary):
            raise ValueError(
                "summary must not reinterpret competition score as intensity"
            )
        return summary
