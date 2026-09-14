import logging
import csv
from pathlib import Path
from typing import Any

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.domain.industry.models import ServiceIndustryModel
from backend.app.domain.sales.models import SalesDataModel
from backend.app.domain.trade_area.models import (
    TradeAreaModel,
    TradeAreaTypeModel,
)

logger = logging.getLogger(__name__)


class SalesSyncError(Exception):
    """매출 데이터 적재 과정에서 발생하는 오류."""


class SalesSyncService:
    BATCH_SIZE = 500

    def __init__(self, session: AsyncSession):
        self.session = session
        self.trade_area_mapping = self._load_trade_area_mapping()

    def _load_trade_area_mapping(
        self,
    ) -> dict[str, str]:
        """
        상권-자치구 매핑 CSV 파일을 읽어 메모리에 로드한다.

        매핑 구조:
        - key: trdar_cd
        - value: signgu_cd

        기존 trade_area에 없는 신규 상권의 자치구 코드를
        찾기 위한 fallback 데이터로 사용한다.
        """
        csv_path = (
            Path(__file__).resolve().parents[3]
            / "data"
            / "trade_area_district_mapping.csv"
        )

        if not csv_path.exists():
            raise SalesSyncError(f"상권-자치구 매핑 CSV를 찾을 수 없습니다: {csv_path}")

        mapping: dict[str, str] = {}

        with csv_path.open(
            encoding="utf-8-sig",
            newline="",
        ) as file:
            reader = csv.DictReader(file)

            for row in reader:
                trdar_cd = row["trdar_cd"].strip()
                signgu_cd = row["signgu_cd"].strip()

                if trdar_cd and signgu_cd:
                    mapping[trdar_cd] = signgu_cd

        return mapping

    async def sync(
        self,
        rows: list[dict[str, Any]],
    ) -> int:
        """
        서울 Open API raw 데이터를 신규 테이블에 적재한다.

        적재 순서:
        1. trade_area_type
        2. service_industry
        3. trade_area
        4. sales_data
        """
        if not rows:
            logger.info("적재할 매출 데이터가 없습니다.")
            return 0

        quarter = str(rows[0]["STDR_YYQU_CD"])

        try:
            (
                trade_area_types,
                trade_areas,
                service_industries,
                sales_rows,
            ) = self._split_rows(rows)

            trade_area_codes = [item["trdar_cd"] for item in trade_areas]

            signgu_map = await self._get_signgu_map(trade_area_codes)

            self._attach_signgu_codes(
                trade_areas,
                signgu_map,
            )

            await self._upsert_trade_area_types(trade_area_types)

            await self._upsert_service_industries(service_industries)

            await self._upsert_trade_areas(trade_areas)

            await self._upsert_sales_batches(sales_rows)

            await self.session.commit()

            logger.info(
                "매출 데이터 적재 성공 quarter=%s total=%d",
                quarter,
                len(sales_rows),
            )

            return len(sales_rows)

        except Exception:
            await self.session.rollback()

            logger.exception(
                "매출 데이터 적재 실패 quarter=%s",
                quarter,
            )

            raise

    def _split_rows(
        self,
        rows: list[dict[str, Any]],
    ) -> tuple[
        list[dict[str, Any]],
        list[dict[str, Any]],
        list[dict[str, Any]],
        list[dict[str, Any]],
    ]:
        """
        API raw rows를 테이블별 데이터로 분리한다.

        기준 데이터는 PK 기준 dict를 사용해서 중복을 제거한다.
        """
        trade_area_types: dict[
            str,
            dict[str, Any],
        ] = {}

        trade_areas: dict[
            str,
            dict[str, Any],
        ] = {}

        service_industries: dict[
            str,
            dict[str, Any],
        ] = {}

        sales_data: list[dict[str, Any]] = []

        for row in rows:
            try:
                trdar_se_cd = str(row["TRDAR_SE_CD"])

                trdar_cd = str(row["TRDAR_CD"])

                svc_induty_cd = str(row["SVC_INDUTY_CD"])

                trade_area_types[trdar_se_cd] = {
                    "trdar_se_cd": trdar_se_cd,
                    "trdar_se_cd_nm": row["TRDAR_SE_CD_NM"],
                }

                trade_areas[trdar_cd] = {
                    "trdar_cd": trdar_cd,
                    "trdar_se_cd": trdar_se_cd,
                    "trdar_cd_nm": row["TRDAR_CD_NM"],
                }

                service_industries[svc_induty_cd] = {
                    "svc_induty_cd": svc_induty_cd,
                    "svc_induty_cd_nm": row["SVC_INDUTY_CD_NM"],
                }

                sales_data.append(self._to_sales_data(row))

            except KeyError as exc:
                raise SalesSyncError(f"필수 API 필드가 없습니다: {exc}") from exc

        return (
            list(trade_area_types.values()),
            list(trade_areas.values()),
            list(service_industries.values()),
            sales_data,
        )

    def _to_sales_data(
        self,
        row: dict[str, Any],
    ) -> dict[str, Any]:
        """
        API의 대문자 필드명을 SalesDataModel 컬럼명으로 변환한다.

        예:
        THSMON_SELNG_AMT
        -> thsmon_selng_amt
        """
        sales_row: dict[str, Any] = {}

        key_columns = {
            "stdr_yyqu_cd",
            "trdar_cd",
            "svc_induty_cd",
        }

        for column in SalesDataModel.__table__.columns:
            column_name = column.name

            if column_name == "sales_id":
                continue

            api_key = column_name.upper()

            if api_key not in row:
                raise SalesSyncError("API 응답에 필요한 필드가 " f"없습니다: {api_key}")

            value = row[api_key]

            if column_name in key_columns:
                sales_row[column_name] = str(value)

            else:
                try:
                    sales_row[column_name] = int(value or 0)

                except (
                    TypeError,
                    ValueError,
                ) as exc:
                    raise SalesSyncError(
                        "숫자 변환에 실패했습니다: " f"{api_key}={value}"
                    ) from exc

        return sales_row

    async def _get_signgu_map(
        self,
        trdar_codes: list[str],
    ) -> dict[str, str]:
        """
        기존 trade_area에서
        TRDAR_CD -> SIGNGU_CD 매핑을 가져온다.
        """
        if not trdar_codes:
            return {}

        stmt = select(
            TradeAreaModel.trdar_cd,
            TradeAreaModel.signgu_cd,
        ).where(TradeAreaModel.trdar_cd.in_(trdar_codes))

        result = await self.session.execute(stmt)

        return {str(trdar_cd): str(signgu_cd) for trdar_cd, signgu_cd in result.all()}

    def _attach_signgu_codes(
        self,
        trade_areas: list[dict[str, Any]],
        signgu_map: dict[str, str],
    ) -> None:
        """
        기존 상권의 자치구 코드를
        API에서 받은 trade_area 데이터에 붙인다.
        """
        missing_codes: list[str] = []

        for trade_area in trade_areas:
            trdar_cd = str(trade_area["trdar_cd"])

            # 1. 기존 Supabase 매핑 우선
            signgu_cd = signgu_map.get(trdar_cd)

            # 2. DB에 없으면 CSV에서 조회
            if signgu_cd is None:
                signgu_cd = self.trade_area_mapping.get(trdar_cd)

            # 3. CSV에도 없으면 적재 중단
            if signgu_cd is None:
                missing_codes.append(trdar_cd)
                continue

            trade_area["signgu_cd"] = signgu_cd

        if missing_codes:
            raise SalesSyncError(
                "DB와 CSV 모두에서 자치구 매핑을 "
                "찾지 못한 상권이 존재합니다. "
                f"count={len(missing_codes)}, "
                f"examples={missing_codes[:10]}"
            )

    async def _upsert_trade_area_types(
        self,
        rows: list[dict[str, Any]],
    ) -> None:
        """
        trade_area_type 기준 데이터를 upsert한다.
        """
        if not rows:
            return

        stmt = insert(TradeAreaTypeModel).values(rows)

        stmt = stmt.on_conflict_do_nothing(
            index_elements=["trdar_se_cd"],
        )

        await self.session.execute(stmt)

        logger.info(
            "trade_area_type 적재 완료 total=%d",
            len(rows),
        )

    async def _upsert_service_industries(
        self,
        rows: list[dict[str, Any]],
    ) -> None:
        """
        service_industry 기준 데이터를 upsert한다.
        """
        if not rows:
            return

        stmt = insert(ServiceIndustryModel).values(rows)

        stmt = stmt.on_conflict_do_nothing(
            index_elements=["svc_induty_cd"],
        )

        await self.session.execute(stmt)

        logger.info(
            "service_industry 적재 완료 total=%d",
            len(rows),
        )

    async def _upsert_trade_areas(
        self,
        rows: list[dict[str, Any]],
    ) -> None:
        """
        trade_area를 upsert한다.

        기존 signgu_cd는 변경하지 않는다.
        """
        if not rows:
            return

        stmt = insert(TradeAreaModel).values(rows)

        stmt = stmt.on_conflict_do_nothing(
            index_elements=["trdar_cd"],
        )

        await self.session.execute(stmt)

        logger.info(
            "trade_area 적재 완료 total=%d",
            len(rows),
        )

    async def _upsert_sales_batches(
        self,
        rows: list[dict[str, Any]],
    ) -> None:
        """
        sales_data를 500건 단위로 upsert한다.

        UNIQUE:
        (
            stdr_yyqu_cd,
            trdar_cd,
            svc_induty_cd
        )
        """
        if not rows:
            return

        excluded_columns = {
            "sales_id",
            "stdr_yyqu_cd",
            "trdar_cd",
            "svc_induty_cd",
        }

        update_columns = [
            column.name
            for column in (SalesDataModel.__table__.columns)
            if column.name not in excluded_columns
        ]

        total = len(rows)

        for start in range(
            0,
            total,
            self.BATCH_SIZE,
        ):
            batch = rows[start : start + self.BATCH_SIZE]

            stmt = insert(SalesDataModel).values(batch)

            stmt = stmt.on_conflict_do_update(
                constraint=("uq_sales_data_" "period_area_industry"),
                set_={
                    column_name: getattr(
                        stmt.excluded,
                        column_name,
                    )
                    for column_name in update_columns
                },
            )

            await self.session.execute(stmt)

            current = min(
                start + self.BATCH_SIZE,
                total,
            )

            logger.info(
                "sales_data batch 적재 " "progress=%d/%d",
                current,
                total,
            )
