"""
DataPilot AI - Pydantic Schemas for DuckDB SQL Assistant
"""

from typing import Dict, List, Any, Optional
from pydantic import BaseModel, Field


class SQLExecuteRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=5000)
    max_rows: Optional[int] = Field(default=500, ge=1, le=5000)


class SQLExecuteResponse(BaseModel):
    success: bool
    columns: List[str]
    rows: List[Dict[str, Any]]
    row_count: int
    execution_time_ms: float
    error: Optional[str] = None


class SQLExplainRequest(BaseModel):
    query: str


class SQLExplainResponse(BaseModel):
    clauses: Dict[str, str]
    summary: str


class SQLGenerateRequest(BaseModel):
    question: str = Field(..., min_length=3, max_length=500)


class SQLGenerateResponse(BaseModel):
    generated_sql: str
    explanation: str
    mode: str  # rule_based or llm

