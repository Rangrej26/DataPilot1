"""
DataPilot AI - DuckDB SQL Assistant API Endpoints
"""

import json
from typing import Dict, List, Any, Optional
from fastapi import APIRouter, HTTPException
import pandas as pd

from backend.services.dataset_store import dataset_store
from backend.schemas.sql import (
    SQLExecuteRequest, SQLExplainRequest, SQLGenerateRequest
)
from modules.sql_engine import (
    explain_sql_query, generate_suggested_queries, rule_based_nl_to_sql,
    validate_sql_security
)

router = APIRouter(prefix="/api/datasets", tags=["SQL Assistant"])


@router.post("/{dataset_id}/sql/execute", summary="Execute read-only SQL query in DuckDB sandbox")
async def execute_sql(dataset_id: str, req: SQLExecuteRequest):
    entry = dataset_store.get(dataset_id)
    if not entry:
        raise HTTPException(status_code=404, detail="Dataset not found.")

    query = req.query.strip()
    is_safe, sec_msg = validate_sql_security(query)
    if not is_safe:
        return {
            "success": False,
            "columns": [],
            "rows": [],
            "row_count": 0,
            "execution_time_ms": 0.0,
            "error": f"Security Sandbox Notice: {sec_msg}"
        }

    res_df, elapsed_ms, err = entry.sql_engine.execute_query(query, max_rows=req.max_rows or 500)
    if err:
        return {
            "success": False,
            "columns": [],
            "rows": [],
            "row_count": 0,
            "execution_time_ms": elapsed_ms,
            "error": err
        }

    # Clean serialization
    columns = list(res_df.columns) if res_df is not None else []
    rows = json.loads(res_df.to_json(orient="records", date_format="iso")) if res_df is not None else []

    return {
        "success": True,
        "columns": columns,
        "rows": rows,
        "row_count": len(rows),
        "execution_time_ms": elapsed_ms,
        "error": None
    }


@router.post("/{dataset_id}/sql/explain", summary="Beginner-friendly breakdown of SQL clauses")
async def explain_sql(dataset_id: str, req: SQLExplainRequest):
    entry = dataset_store.get(dataset_id)
    if not entry:
        raise HTTPException(status_code=404, detail="Dataset not found.")

    clauses = explain_sql_query(req.query)
    summary_parts = []
    if "SELECT Clause" in clauses:
        summary_parts.append(clauses["SELECT Clause"])
    if "FROM Clause" in clauses:
        summary_parts.append(clauses["FROM Clause"])
    if "WHERE Clause" in clauses:
        summary_parts.append(clauses["WHERE Clause"])
    if "GROUP BY Clause" in clauses:
        summary_parts.append(clauses["GROUP BY Clause"])

    return {
        "clauses": clauses,
        "summary": " ".join(summary_parts) if summary_parts else "Analytical SQL query."
    }


@router.get("/{dataset_id}/sql/templates", summary="Get tailored query templates for dataset")
async def get_sql_templates(dataset_id: str):
    entry = dataset_store.get(dataset_id)
    if not entry:
        raise HTTPException(status_code=404, detail="Dataset not found.")

    templates = generate_suggested_queries(entry.current_df, table_name="data")
    return {
        "dataset_id": dataset_id,
        "templates": templates
    }


@router.post("/{dataset_id}/sql/generate", summary="Convert natural language question to SQL query")
async def generate_sql(dataset_id: str, req: SQLGenerateRequest):
    entry = dataset_store.get(dataset_id)
    if not entry:
        raise HTTPException(status_code=404, detail="Dataset not found.")

    sql = rule_based_nl_to_sql(req.question, entry.current_df, table_name="data")
    if not sql:
        sql = f"SELECT * FROM data LIMIT 10;"
        explanation = "Could not map question precisely; generated default inspection query."
    else:
        explanation = "Rule-based natural language parser mapped terms directly to dataset schema."

    return {
        "generated_sql": sql,
        "explanation": explanation,
        "mode": "rule_based"
    }

