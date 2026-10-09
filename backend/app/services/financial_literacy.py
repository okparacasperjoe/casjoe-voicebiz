"""
Financial Literacy Engine — structured content store.
All content is pre-written and reviewed. N-ATLAS formats but does not invent.
"""
import logging

logger = logging.getLogger(__name__)

CONTENT = {
    "FL_WHAT_IS_PROFIT": {
        "title": "What is Profit?",
        "core": (
            "Profit is what you keep after paying for everything used to make a sale. "
            "If you sell something for more than it cost you, the difference is your profit."
        ),
        "formula": "Profit = Revenue - Cost",
        "example": (
            "Mama Chibuzor buys 5 bags of garri for N3,500 and sells them for N5,000. "
            "Her profit is N1,500."
        ),
        "follow_up": "Would you like to know how to calculate your own profit from your business records?",
    },
    "FL_REVENUE_PROFIT": {
        "title": "Revenue vs Profit",
        "core": (
            "Revenue is the total money your business receives from sales. "
            "Profit is what remains after you subtract all your costs from that revenue. "
            "Revenue is always bigger. Profit is what you actually earned."
        ),
        "formula": "Revenue = all sales money | Profit = Revenue - all costs",
        "example": (
            "You sell N500,000 worth of goods in a month. "
            "But you spent N380,000 buying stock and paying rent. "
            "Your profit is N120,000, not N500,000."
        ),
        "follow_up": "Would you like to see your actual numbers from your Casjoe records?",
    },
    "FL_CASH_FLOW": {
        "title": "What is Cash Flow?",
        "core": (
            "Cash flow is the movement of money in and out of your business. "
            "Positive cash flow means more money is coming in than going out. "
            "Even a profitable business can fail if it runs out of cash."
        ),
        "formula": "Cash Flow = Money In - Money Out",
        "example": (
            "You made N200,000 profit this month, but your customers owe you N180,000. "
            "You only have N20,000 in hand. That is a cash flow problem — "
            "you are profitable but short of cash."
        ),
        "follow_up": "Would you like to check who owes you money right now?",
    },
    "FL_SEPARATE_MONEY": {
        "title": "Separating Business and Personal Money",
        "core": (
            "Mixing business money with personal money is one of the most common mistakes small business owners make. "
            "When you mix them, you cannot know your true profit, and you may unknowingly spend business capital on personal needs."
        ),
        "formula": "Business money stays in the business. Personal needs come from your salary or profit withdrawal.",
        "example": (
            "Every month, decide what salary you pay yourself from the business. "
            "That is your personal money. Everything else stays in the business account."
        ),
        "follow_up": "Would you like to know how to track your business expenses separately?",
    },
    "FL_BUDGETING": {
        "title": "What is a Budget?",
        "core": (
            "A budget is a plan for your money — deciding in advance how much you will spend on each thing. "
            "A budget helps you avoid surprises and ensures you always have money for important costs."
        ),
        "formula": "Budget = Planned Income - Planned Expenses",
        "example": (
            "If you expect to earn N300,000 this month, plan your spending: "
            "N150,000 for stock, N30,000 for rent, N20,000 for transport. "
            "That leaves N100,000 as your target profit."
        ),
        "follow_up": "Would you like to see your actual expenses this month to compare with a budget?",
    },
    "FL_EXPENSE_TRACKING": {
        "title": "Why Track Your Expenses?",
        "core": (
            "Tracking expenses means recording every amount your business spends. "
            "When you track expenses, you know exactly where your money is going "
            "and you can find areas where you are spending too much."
        ),
        "formula": "Profit is only accurate when all expenses are recorded.",
        "example": (
            "If you spend N5,000 on transport every week but never record it, "
            "you will think you made more profit than you actually did. "
            "After four weeks, that is N20,000 in hidden costs."
        ),
        "follow_up": "Would you like to see your recorded expenses for this month?",
    },
    "FL_CREDIT_MGMT": {
        "title": "Managing Credit Sales",
        "core": (
            "Selling on credit means your customer takes goods now and pays later. "
            "Credit can help you win more customers, but if it is not managed carefully, "
            "it can destroy your cash flow. Always record who owes you and for how long."
        ),
        "formula": "Total Credit Given - Payments Received = Outstanding Balance",
        "example": (
            "If 5 customers each owe you N20,000, that is N100,000 of your money sitting outside your business. "
            "The longer they delay, the harder it is to restock and keep trading."
        ),
        "follow_up": "Would you like to see who currently owes you money and how much?",
    },
    "FL_PRICING": {
        "title": "How to Price for Profit",
        "core": (
            "To make a profit, your selling price must be higher than your cost price. "
            "Your selling price should cover: cost of goods, operating expenses, and your desired profit margin."
        ),
        "formula": "Selling Price = Cost Price + Operating Expenses Share + Profit Margin",
        "example": (
            "You buy a fabric roll for N8,000. Transport cost N500. "
            "You want 25% profit. "
            "Cost = N8,500. 25% of N8,500 = N2,125. Selling price = N10,625."
        ),
        "follow_up": "Would you like to see your top-selling products to review their pricing?",
    },
    "FL_SAVINGS": {
        "title": "Saving and Reinvesting in Your Business",
        "core": (
            "Not all profit should be spent. A wise business owner keeps a portion as reserves "
            "for slow months, unexpected costs, or to grow the business. "
            "Aim to save at least 10-20% of monthly profit."
        ),
        "formula": "Business Reserve = Monthly Profit x Savings Rate",
        "example": (
            "If your profit is N100,000 per month and you save 15%, "
            "after 6 months you will have N90,000 in reserve — "
            "enough to survive a bad month or buy more stock when an opportunity comes."
        ),
        "follow_up": "Would you like to see your profit for this month to calculate what you could save?",
    },
    "FL_INVOICES": {
        "title": "What is an Invoice?",
        "core": (
            "An invoice is a document you give to a customer that lists what they bought, "
            "the price of each item, and the total amount they owe you. "
            "Issuing invoices protects you legally and helps you track who owes you money."
        ),
        "formula": "Invoice = List of Items + Unit Prices + Total Amount + Payment Terms",
        "example": (
            "You sold 10 bags of rice to ABC Stores. Your invoice will show: "
            "10 bags x N5,000 = N50,000. Payment due in 7 days. "
            "This is your legal record of the debt."
        ),
        "follow_up": "Would you like to create an invoice right now using your voice?",
    },
}


def handle_educational_query(intent: str, language: str, transcript: str) -> dict:
    """
    Return structured FL content for N-ATLAS to format.
    Returns a dict that becomes business_data in the response formatter.
    """
    content = CONTENT.get(intent)
    if not content:
        return {
            "type": "educational",
            "error": "Topic not found",
            "message": "I don't have information on that topic yet, but I'm learning more every day.",
        }

    return {
        "type": "educational",
        "title": content["title"],
        "explanation": content["core"],
        "formula": content.get("formula", ""),
        "example": content.get("example", ""),
        "follow_up": content.get("follow_up", ""),
        "instruction": (
            f"Format this as a warm, simple explanation in {language} for a Nigerian market trader. "
            f"Use the example provided. Maximum 3-4 sentences."
        ),
    }
