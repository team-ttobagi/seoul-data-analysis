import logging
from typing import Any

from backend.app.domain.sales.sync_service import SalesSyncService
from backend.app.domain.store.models import StoreModel
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)


class StoreSyncError(Exception):
    """점포 데이터 적재 과정에서 발생하는 오류."""


class StoreSyncService(SalesSyncService):
    """점포 원천 데이터와 관련 기준정보를 PostgreSQL에 동기화한다."""

    BATCH_SIZE = 500
    reference_error_type = StoreSyncError

    def __init__(self, session: AsyncSession):
        # SalesSyncService의 상권-자치구 매핑과 기준정보 UPSERT를 재사용한다.
        super().__init__(session)

    async def sync(self, rows: list[dict[str, Any]]) -> int:
        """
        서울 Open API raw 데이터를 점포 및 기준정보 테이블에 적재한다.

        적재 중 하나라도 실패하면 기준정보와 점포 데이터 변경을 함께 rollback한다.
        """
        if not rows:
            logger.info("적재할 점포 데이터가 없습니다.")
            return 0

        quarter = str(rows[0].get("STDR_YYQU_CD", "unknown"))

        try:
            (
                trade_area_types,
                trade_areas,
                service_industries,
                store_rows,
            ) = self._split_store_rows(rows)

            trade_area_codes = [item["trdar_cd"] for item in trade_areas]
            signgu_map = await self._get_signgu_map(trade_area_codes)
            self._attach_signgu_codes(trade_areas, signgu_map)

            await self._upsert_trade_area_types(trade_area_types)
            await self._upsert_service_industries(service_industries)
            await self._upsert_trade_areas(trade_areas)
            await self._upsert_store_batches(store_rows)

            await self.session.commit()

            logger.info(
                "점포 데이터 적재 성공 quarter=%s total=%d",
                quarter,
                len(store_rows),
            )

            return len(store_rows)

        except Exception:
            await self.session.rollback()
            logger.exception("점포 데이터 적재 실패 quarter=%s", quarter)
            raise

    def _split_store_rows(
        self,
        rows: list[dict[str, Any]],
    ) -> tuple[
        list[dict[str, Any]],
        list[dict[str, Any]],
        list[dict[str, Any]],
        list[dict[str, Any]],
    ]:
        """API raw rows를 기준정보와 store_data 행으로 분리한다."""
        trade_area_types: dict[str, dict[str, Any]] = {}
        trade_areas: dict[str, dict[str, Any]] = {}
        service_industries: dict[str, dict[str, Any]] = {}
        store_data: list[dict[str, Any]] = []

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
                store_data.append(self._to_store_data(row))
            except KeyError as exc:
                raise StoreSyncError(
                    f"점포 API 응답에 필수 필드가 없습니다: {exc}"
                ) from exc

        return (
            list(trade_area_types.values()),
            list(trade_areas.values()),
            list(service_industries.values()),
            store_data,
        )

    def _to_store_data(self, row: dict[str, Any]) -> dict[str, Any]:
        """점포 API 필드를 store_data 컬럼에 맞추고 모든 수치를 int로 변환한다."""
        store_row: dict[str, Any] = {}
        key_columns = {
            "stdr_yyqu_cd",
            "trdar_cd",
            "svc_induty_cd",
        }

        for column in StoreModel.__table__.columns:
            column_name = column.name

            if column_name == "store_id":
                continue

            api_key = column_name.upper()
            if api_key not in row:
                raise StoreSyncError(
                    f"점포 API 응답에 필요한 필드가 없습니다: {api_key}"
                )

            value = row[api_key]
            if column_name in key_columns:
                store_row[column_name] = str(value)
                continue

            try:
                # OPBIZ_RT/CLSBIZ_RT도 원천 정의상 정수이므로 float 변환을 하지 않는다.
                store_row[column_name] = int(value or 0)
            except (TypeError, ValueError) as exc:
                raise StoreSyncError(
                    f"점포 수치 변환에 실패했습니다: {api_key}={value}"
                ) from exc

        return store_row

    async def _upsert_store_batches(self, rows: list[dict[str, Any]]) -> None:
        """store_data를 500건 단위로 UPSERT한다."""
        if not rows:
            return

        excluded_columns = {
            "store_id",
            "stdr_yyqu_cd",
            "trdar_cd",
            "svc_induty_cd",
        }
        update_columns = [
            column.name
            for column in StoreModel.__table__.columns
            if column.name not in excluded_columns
        ]

        total = len(rows)
        for start in range(0, total, self.BATCH_SIZE):
            batch = rows[start : start + self.BATCH_SIZE]
            stmt = insert(StoreModel).values(batch)
            stmt = stmt.on_conflict_do_update(
                constraint="uq_store_data_period_area_industry",
                set_={
                    column_name: getattr(stmt.excluded, column_name)
                    for column_name in update_columns
                },
            )
            await self.session.execute(stmt)

            current = min(start + self.BATCH_SIZE, total)
            logger.info("store_data batch 적재 progress=%d/%d", current, total)
