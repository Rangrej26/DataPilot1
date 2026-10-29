"""
DataPilot AI - Dataset Management & Exploration API Endpoints
"""

import io
import json
from typing import Dict, List, Any, Optional
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Query
from fastapi.responses import JSONResponse
import pandas as pd

from backend.core.config import MAX_UPLOAD_SIZE_MB
from backend.services.dataset_store import dataset_store
from backend.schemas.datasets import (
    DatasetItem, DatasetPreviewResponse, DatasetOverviewResponse,
    ContextUpdateRequest, LoadSampleRequest
)
from modules.data_loader import (
    load_dataset, AVAILABLE_SAMPLES, get_excel_sheet_names
)
from modules.profiler import (
    get_numerical_summary, get_categorical_summary,
    plot_correlation_heatmap, plot_missing_values, plot_column_distribution
)

router = APIRouter(prefix="/api/datasets", tags=["Datasets"])


@router.get("/samples", summary="List available academic sample datasets")
async def get_sample_datasets():
    return {
        "samples": [
            {
                "key": key,
                "name": info["name"],
                "type": info["type"],
                "badge": info["badge"],
                "description": info["description"]
            }
            for key, info in AVAILABLE_SAMPLES.items()
        ]
    }


@router.post("/load-sample", summary="Load a pre-packaged sample dataset")
async def load_sample(req: LoadSampleRequest):
    entry = dataset_store.load_sample(req.sample_key, sheet_name=req.sheet_name)
    if not entry:
        raise HTTPException(status_code=404, detail=f"Sample '{req.sample_key}' could not be loaded.")
    
    return {
        "success": True,
        "message": f"Successfully loaded sample dataset: {entry.name}",
        "dataset": entry.to_summary_dict()
    }


@router.post("/upload", summary="Upload CSV or Excel dataset")
async def upload_dataset(
    file: UploadFile = File(...),
    sheet_name: Optional[str] = Form(None)
):
    if not file.filename:
        raise HTTPException(status_code=400, detail="Filename cannot be empty.")

    filename = file.filename
    lower_name = filename.lower()
    
    if not (lower_name.endswith(".csv") or lower_name.endswith(".xlsx") or lower_name.endswith(".xls")):
        raise HTTPException(
            status_code=400,
            detail="Unsupported file format. Please upload a CSV (.csv) or Excel spreadsheet (.xlsx, .xls)."
        )

    file_bytes = await file.read()
    size_mb = len(file_bytes) / (1024 * 1024)
    if size_mb > MAX_UPLOAD_SIZE_MB:
        raise HTTPException(
            status_code=413,
            detail=f"File exceeds maximum upload size of {MAX_UPLOAD_SIZE_MB}MB (current size: {size_mb:.1f}MB)."
        )

    buffer = io.BytesIO(file_bytes)
    file_type = "csv" if lower_name.endswith(".csv") else "excel"
    available_sheets = []

    if file_type == "excel":
        available_sheets = get_excel_sheet_names(buffer)
        buffer.seek(0)
        # If user did not specify sheet, default to first sheet
        if not sheet_name and available_sheets:
            sheet_name = available_sheets[0]

    df, err = load_dataset(buffer, file_type=file_type, sheet_name=sheet_name)
    if df is None:
        raise HTTPException(status_code=400, detail=f"Failed to parse uploaded dataset: {err}")

    if df.empty or len(df.columns) == 0:
        raise HTTPException(status_code=400, detail="The uploaded file contains no data or no columns.")

    clean_name = filename.rsplit(".", 1)[0]
    entry = dataset_store.create(
        name=clean_name,
        df=df,
        file_type=file_type,
        sheet_name=sheet_name,
        available_sheets=available_sheets
    )

    return {
        "success": True,
        "message": f"Uploaded and indexed '{filename}' successfully.",
        "dataset": entry.to_summary_dict(),
        "available_sheets": available_sheets
    }


@router.get("", summary="List all active datasets in current session")
async def list_datasets():
    return {"datasets": dataset_store.list_all()}


@router.get("/{dataset_id}", summary="Get dataset summary and health metrics")
async def get_dataset(dataset_id: str):
    entry = dataset_store.get(dataset_id)
    if not entry:
        raise HTTPException(status_code=404, detail="Dataset not found or session has expired.")
    return entry.to_summary_dict()


@router.delete("/{dataset_id}", summary="Delete dataset from session")
async def delete_dataset(dataset_id: str):
    deleted = dataset_store.delete(dataset_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Dataset not found.")
    return {"success": True, "message": "Dataset deleted successfully."}


@router.get("/{dataset_id}/preview", summary="Get paginated data preview")
async def get_preview(
    dataset_id: str,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=15, ge=5, le=100),
    search: Optional[str] = Query(default=None)
):
    entry = dataset_store.get(dataset_id)
    if not entry:
        raise HTTPException(status_code=404, detail="Dataset not found.")

    df = entry.current_df

    if search:
        s = search.strip().lower()
        # Filter rows where any string column contains the search term
        mask = df.astype(str).apply(lambda row: row.str.lower().str.contains(s, regex=False)).any(axis=1)
        df_filtered = df[mask]
    else:
        df_filtered = df

    total_rows = len(df_filtered)
    total_pages = max(1, (total_rows + page_size - 1) // page_size)
    page = min(page, total_pages)
    
    start_idx = (page - 1) * page_size
    end_idx = min(start_idx + page_size, total_rows)
    slice_df = df_filtered.iloc[start_idx:end_idx]

    # Convert non-serializable objects (timestamps, NaNs) cleanly
    records = json.loads(slice_df.to_json(orient="records", date_format="iso"))

    return {
        "dataset_id": dataset_id,
        "dataset_name": entry.name,
        "page": page,
        "page_size": page_size,
        "total_pages": total_pages,
        "total_rows": total_rows,
        "total_dataset_rows": len(df),
        "columns": list(df.columns),
        "dtypes": {c: str(d) for c, d in df.dtypes.items()},
        "rows": records
    }


@router.get("/{dataset_id}/profile", summary="Get extended statistical profiles")
async def get_profile(dataset_id: str):
    entry = dataset_store.get(dataset_id)
    if not entry:
        raise HTTPException(status_code=404, detail="Dataset not found.")

    df = entry.current_df
    num_sum = get_numerical_summary(df)
    cat_sum = get_categorical_summary(df)

    num_records = json.loads(num_sum.to_json(orient="records")) if not num_sum.empty else []
    cat_records = json.loads(cat_sum.to_json(orient="records")) if not cat_sum.empty else []

    return {
        "dataset_id": dataset_id,
        "metadata": entry.get_metadata(),
        "numerical_summary": num_records,
        "categorical_summary": cat_records
    }


@router.get("/{dataset_id}/overview", summary="Get intelligent dataset understanding and semantic column dictionary")
async def get_overview(dataset_id: str):
    entry = dataset_store.get(dataset_id)
    if not entry:
        raise HTTPException(status_code=404, detail="Dataset not found.")

    overview = entry.get_overview()
    meta = entry.get_metadata()

    return {
        "dataset_id": dataset_id,
        "domain": overview.get("domain", "General Dataset"),
        "inferred_subject": overview.get("inferred_subject", "Data Records"),
        "dataset_description": overview.get("dataset_description", ""),
        "key_findings": overview.get("key_findings", []),
        "column_dictionary": overview.get("column_dictionary", []),
        "analysis_suggestions": overview.get("analysis_suggestions", []),
        "user_context": entry.user_context,
        "total_rows": meta.get("total_rows", 0),
        "total_cols": meta.get("total_cols", 0),
        "numeric_count": len(meta.get("num_cols", [])),
        "categorical_count": len(meta.get("cat_cols", [])),
        "datetime_count": len(meta.get("date_cols", []))
    }


@router.post("/{dataset_id}/overview/context", summary="Update background context for dataset")
async def update_context(dataset_id: str, req: ContextUpdateRequest):
    entry = dataset_store.get(dataset_id)
    if not entry:
        raise HTTPException(status_code=404, detail="Dataset not found.")

    overview = entry.get_overview(user_context=req.context)
    return {
        "success": True,
        "message": "Dataset background context updated successfully.",
        "dataset_description": overview.get("dataset_description", "")
    }


@router.get("/{dataset_id}/visualizations/correlation", summary="Get Plotly correlation heatmap")
async def get_correlation_vis(
    dataset_id: str,
    method: str = Query(default="pearson", pattern="^(pearson|spearman)$")
):
    entry = dataset_store.get(dataset_id)
    if not entry:
        raise HTTPException(status_code=404, detail="Dataset not found.")

    fig = plot_correlation_heatmap(entry.current_df, method=method, theme_name="Professional SaaS")
    if fig is None:
        return {"has_figure": False, "message": "At least 2 numerical features are required for correlation analysis."}

    return {"has_figure": True, "figure": json.loads(fig.to_json())}


@router.get("/{dataset_id}/visualizations/missing", summary="Get Plotly missing values chart")
async def get_missing_vis(dataset_id: str):
    entry = dataset_store.get(dataset_id)
    if not entry:
        raise HTTPException(status_code=404, detail="Dataset not found.")

    fig = plot_missing_values(entry.current_df, theme_name="Professional SaaS")
    if fig is None:
        return {"has_figure": False, "message": "No missing values detected in the current dataset."}

    return {"has_figure": True, "figure": json.loads(fig.to_json())}


@router.get("/{dataset_id}/visualizations/distribution", summary="Get single column distribution chart")
async def get_distribution_vis(dataset_id: str, column: str = Query(...)):
    entry = dataset_store.get(dataset_id)
    if not entry:
        raise HTTPException(status_code=404, detail="Dataset not found.")

    if column not in entry.current_df.columns:
        raise HTTPException(status_code=400, detail=f"Column '{column}' does not exist.")

    fig = plot_column_distribution(entry.current_df, column, theme_name="Professional SaaS")
    if fig is None:
        return {"has_figure": False, "message": "Unable to generate distribution plot."}

    return {"has_figure": True, "figure": json.loads(fig.to_json())}
