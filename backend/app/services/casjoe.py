"""
Casjoe Biz API client.
All calls are scoped to the business_id extracted from the JWT — never from user input.
"""
import time
import logging
import httpx
from typing import Optional

from app.core.config import settings

logger = logging.getLogger(__name__)


class CasjoeBizClient:
    """
    HTTP client for Casjoe Biz API.
    business_id is set at construction time from the validated JWT — immutable.
    """

    def __init__(self, jwt_token: str, business_id: str):
        self.base_url = settings.CASJOE_API_BASE_URL
        self.business_id = business_id  # From JWT — authoritative
        self.headers = {
            "Authorization": f"Bearer {jwt_token}",
            "X-Business-ID": business_id,
            "Content-Type": "application/json",
        }

    async def _get(self, endpoint: str, params: dict = None) -> tuple[dict, int, int]:
        """
        Make a GET request. Returns (data, status_code, latency_ms).
        """
        start = time.perf_counter()
        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.get(
                f"{self.base_url}{endpoint}",
                headers=self.headers,
                params=params or {},
            )
        latency_ms = int((time.perf_counter() - start) * 1000)

        if resp.status_code == 200:
            return resp.json(), resp.status_code, latency_ms

        logger.warning(f"Casjoe API {endpoint} returned {resp.status_code}")
        return {}, resp.status_code, latency_ms

    # ─── Sales ────────────────────────────────────────────────────────────────

    async def get_sales(self, period: str = "week") -> tuple[dict, int, int]:
        return await self._get("/sales", {"period": period})

    async def get_top_products(self, limit: int = 3) -> tuple[dict, int, int]:
        return await self._get("/sales/top-products", {"limit": limit})

    async def get_sales_trend(self, days: int = 7) -> tuple[dict, int, int]:
        return await self._get("/sales/trend", {"days": days})

    # ─── Customers ────────────────────────────────────────────────────────────

    async def get_receivables(self) -> tuple[dict, int, int]:
        return await self._get("/receivables")

    async def get_top_customers(self, limit: int = 3) -> tuple[dict, int, int]:
        return await self._get("/customers/top", {"limit": limit})

    async def get_customer(self, customer_id: str) -> tuple[dict, int, int]:
        return await self._get(f"/customers/{customer_id}")

    async def get_customer_payments(self, customer_id: str) -> tuple[dict, int, int]:
        return await self._get(f"/customers/{customer_id}/payments")

    # ─── Expenses ─────────────────────────────────────────────────────────────

    async def get_expenses(self, period: str = "month") -> tuple[dict, int, int]:
        return await self._get("/expenses", {"period": period})

    async def get_top_expenses(self, limit: int = 3) -> tuple[dict, int, int]:
        return await self._get("/expenses/top", {"limit": limit})

    # ─── Inventory ────────────────────────────────────────────────────────────

    async def get_inventory_summary(self) -> tuple[dict, int, int]:
        return await self._get("/inventory/summary")

    async def get_low_stock(self) -> tuple[dict, int, int]:
        return await self._get("/inventory/low-stock")

    async def get_inventory_value(self) -> tuple[dict, int, int]:
        return await self._get("/inventory/value")

    # ─── Business summary ─────────────────────────────────────────────────────

    async def get_business_summary(self, period: str = "month") -> tuple[dict, int, int]:
        return await self._get("/business/summary", {"period": period})
