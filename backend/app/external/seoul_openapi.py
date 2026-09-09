import httpx

from app.core.config import settings


# 오류 핸들러
class SeoulOpenAPIError(Exception):
    pass


class SeoulOpenAPIAuthError(SeoulOpenAPIError):
    pass


class SeoulOpenAPIResponseError(SeoulOpenAPIError):
    pass


class SeoulOpenAPIClient:
    SERVICE_NAME = "VwsmTrdarSelngQq"
    PAGE_SIZE = 1000

    async def fetch_page(
        self,
        client: httpx.AsyncClient,
        *,
        quarter: str,
        start: int,
        end: int,
    ) -> dict:
        url = (
            f"{settings.SEOUL_API_BASE_URL}/"
            f"{settings.SEOUL_API_KEY}/"
            f"json/"
            f"{self.SERVICE_NAME}/"
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

        self._validate_response(data)

        return data

    def _validate_response(self, data: dict) -> None:
        top_level_result = data.get("RESULT")

        # 응답 본문에 오류가 있으면 실패 처리
        if top_level_result:
            code = top_level_result.get("CODE")
            message = top_level_result.get("MESSAGE")

            if code == "INFO-100":
                raise SeoulOpenAPIAuthError(message)

            if code != "INFO-000":
                raise SeoulOpenAPIResponseError(f"[{code}] {message}")

        service_data = data.get(self.SERVICE_NAME)

        if service_data is None:
            raise SeoulOpenAPIResponseError(
                f"{self.SERVICE_NAME} 응답 데이터가 없습니다."
            )

        result = service_data.get("RESULT")

        if result:
            code = result.get("CODE")
            message = result.get("MESSAGE")

            if code == "INFO-100":
                raise SeoulOpenAPIAuthError(message)

            if code != "INFO-000":
                raise SeoulOpenAPIResponseError(f"[{code}] {message}")

    async def fetch_all(self, quarter: str) -> list[dict]:
        rows: list[dict] = []
        start = 1

        async with httpx.AsyncClient(timeout=30.0) as client:
            while True:
                end = start + self.PAGE_SIZE - 1

                data = await self.fetch_page(
                    client,
                    quarter=quarter,
                    start=start,
                    end=end,
                )

                service_data = data[self.SERVICE_NAME]
                page_rows = service_data.get("row", [])
                total_count = int(service_data.get("list_total_count", 0))

                rows.extend(page_rows)

                if len(rows) >= total_count:
                    break

                if not page_rows:
                    raise SeoulOpenAPIResponseError(
                        "전체 수집 전에 빈 페이지가 반환되었습니다."
                    )

                start += self.PAGE_SIZE

        return rows
