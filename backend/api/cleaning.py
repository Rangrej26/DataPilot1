"""
DataPilot AI - Smart Data Cleaning API Endpoints
"""

from typing import Dict, List, Any, Optional
from fastapi import APIRouter, HTTPException, Body
import pandas as pd

from backend.services.dataset_store import dataset_store
from backend.schemas.cleaning import ApplyFixRequest, BatchCleanRequest
from modules.cleaning_engine import (
    detect_cleaning_issues, apply_remove_duplicates,
    apply_missing_imputation, apply_text_standardization,
    apply_date_parsing, apply_outlier_handling, apply_drop_column,
    get_cleaning_comparison_stats
)

router = APIRouter(prefix="/api/datasets", tags=["Cleaning"])


@router.get("/{dataset_id}/cleaning/issues", summary="Detect all confirmed and review-needed data issues")
async def get_issues(dataset_id: str):
    entry = dataset_store.get(dataset_id)
    if not entry:
        raise HTTPException(status_code=404, detail="Dataset not found.")

    issues = detect_cleaning_issues(entry.current_df)
    meta = entry.get_metadata()

    return {
        "dataset_id": dataset_id,
        "total_issues": len(issues),
        "issues": issues,
        "health_score": meta.get("health_score", 100),
        "duplicate_rows": meta.get("duplicate_rows", 0),
        "missing_cells": meta.get("total_missing_cells", 0),
        "can_undo": entry.cleaning_session.can_undo()
    }


@router.post("/{dataset_id}/cleaning/apply", summary="Apply a single cleaning fix")
async def apply_fix(dataset_id: str, req: ApplyFixRequest):
    entry = dataset_store.get(dataset_id)
    if not entry:
        raise HTTPException(status_code=404, detail="Dataset not found.")

    session = entry.cleaning_session
    success = False
    message = "Unknown cleaning action"

    issue_type = req.issue_type.lower()
    col = req.target_column

    if "duplicate" in issue_type or req.action == "remove_duplicates":
        success, message = apply_remove_duplicates(session)

    elif "missing" in issue_type or req.action == "impute_missing":
        if not col or col not in entry.current_df.columns:
            raise HTTPException(status_code=400, detail=f"Target column '{col}' is invalid.")
        
        is_num = pd.api.types.is_numeric_dtype(entry.current_df[col])
        strategy = req.method or ("median" if is_num else "mode")
        success, message = apply_missing_imputation(session, col, strategy=strategy)

    elif "text" in issue_type or req.action == "standardize_text":
        if not col or col not in entry.current_df.columns:
            raise HTTPException(status_code=400, detail=f"Target column '{col}' is invalid.")
        operation = req.method or "trim_and_title"
        success, message = apply_text_standardization(session, col, operation=operation)

    elif "date" in issue_type or req.action == "parse_dates":
        if not col or col not in entry.current_df.columns:
            raise HTTPException(status_code=400, detail=f"Target column '{col}' is invalid.")
        success, message = apply_date_parsing(session, col)

    elif "outlier" in issue_type or req.action == "handle_outliers":
        if not col or col not in entry.current_df.columns:
            raise HTTPException(status_code=400, detail=f"Target column '{col}' is invalid.")
        method = req.method or "cap"
        success, message = apply_outlier_handling(session, col, method=method)

    elif "drop_column" in issue_type or req.action == "drop_column":
        if not col or col not in entry.current_df.columns:
            raise HTTPException(status_code=400, detail=f"Target column '{col}' is invalid.")
        success, message = apply_drop_column(session, col)

    else:
        raise HTTPException(status_code=400, detail=f"Unrecognized cleaning action: {req.action}")

    if success:
        # Sync working DataFrame and DuckDB table
        entry.current_df = session.current_df
        entry.refresh_sql_engine()
        entry._overview_cache = None  # invalidate cached overview

    return {
        "success": success,
        "message": message,
        "can_undo": session.can_undo(),
        "compact_summary": session.get_compact_summary()
    }


@router.post("/{dataset_id}/cleaning/auto-clean", summary="One-click fix of all confirmed issues")
async def auto_clean_all(dataset_id: str):
    entry = dataset_store.get(dataset_id)
    if not entry:
        raise HTTPException(status_code=404, detail="Dataset not found.")

    session = entry.cleaning_session
    issues = detect_cleaning_issues(entry.current_df)
    
    applied_count = 0
    actions_taken = []

    # 1. Duplicates first
    for iss in issues:
        if iss.get("id") == "duplicates":
            ok, msg = apply_remove_duplicates(session)
            if ok:
                applied_count += 1
                actions_taken.append(msg)

    # Re-detect issues on updated df
    current_issues = detect_cleaning_issues(session.current_df)
    for iss in current_issues:
        iss_id = iss.get("id", "")
        col = iss.get("column")

        # Skip items that require explicit user confirmation
        if iss.get("requires_confirmation", False):
            continue

        if iss_id.startswith("missing_") and col in session.current_df.columns:
            is_num = pd.api.types.is_numeric_dtype(session.current_df[col])
            ok, msg = apply_missing_imputation(session, col, strategy="median" if is_num else "mode")
            if ok:
                applied_count += 1
                actions_taken.append(msg)

        elif iss_id.startswith("text_") and col in session.current_df.columns:
            ok, msg = apply_text_standardization(session, col, operation="trim_and_title")
            if ok:
                applied_count += 1
                actions_taken.append(msg)

        elif iss_id.startswith("date_") and col in session.current_df.columns:
            ok, msg = apply_date_parsing(session, col)
            if ok:
                applied_count += 1
                actions_taken.append(msg)

    # Sync
    entry.current_df = session.current_df
    entry.refresh_sql_engine()
    entry._overview_cache = None

    return {
        "success": True,
        "applied_count": applied_count,
        "actions_taken": actions_taken,
        "can_undo": session.can_undo(),
        "compact_summary": session.get_compact_summary(),
        "comparison": get_cleaning_comparison_stats(entry.raw_df, entry.current_df)
    }


@router.post("/{dataset_id}/cleaning/undo", summary="Undo last cleaning operation")
async def undo_cleaning(dataset_id: str):
    entry = dataset_store.get(dataset_id)
    if not entry:
        raise HTTPException(status_code=404, detail="Dataset not found.")

    session = entry.cleaning_session
    if not session.can_undo():
        raise HTTPException(status_code=400, detail="No transformations available to undo.")

    ok, msg = session.undo_last_step()
    if ok:
        entry.current_df = session.current_df
        entry.refresh_sql_engine()
        entry._overview_cache = None

    return {
        "success": ok,
        "message": msg,
        "can_undo": session.can_undo(),
        "compact_summary": session.get_compact_summary()
    }


@router.post("/{dataset_id}/cleaning/reset", summary="Reset dataset to raw original upload")
async def reset_cleaning(dataset_id: str):
    entry = dataset_store.get(dataset_id)
    if not entry:
        raise HTTPException(status_code=404, detail="Dataset not found.")

    session = entry.cleaning_session
    session.reset_to_original()
    entry.current_df = session.current_df
    entry.refresh_sql_engine()
    entry._overview_cache = None

    return {
        "success": True,
        "message": "Dataset successfully reset to original raw state.",
        "can_undo": session.can_undo(),
        "compact_summary": session.get_compact_summary()
    }


@router.get("/{dataset_id}/cleaning/audit", summary="Get full cleaning audit trail")
async def get_audit_trail(dataset_id: str):
    entry = dataset_store.get(dataset_id)
    if not entry:
        raise HTTPException(status_code=404, detail="Dataset not found.")

    trail = [entry.to_dict() for entry in entry.cleaning_session.audit_trail]
    return {
        "dataset_id": dataset_id,
        "audit_trail": trail,
        "compact_summary": entry.cleaning_session.get_compact_summary(),
        "can_undo": entry.cleaning_session.can_undo()
    }


@router.get("/{dataset_id}/cleaning/comparison", summary="Get before vs after cleaning comparison metrics")
async def get_comparison(dataset_id: str):
    entry = dataset_store.get(dataset_id)
    if not entry:
        raise HTTPException(status_code=404, detail="Dataset not found.")

    stats = get_cleaning_comparison_stats(entry.raw_df, entry.current_df)
    return {
        "dataset_id": dataset_id,
        "comparison": stats
    }
