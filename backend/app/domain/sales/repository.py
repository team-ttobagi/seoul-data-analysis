import logging
import re
from typing import Optional, List, Dict
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

logger = logging.getLogger(__name__)


def _normalize_quarter(quarter: str) -> str:
    """Convert 'YYYY Q#' (API-facing) into the DB's 'YYYYQ#' code, e.g. '2025 Q4' -> '20254'."""
    match = re.match(r"\s*(\d{4})\s*[Qq]?\s*(\d)\s*$", quarter)
    if match:
        return f"{match.group(1)}{match.group(2)}"
    return quarter


def _previous_quarter(quarter_code: str) -> str:
    year, q = int(quarter_code[:4]), int(quarter_code[4])
    if q == 1:
        return f"{year - 1}4"
    return f"{year}{q - 1}"


class SalesRepository:
    def __init__(self, session: Optional[AsyncSession] = None):
        self.session = session

    async def get_sales_summary(
        self, trade_area_code: str, industry_code: str, quarter: str
    ) -> Optional[dict]:
        if not self.session:
            return None

        code = trade_area_code.upper()
        quarter_code = _normalize_quarter(quarter)

        try:
            stmt = text(
                """
                WITH ranked AS (
                    SELECT
                        trdar_cd,
                        thsmon_selng_amt,
                        thsmon_selng_co,
                        RANK() OVER (ORDER BY thsmon_selng_amt DESC) AS sales_rank,
                        PERCENT_RANK() OVER (ORDER BY thsmon_selng_amt DESC) AS sales_pctl,
                        PERCENT_RANK() OVER (ORDER BY thsmon_selng_co DESC) AS volume_pctl
                    FROM sales_data
                    WHERE svc_induty_cd = :industry_code AND stdr_yyqu_cd = :quarter_code
                )
                SELECT * FROM ranked WHERE trdar_cd = :trade_area_code
                """
            )
            result = await self.session.execute(
                stmt,
                {"industry_code": industry_code, "quarter_code": quarter_code, "trade_area_code": code},
            )
            row = result.mappings().first()
            if not row:
                return None

            prev_stmt = text(
                """
                SELECT thsmon_selng_amt FROM sales_data
                WHERE trdar_cd = :trade_area_code AND svc_induty_cd = :industry_code AND stdr_yyqu_cd = :prev_quarter
                """
            )
            prev_result = await self.session.execute(
                prev_stmt,
                {
                    "trade_area_code": code,
                    "industry_code": industry_code,
                    "prev_quarter": _previous_quarter(quarter_code),
                },
            )
            prev_amount = prev_result.scalar()

            growth_rate = 0.0
            if prev_amount:
                growth_rate = round((row["thsmon_selng_amt"] - prev_amount) / prev_amount * 100, 1)

            return {
                "quarter": quarter,
                "trade_area_code": code,
                "industry_code": industry_code,
                "estimated_sales": row["thsmon_selng_amt"],
                "estimated_sales_formatted": _format_amount(row["thsmon_selng_amt"]),
                "transaction_count": row["thsmon_selng_co"],
                "transaction_count_formatted": _format_count(row["thsmon_selng_co"]),
                "qoq_growth_rate": growth_rate,
                "seoul_rank": row["sales_rank"],
                "sales_percentile": round(row["sales_pctl"] * 100),
                "volume_percentile": round(row["volume_pctl"] * 100),
            }
        except Exception:
            logger.exception("Failed to load sales summary from DB")
            return None

    async def get_sales_by_time(
        self, trade_area_code: str, industry_code: str, quarter: str
    ) -> List[dict]:
        row = await self._get_raw_row(trade_area_code, industry_code, quarter)
        if not row:
            return []

        slots = [
            ("00-06시", row["tmzon_00_06_selng_amt"]),
            ("06-11시", row["tmzon_06_11_selng_amt"]),
            ("11-14시", row["tmzon_11_14_selng_amt"]),
            ("14-17시", row["tmzon_14_17_selng_amt"]),
            ("17-21시", row["tmzon_17_21_selng_amt"]),
            ("21-24시", row["tmzon_21_24_selng_amt"]),
        ]
        total = sum(amount for _, amount in slots) or 1
        peak_amount = max(amount for _, amount in slots)

        return [
            {
                "slot": slot,
                "percentage": round(amount / total * 100),
                "sales_amount": amount,
                "is_peak": amount == peak_amount,
            }
            for slot, amount in slots
        ]

    async def get_sales_by_age_gender(
        self, trade_area_code: str, industry_code: str, quarter: str
    ) -> List[dict]:
        """Age-group sales share only. DB has no age x gender cross data, so gender
        is reported separately via get_gender_split() rather than combined per group."""
        row = await self._get_raw_row(trade_area_code, industry_code, quarter)
        if not row:
            return []

        groups = [
            ("10대", row["agrde_10_selng_amt"]),
            ("20대", row["agrde_20_selng_amt"]),
            ("30대", row["agrde_30_selng_amt"]),
            ("40대", row["agrde_40_selng_amt"]),
            ("50대", row["agrde_50_selng_amt"]),
            ("60대+", row["agrde_60_above_selng_amt"]),
        ]
        total = sum(amount for _, amount in groups) or 1
        peak_amount = max(amount for _, amount in groups)

        return [
            {
                "age_group": age_group,
                "percentage": round(amount / total * 100),
                "is_primary": amount == peak_amount,
            }
            for age_group, amount in groups
        ]

    async def get_gender_split(
        self, trade_area_code: str, industry_code: str, quarter: str
    ) -> Optional[dict]:
        row = await self._get_raw_row(trade_area_code, industry_code, quarter)
        if not row:
            return None

        total = (row["ml_selng_amt"] + row["fml_selng_amt"]) or 1
        female_ratio = round(row["fml_selng_amt"] / total * 100)
        male_ratio = 100 - female_ratio
        dominant_gender = "female" if female_ratio >= male_ratio else "male"

        return {
            "female_ratio": female_ratio,
            "male_ratio": male_ratio,
            "dominant_gender": dominant_gender,
        }

    async def get_sales_by_day(
        self, trade_area_code: str, industry_code: str, quarter: str
    ) -> List[dict]:
        row = await self._get_raw_row(trade_area_code, industry_code, quarter)
        if not row:
            return []

        days = [
            ("월", row["mon_selng_amt"]),
            ("화", row["tues_selng_amt"]),
            ("수", row["wed_selng_amt"]),
            ("목", row["thur_selng_amt"]),
            ("금", row["fri_selng_amt"]),
            ("토", row["sat_selng_amt"]),
            ("일", row["sun_selng_amt"]),
        ]
        total = sum(amount for _, amount in days) or 1
        average = total / len(days)
        peak_amount = max(amount for _, amount in days)

        return [
            {
                "day": day,
                "percentage": round(amount / total * 100),
                "diff_from_average": round((amount - average) / average * 100) if average else 0,
                "is_peak": amount == peak_amount,
            }
            for day, amount in days
        ]

    async def get_metrics_rows(self, quarter: str, industry_code: str) -> List[dict]:
        """Current + previous quarter sales/transaction per trade area, for the given
        quarter+industry population. Feeds analytics/scoring.py's score pipeline."""
        if not self.session:
            return []

        quarter_code = _normalize_quarter(quarter)
        prev_quarter_code = _previous_quarter(quarter_code)

        try:
            stmt = text(
                """
                SELECT
                    cur.trdar_cd AS trdar_cd,
                    cur.thsmon_selng_amt AS sales,
                    cur.thsmon_selng_co AS transaction_count,
                    prev.thsmon_selng_amt AS prev_sales,
                    prev.thsmon_selng_co AS prev_transaction_count
                FROM sales_data cur
                LEFT JOIN sales_data prev
                    ON prev.trdar_cd = cur.trdar_cd
                    AND prev.svc_induty_cd = cur.svc_induty_cd
                    AND prev.stdr_yyqu_cd = :prev_quarter_code
                WHERE cur.svc_induty_cd = :industry_code AND cur.stdr_yyqu_cd = :quarter_code
                """
            )
            result = await self.session.execute(
                stmt,
                {
                    "prev_quarter_code": prev_quarter_code,
                    "industry_code": industry_code,
                    "quarter_code": quarter_code,
                },
            )
            return [dict(row) for row in result.mappings().all()]
        except Exception:
            logger.exception("Failed to load sales metrics from DB")
            return []

    async def get_diversity_rows(self, quarter: str) -> List[dict]:
        """Every industry's sales per trade area for the quarter (no industry filter),
        used to compute HHI-based demand diversity independent of the selected industry."""
        if not self.session:
            return []

        quarter_code = _normalize_quarter(quarter)

        try:
            stmt = text(
                """
                SELECT trdar_cd, svc_induty_cd, thsmon_selng_amt AS sales
                FROM sales_data
                WHERE stdr_yyqu_cd = :quarter_code
                """
            )
            result = await self.session.execute(stmt, {"quarter_code": quarter_code})
            return [dict(row) for row in result.mappings().all()]
        except Exception:
            logger.exception("Failed to load diversity rows from DB")
            return []

    async def _get_raw_row(
        self, trade_area_code: str, industry_code: str, quarter: str
    ) -> Optional[Dict]:
        if not self.session:
            return None

        try:
            stmt = text(
                """
                SELECT * FROM sales_data
                WHERE trdar_cd = :trade_area_code AND svc_induty_cd = :industry_code AND stdr_yyqu_cd = :quarter_code
                """
            )
            result = await self.session.execute(
                stmt,
                {
                    "trade_area_code": trade_area_code.upper(),
                    "industry_code": industry_code,
                    "quarter_code": _normalize_quarter(quarter),
                },
            )
            return result.mappings().first()
        except Exception:
            logger.exception("Failed to load sales data row from DB")
            return None


def _format_amount(amount: int) -> str:
    if amount >= 100_000_000:
        return f"{amount / 100_000_000:.1f}억"
    if amount >= 10_000:
        return f"{amount / 10_000:.0f}만"
    return str(amount)


def _format_count(count: int) -> str:
    if count >= 10_000:
        return f"{count / 10_000:.0f}만"
    return str(count)
