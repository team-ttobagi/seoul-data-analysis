import argparse
import asyncio
import logging
import re
import sys
from pathlib import Path

# 프로젝트의 기존 import 경로(backend.app.*)를 유지하면서
# backend 디렉터리에서 `python -m app.scripts.sync_quarterly` 실행을 지원한다.
PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backend.app.core.database import AsyncSessionLocal
from backend.app.domain.sales.sync_service import SalesSyncService
from backend.app.domain.store.sync_service import StoreSyncService
from backend.app.external.seoul_openapi import SeoulOpenAPIClient, SeoulOpenAPIError

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
)

logger = logging.getLogger(__name__)


def parse_quarter(value: str) -> str:
    if not re.fullmatch(r"\d{4}[1-4]", value):
        raise argparse.ArgumentTypeError("분기는 YYYYQ 형식이어야 합니다. 예: 20261")
    return value


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="서울 Open API 분기 매출·점포 데이터 수집"
    )
    parser.add_argument(
        "--quarter",
        required=True,
        type=parse_quarter,
        help="조회할 분기. 예: 20261",
    )
    return parser.parse_args()


async def sync_quarterly(quarter: str) -> tuple[int, int]:
    """한 분기의 매출을 먼저 동기화한 뒤 점포 데이터를 동기화한다."""
    api_client = SeoulOpenAPIClient()

    logger.info("분기 매출 동기화 시작 quarter=%s", quarter)
    sales_rows = await api_client.fetch_sales_all(quarter)
    logger.info("매출 API 수집 완료 quarter=%s total=%d", quarter, len(sales_rows))

    async with AsyncSessionLocal() as session:
        sales_count = await SalesSyncService(session).sync(sales_rows)

    logger.info("매출 적재 완료 quarter=%s total=%d", quarter, sales_count)

    logger.info("분기 점포 동기화 시작 quarter=%s", quarter)
    store_rows = await api_client.fetch_store_all(quarter)
    logger.info("점포 API 수집 완료 quarter=%s total=%d", quarter, len(store_rows))

    async with AsyncSessionLocal() as session:
        store_count = await StoreSyncService(session).sync(store_rows)

    logger.info("점포 적재 완료 quarter=%s total=%d", quarter, store_count)
    logger.info(
        "분기 매출·점포 동기화 완료 quarter=%s sales=%d store=%d",
        quarter,
        sales_count,
        store_count,
    )
    return sales_count, store_count


def main() -> None:
    args = parse_args()

    try:
        asyncio.run(sync_quarterly(args.quarter))
    except SeoulOpenAPIError:
        logger.exception("서울 Open API 수집 실패")
        raise SystemExit(1)
    except Exception:
        logger.exception("분기 매출·점포 동기화 실패")
        raise SystemExit(1)


if __name__ == "__main__":
    main()
