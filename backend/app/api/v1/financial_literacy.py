"""
Standalone Financial Literacy endpoint.
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel

from app.core.auth import get_current_user, TokenPayload
from app.services.financial_literacy import CONTENT

router = APIRouter()


class FinancialLiteracyTopic(BaseModel):
    id: str
    title: str
    core: str
    formula: str
    example: str
    follow_up: str


@router.get("/topics", response_model=list[FinancialLiteracyTopic])
async def list_topics(current_user: TokenPayload = Depends(get_current_user)):
    """
    List all available financial literacy topics.
    """
    topics = []
    for k, v in CONTENT.items():
        topics.append(
            FinancialLiteracyTopic(
                id=k,
                title=v["title"],
                core=v["core"],
                formula=v.get("formula", ""),
                example=v.get("example", ""),
                follow_up=v.get("follow_up", ""),
            )
        )
    return topics
