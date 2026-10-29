"""
DataPilot AI - Reports & Exports API Endpoints
"""

import io
import re
from typing import Dict, List, Any, Optional
from fastapi import APIRouter, HTTPException, Response, Body
from fastapi.responses import StreamingResponse
import pandas as pd

from backend.services.dataset_store import dataset_store
from modules.report_generator import generate_pdf_report, generate_excel_dossier
from modules.profiler import get_numerical_summary
from modules.insights_engine import generate_comprehensive_insights

router = APIRouter(prefix="/api/datasets", tags=["Reports & Exports"])


@router.get("/{dataset_id}/reports/csv", summary="Download cleaned dataset as CSV")
async def download_csv(dataset_id: str):
    entry = dataset_store.get(dataset_id)
    if not entry:
        raise HTTPException(status_code=404, detail="Dataset not found.")

    csv_data = entry.current_df.to_csv(index=False)
    filename = f"cleaned_{re.sub(r'[^a-zA-Z0-9_]', '_', entry.name).lower()}.csv"

    return Response(
        content=csv_data,
        media_type="text/csv",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'}
    )


@router.get("/{dataset_id}/reports/excel", summary="Download academic multi-tab Excel dossier")
async def download_excel(dataset_id: str):
    entry = dataset_store.get(dataset_id)
    if not entry:
        raise HTTPException(status_code=404, detail="Dataset not found.")

    num_summary = get_numerical_summary(entry.current_df)
    ml_results = entry.ml_pipeline.model_results if entry.ml_pipeline else None
    overview = entry.get_overview()

    excel_bytes = generate_excel_dossier(
        cleaned_df=entry.current_df,
        audit_trail=entry.cleaning_session.audit_trail,
        numerical_summary=num_summary,
        ml_results=ml_results,
        dataset_overview=overview
    )

    filename = f"datapilot_dossier_{re.sub(r'[^a-zA-Z0-9_]', '_', entry.name).lower()}.xlsx"

    return Response(
        content=excel_bytes,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'}
    )


@router.get("/{dataset_id}/reports/pdf", summary="Download ReportLab academic PDF analytical dossier")
async def download_pdf(dataset_id: str):
    entry = dataset_store.get(dataset_id)
    if not entry:
        raise HTTPException(status_code=404, detail="Dataset not found.")

    meta = entry.get_metadata()
    overview = entry.get_overview()
    insights = generate_comprehensive_insights(entry.current_df)
    ml_results = entry.ml_pipeline.model_results if entry.ml_pipeline else None

    pdf_bytes = generate_pdf_report(
        metadata=meta,
        audit_trail=entry.cleaning_session.audit_trail,
        insights=insights,
        ml_results=ml_results,
        dataset_overview=overview
    )

    filename = f"datapilot_academic_report_{re.sub(r'[^a-zA-Z0-9_]', '_', entry.name).lower()}.pdf"

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'}
    )


@router.post("/{dataset_id}/reports/sql-csv", summary="Download SQL query results as CSV")
async def download_sql_csv(dataset_id: str, payload: Dict[str, str] = Body(...)):
    entry = dataset_store.get(dataset_id)
    if not entry:
        raise HTTPException(status_code=404, detail="Dataset not found.")

    query = payload.get("query", "").strip()
    if not query:
        raise HTTPException(status_code=400, detail="SQL query cannot be empty.")

    res_df, elapsed, err = entry.sql_engine.execute_query(query, max_rows=10000)
    if err or res_df is None:
        raise HTTPException(status_code=400, detail=f"Query failed: {err}")

    csv_data = res_df.to_csv(index=False)
    filename = f"sql_results_{re.sub(r'[^a-zA-Z0-9_]', '_', entry.name).lower()}.csv"

    return Response(
        content=csv_data,
        media_type="text/csv",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'}
    )

