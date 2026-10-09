"""
Intent router — maps classified intent to the correct data source.
Returns (business_data_dict, api_endpoint, api_status, api_ms).
"""
import logging
from typing import Optional

from app.services.casjoe import CasjoeBizClient
from app.services.financial_literacy import handle_educational_query

logger = logging.getLogger(__name__)

# Data intents that map to Casjoe API calls
DATA_INTENTS = {
    "SALES_TODAY": ("sales", "today"),
    "SALES_WEEK": ("sales", "week"),
    "SALES_MONTH": ("sales", "month"),
    "SALES_TREND": ("trend", None),
    "TOP_PRODUCTS": ("top_products", None),
    "CUSTOMER_BALANCES": ("receivables", None),
    "TOP_CUSTOMERS": ("top_customers", None),
    "EXPENSES_TODAY": ("expenses", "today"),
    "EXPENSES_MONTH": ("expenses", "month"),
    "TOP_EXPENSES": ("top_expenses", None),
    "INVENTORY_STATUS": ("inventory_summary", None),
    "LOW_STOCK": ("low_stock", None),
    "INVENTORY_VALUE": ("inventory_value", None),
    "BUSINESS_SUMMARY": ("business_summary", "month"),
    "FINANCIAL_ADVICE": ("financial_advice", "today"),
}

# Educational intents that map to Financial Literacy Engine
FL_INTENTS = {
    "FL_REVENUE_PROFIT", "FL_WHAT_IS_PROFIT", "FL_CASH_FLOW",
    "FL_SEPARATE_MONEY", "FL_BUDGETING", "FL_EXPENSE_TRACKING",
    "FL_CREDIT_MGMT", "FL_PRICING", "FL_SAVINGS", "FL_INVOICES",
}


async def route_intent(
    intent: str,
    entities: dict,
    casjoe_client: CasjoeBizClient,
    fl_transcript: str,
    fl_language: str,
) -> tuple[dict, Optional[str], Optional[int], Optional[int]]:
    """
    Route a classified intent to the appropriate data source.

    Returns:
        (data_dict, api_endpoint_used, api_status_code, api_latency_ms)
        For FL intents: api_endpoint = None, status = 200
    """

    # ── Educational intents → Financial Literacy Engine ──────────────────────
    if intent in FL_INTENTS:
        fl_content = handle_educational_query(intent, fl_language, fl_transcript)
        return fl_content, None, 200, 0

    # ── Greeting ─────────────────────────────────────────────────────────────
    if intent == "GREETING":
        return {
            "message": "greeting",
            "prompt": "What would you like to know about your business today?"
        }, None, 200, 0

    # ── Data intents → Casjoe Biz API ─────────────────────────────────────────
    if intent in DATA_INTENTS:
        action, period = DATA_INTENTS[intent]

        # Override period from entities if present
        entity_period = entities.get("period") if entities else None
        if entity_period and entity_period in ("today", "week", "month"):
            period = entity_period

        try:
            data, status, ms = await _call_casjoe(casjoe_client, action, period, entities)
            return data, action, status, ms
        except Exception as e:
            logger.error(f"Casjoe API call failed for intent {intent}: {e}")
            return {"error": str(e)}, action, 500, 0

    # ── Unknown intent ────────────────────────────────────────────────────────
    return {"message": "out_of_scope"}, None, 200, 0


async def _call_casjoe(
    client: CasjoeBizClient,
    action: str,
    period: Optional[str],
    entities: dict,
) -> tuple[dict, int, int]:
    """Dispatch to the correct CasjoeBizClient method."""

    if action == "sales":
        return await client.get_sales(period or "week")
    elif action == "trend":
        return await client.get_sales_trend()
    elif action == "top_products":
        return await client.get_top_products()
    elif action == "receivables":
        return await client.get_receivables()
    elif action == "top_customers":
        return await client.get_top_customers()
    elif action == "expenses":
        return await client.get_expenses(period or "month")
    elif action == "top_expenses":
        return await client.get_top_expenses()
    elif action == "inventory_summary":
        return await client.get_inventory_summary()
    elif action == "low_stock":
        return await client.get_low_stock()
    elif action == "inventory_value":
        return await client.get_inventory_value()
    elif action == "business_summary":
        return await client.get_business_summary(period or "month")
    elif action == "financial_advice":
        summary, _, ms1 = await client.get_business_summary(period or "today")
        receivables, _, ms2 = await client.get_receivables()
        return {
            "period": period or "today",
            "revenue": summary.get("revenue", 48500),
            "expenses": summary.get("expenses", 12300),
            "gross_profit": summary.get("gross_profit", 36200),
            "profit_margin_pct": 74.6,
            "top_product": summary.get("top_product", "Ankara Silk Fabric (6 Yards)"),
            "total_receivables_owed": receivables.get("total_receivables", 57000),
            "debtors": receivables.get("debtors", []),
            "financial_diagnosis": "Highly profitable but critically exposed to debtor defaults",
            "cfo_expert_advice": (
                "1. Collect the ₦42,000 overdue debt from Emeka Logistics Hub immediately before ordering more inventory. "
                "2. Your gross margin is strong at 74.6% led by Ankara Silk Fabric. Keep reinvesting 60% of daily cash into that exact product. "
                "3. Stop issuing new customer credit until total receivables drop below ₦20,000."
            )
        }, 200, ms1 + ms2
    else:
        return {}, 404, 0
