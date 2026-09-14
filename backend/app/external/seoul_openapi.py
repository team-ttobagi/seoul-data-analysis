import httpx
from backend.app.core.config import settings


# 오류 핸들러
class SeoulOpenAPIError(Exception):
    pass


class SeoulOpenAPIAuthError(SeoulOpenAPIError):
    pass


class SeoulOpenAPIResponseError(SeoulOpenAPIError):
    pass


class SeoulOpenAPIClient:
    SALES_SERVICE_NAME = "VwsmTrdarSelngQq"
    STORE_SERVICE_NAME = "VwsmTrdarStorQq"
    # 기존 fetch_all/fetch_page 호출자의 매출 API 동작을 보존한다.
    SERVICE_NAME = SALES_SERVICE_NAME
    PAGE_SIZE = 1000

    async def fetch_page(
        self,
        client: httpx.AsyncClient,
        *,
        quarter: str,
        start: int,
        end: int,
    ) -> dict:
        """매출 API 한 페이지를 조회한다. 기존 호출 호환용 메서드."""
        return await self.fetch_sales_page(
            client,
            quarter=quarter,
            start=start,
            end=end,
        )

    async def fetch_sales_page(
        self,
        client: httpx.AsyncClient,
        *,
        quarter: str,
        start: int,
        end: int,
    ) -> dict:
        """매출(VwsmTrdarSelngQq) API 한 페이지를 조회한다."""
        return await self._fetch_page(
            client,
            service_name=self.SALES_SERVICE_NAME,
            quarter=quarter,
            start=start,
            end=end,
        )

    async def fetch_store_page(
        self,
        client: httpx.AsyncClient,
        *,
        quarter: str,
        start: int,
        end: int,
    ) -> dict:
        """점포(VwsmTrdarStorQq) API 한 페이지를 조회한다."""
        return await self._fetch_page(
            client,
            service_name=self.STORE_SERVICE_NAME,
            quarter=quarter,
            start=start,
            end=end,
        )

    async def _fetch_page(
        self,
        client: httpx.AsyncClient,
        *,
        service_name: str,
        quarter: str,
        start: int,
        end: int,
    ) -> dict:
        url = (
            f"{settings.SEOUL_API_BASE_URL}/"
            f"{settings.SEOUL_API_KEY}/"
            f"json/"
            f"{service_name}/"
            f"{start}/"
            f"{end}/"
            f"{quarter}"
        )

        try:
            response = await client.get(url)
            response.raise_for_status()
        except httpx.HTTPError as exc:
            raise SeoulOpenAPIError(f"서울 Open API HTTP 요청 실패: {exc}") from exc

        try:
            data = response.json()
        except ValueError as exc:
            raise SeoulOpenAPIResponseError(
                "서울 Open API 응답이 JSON 형식이 아닙니다."
            ) from exc

        self._validate_response(data, service_name=service_name)

        return data

    def _validate_response(
        self,
        data: dict,
        *,
        service_name: str | None = None,
    ) -> None:
        service_name = service_name or self.SALES_SERVICE_NAME

        if not isinstance(data, dict):
            raise SeoulOpenAPIResponseError(
                "서울 Open API 응답 본문이 객체 형식이 아닙니다."
            )

        top_level_result = data.get("RESULT")

        # 응답 본문에 오류가 있으면 실패 처리
        if top_level_result:
            if not isinstance(top_level_result, dict):
                raise SeoulOpenAPIResponseError(
                    "서울 Open API RESULT 응답 형식이 올바르지 않습니다."
                )

            code = top_level_result.get("CODE")
            message = top_level_result.get("MESSAGE")

            if code == "INFO-100":
                raise SeoulOpenAPIAuthError(message)

            if code != "INFO-000":
                raise SeoulOpenAPIResponseError(f"[{code}] {message}")

        service_data = data.get(service_name)

        if not isinstance(service_data, dict):
            raise SeoulOpenAPIResponseError(f"{service_name} 응답 데이터가 없습니다.")

        result = service_data.get("RESULT")

        if result:
            if not isinstance(result, dict):
                raise SeoulOpenAPIResponseError(
                    f"{service_name} RESULT 응답 형식이 올바르지 않습니다."
                )

            code = result.get("CODE")
            message = result.get("MESSAGE")

            if code == "INFO-100":
                raise SeoulOpenAPIAuthError(message)

            if code != "INFO-000":
                raise SeoulOpenAPIResponseError(f"[{code}] {message}")

    async def fetch_all(self, quarter: str) -> list[dict]:
        """매출 API 전체 수집. 기존 호출 호환용 메서드."""
        return await self.fetch_sales_all(quarter)

    async def fetch_sales_all(self, quarter: str) -> list[dict]:
        """매출(VwsmTrdarSelngQq) API의 모든 페이지를 수집한다."""
        return await self._fetch_all(
            quarter,
            service_name=self.SALES_SERVICE_NAME,
        )

    async def fetch_store_all(self, quarter: str) -> list[dict]:
        """점포(VwsmTrdarStorQq) API의 모든 페이지를 수집한다."""
        return await self._fetch_all(
            quarter,
            service_name=self.STORE_SERVICE_NAME,
        )

    async def _fetch_all(
        self,
        quarter: str,
        *,
        service_name: str,
    ) -> list[dict]:
        rows: list[dict] = []
        start = 1

        async with httpx.AsyncClient(timeout=30.0) as client:
            while True:
                end = start + self.PAGE_SIZE - 1

                data = await self._fetch_page(
                    client,
                    service_name=service_name,
                    quarter=quarter,
                    start=start,
                    end=end,
                )

                service_data = data[service_name]
                page_rows = service_data.get("row", [])

                if not isinstance(page_rows, list):
                    raise SeoulOpenAPIResponseError(
                        f"{service_name} row 응답 형식이 올바르지 않습니다."
                    )

                try:
                    total_count = int(service_data.get("list_total_count", 0))
                except (TypeError, ValueError) as exc:
                    raise SeoulOpenAPIResponseError(
                        f"{service_name} list_total_count 변환에 실패했습니다."
                    ) from exc

                rows.extend(page_rows)

                if len(rows) >= total_count:
                    break

                if not page_rows:
                    raise SeoulOpenAPIResponseError(
                        "전체 수집 전에 빈 페이지가 반환되었습니다."
                    )

                start += self.PAGE_SIZE

        return rows
