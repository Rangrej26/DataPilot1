"""
DataPilot AI - Pydantic Schemas for AI Data Analyst
"""

from typing import Dict, List, Any, Optional
from pydantic import BaseModel, Field


class AnalystQuestionRequest(BaseModel):
    question: str = Field(..., min_length=2, max_length=1000)
    theme: Optional[str] = "Professional SaaS"


class AnalystQuestionResponse(BaseModel):
    question: str
    primary_finding: str
    bullet_points: List[str]
    facts: Dict[str, Any]
    calculation_details: str
    mode: str  # deterministic or llm
    has_chart: bool
    chart_figure: Optional[Dict[str, Any]] = None
    table_data: Optional[List[Dict[str, Any]]] = None

