"""
DataPilot AI - AI Data Analyst Assistant API Endpoints
"""

import json
from typing import Dict, List, Any, Optional
from fastapi import APIRouter, HTTPException
import pandas as pd

from backend.services.dataset_store import dataset_store
from backend.core.config import GEMINI_API_KEY, GROQ_API_KEY, OPENAI_API_KEY
from backend.schemas.analyst import AnalystQuestionRequest, AnalystQuestionResponse
from modules.ai_analyst import query_data_analyst

router = APIRouter(prefix="/api/datasets", tags=["AI Data Analyst"])


@router.get("/{dataset_id}/analyst/suggested-questions", summary="Get suggested analytical questions for dataset")
async def get_suggested_questions(dataset_id: str):
    entry = dataset_store.get(dataset_id)
    if not entry:
        raise HTTPException(status_code=404, detail="Dataset not found.")

    df = entry.current_df
    num_cols = list(df.select_dtypes(include=["number"]).columns)
    cat_cols = list(df.select_dtypes(include=["object", "category", "string"]).columns)
    questions = []

    if len(num_cols) >= 2:
        questions.append(f"What are the strongest correlations between numerical columns?")
    if num_cols and cat_cols:
        questions.append(f"Which {cat_cols[0]} has the highest average {num_cols[0]}?")
    if num_cols:
        questions.append(f"Are there extreme outliers in {num_cols[0]}?")
        questions.append(f"What is the distribution and median of {num_cols[0]}?")
    if cat_cols:
        questions.append(f"What is the category breakdown and dominance in {cat_cols[0]}?")

    questions.append("What is the overall data quality and missingness status?")

    return {"questions": questions[:5]}


@router.post("/{dataset_id}/analyst/ask", summary="Ask a grounded analytical question in plain English")
async def ask_analyst(dataset_id: str, req: AnalystQuestionRequest):
    entry = dataset_store.get(dataset_id)
    if not entry:
        raise HTTPException(status_code=404, detail="Dataset not found.")

    # Determine if an LLM key is configured
    api_key = GEMINI_API_KEY or GROQ_API_KEY or OPENAI_API_KEY or None
    api_provider = "Google Gemini" if GEMINI_API_KEY else ("Groq" if GROQ_API_KEY else "OpenAI")

    res = query_data_analyst(
        question=req.question,
        df=entry.current_df,
        api_key=api_key,
        api_provider=api_provider,
        theme_name="Professional SaaS"
    )

    answer_text = res.get("answer", "")
    lines = [line.strip() for line in answer_text.splitlines() if line.strip()]

    # Extract primary bold/first finding
    primary_finding = lines[0] if lines else "No conclusive pattern detected."
    bullet_points = lines[1:] if len(lines) > 1 else []

    # Clean chart serialization
    chart_fig = res.get("chart")
    chart_json = json.loads(chart_fig.to_json()) if chart_fig is not None else None

    # Clean table serialization
    table = res.get("table")
    table_records = json.loads(table.to_json(orient="records")) if (table is not None and isinstance(table, pd.DataFrame)) else None

    return {
        "question": req.question,
        "primary_finding": primary_finding,
        "bullet_points": bullet_points,
        "facts": res.get("facts", {}),
        "calculation_details": res.get("calculation_details", "Deterministic pandas aggregation and descriptive statistics."),
        "mode": res.get("mode", "offline"),
        "has_chart": chart_json is not None,
        "chart_figure": chart_json,
        "table_data": table_records
    }

