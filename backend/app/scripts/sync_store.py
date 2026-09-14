import argparse
import asyncio
import logging
import re
import sys
from pathlib import Path

# backend 디렉터리에서 `python -m app.scripts.sync_store` 실행을 지원한다.
PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backend.app.core.database import AsyncSessionLocal
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
        description="서울 Open API 분기 점포 데이터 수집"
    )
    parser.add_argument(
        "--quarter",
        required=True,
        type=parse_quarter,
        help="조회할 분기. 예: 20261 또는 20262",
    )
    return parser.parse_args()


async def sync_store(quarter: str) -> int:
    logger.info("분기 점포 동기화 시작 quarter=%s", quarter)

    api_client = SeoulOpenAPIClient()
    rows = await api_client.fetch_store_all(quarter)

    logger.info("점포 API 수집 완료 quarter=%s total=%d", quarter, len(rows))

    async with AsyncSessionLocal() as session:
        stored_count = await StoreSyncService(session).sync(rows)

    logger.info("분기 점포 동기화 완료 quarter=%s total=%d", quarter, stored_count)
    return stored_count


def main() -> None:
    args = parse_args()

    try:
        asyncio.run(sync_store(args.quarter))
    except SeoulOpenAPIError:
        logger.exception("서울 Open API 점포 수집 실패")
        raise SystemExit(1)
    except Exception:
        logger.exception("분기 점포 동기화 실패")
        raise SystemExit(1)


if __name__ == "__main__":
    main()
