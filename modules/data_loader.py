"""
DataPilot AI - Data Loader Module
Handles multi-format dataset loading (CSV, Excel sheets), 
metadata inspection, memory optimization, and pre-packaged academic datasets.
"""

import os
import io
import pandas as pd
try:
    import streamlit as st
except ImportError:
    st = None
from typing import Dict, List, Tuple, Any, Optional

SAMPLE_DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "sample_data")

AVAILABLE_SAMPLES = {
    "ecommerce_churn": {
        "name": "E-Commerce Customer Churn",
        "filename": "ecommerce_churn.csv",
        "type": "csv",
        "description": "1,542 customers with realistic flaws: missing incomes, casing discrepancies, duplicate records, mixed date formats, and churn target.",
        "badge": "Messy Real-World CSV"
    },
    "employee_attrition": {
        "name": "Employee HR & Attrition",
        "filename": "employee_attrition.xlsx",
        "type": "excel",
        "description": "Multi-sheet Excel workbook with 'Employees' & 'Department_Info' sheets, salary outliers, and department hierarchy.",
        "badge": "Multi-Sheet Excel"
    },
    "patient_health": {
        "name": "Medical Patient Health Risk",
        "filename": "patient_health_risk.csv",
        "type": "csv",
        "description": "1,200 clinical patient records with BMI/BP outliers, continuous risk score (Regression), and diabetic status (Classification).",
        "badge": "Clinical ML Ready"
    },
    "performance_benchmark": {
        "name": "Retail Performance Benchmark (50K)",
        "filename": "performance_benchmark_50k.csv",
        "type": "csv",
        "description": "50,000 sales transactions across 25 stores and 5 regions. Ideal for high-speed DuckDB SQL testing and caching benchmarks.",
        "badge": "Large Dataset (50K)"
    }
}


def get_excel_sheet_names(uploaded_file) -> List[str]:
    """Inspects an uploaded Excel file and returns the list of available sheet names."""
    try:
        excel_file = pd.ExcelFile(uploaded_file)
        return excel_file.sheet_names
    except Exception as e:
        if st is not None:
            st.error(f"Error reading Excel sheets: {str(e)}")
        return []


def load_dataset(file_source: Any, file_type: str = "csv", sheet_name: Optional[str] = None) -> Tuple[Optional[pd.DataFrame], Optional[str]]:
    """
    Robust dataset loader supporting CSV (auto-delimiter and multi-encoding) and Excel.
    Returns (DataFrame, error_message).
    """
    try:
        if file_type == "csv":
            # Attempt with utf-8 first, fallback to latin1/cp1252 if decoding error
            if isinstance(file_source, str):
                df = pd.read_csv(file_source, encoding="utf-8")
            else:
                try:
                    df = pd.read_csv(file_source, encoding="utf-8")
                except UnicodeDecodeError:
                    if hasattr(file_source, "seek"):
                        file_source.seek(0)
                    df = pd.read_csv(file_source, encoding="latin1")

        elif file_type in ["excel", "xlsx", "xls"]:
            if sheet_name:
                df = pd.read_excel(file_source, sheet_name=sheet_name, engine="openpyxl")
            else:
                df = pd.read_excel(file_source, engine="openpyxl")
        else:
            return None, f"Unsupported file type: {file_type}"

        # Standardize column names (strip leading/trailing whitespace in column headers)
        df.columns = [str(col).strip() for col in df.columns]
        return df, None

    except Exception as e:
        return None, str(e)


def load_sample_dataset(sample_key: str, sheet_name: Optional[str] = None) -> Tuple[Optional[pd.DataFrame], Optional[str]]:
    """Loads one of the pre-packaged academic sample datasets from the sample_data directory."""
    if sample_key not in AVAILABLE_SAMPLES:
        return None, f"Sample '{sample_key}' not found."
    
    meta = AVAILABLE_SAMPLES[sample_key]
    file_path = os.path.join(SAMPLE_DATA_DIR, meta["filename"])
    
    if not os.path.exists(file_path):
        return None, f"Sample file not found at: {file_path}"
        
    return load_dataset(file_path, file_type=meta["type"], sheet_name=sheet_name)


def get_dataset_metadata(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Computes comprehensive structural and memory metadata for a dataset.
    Optimized to run fast even on large datasets.
    """
    if df is None or df.empty:
        return {}

    total_rows = len(df)
    total_cols = len(df.columns)
    
    # Memory estimation
    memory_bytes = df.memory_usage(deep=True).sum()
    if memory_bytes < 1024 * 1024:
        memory_str = f"{memory_bytes / 1024:.2f} KB"
    else:
        memory_str = f"{memory_bytes / (1024 * 1024):.2f} MB"

    # Duplicates
    duplicate_rows = int(df.duplicated().sum())
    duplicate_pct = round((duplicate_rows / total_rows) * 100, 2) if total_rows > 0 else 0

    # Missing values
    missing_by_col = df.isnull().sum().to_dict()
    total_missing_cells = sum(missing_by_col.values())
    total_cells = total_rows * total_cols
    missing_pct = round((total_missing_cells / total_cells) * 100, 2) if total_cells > 0 else 0

    # Column Type Classification
    num_cols = list(df.select_dtypes(include=["number"]).columns)
    cat_cols = list(df.select_dtypes(include=["object", "category", "string"]).columns)
    date_cols = list(df.select_dtypes(include=["datetime"]).columns)
    bool_cols = list(df.select_dtypes(include=["bool"]).columns)

    # Health score estimate (0 - 100)
    # Deductions: missing percentage * 1.5, duplicate percentage * 2.0
    deduction = (missing_pct * 1.2) + (duplicate_pct * 1.8)
    health_score = max(10, min(100, int(100 - deduction)))

    return {
        "total_rows": total_rows,
        "total_cols": total_cols,
        "memory_str": memory_str,
        "duplicate_rows": duplicate_rows,
        "duplicate_pct": duplicate_pct,
        "missing_by_col": missing_by_col,
        "total_missing_cells": total_missing_cells,
        "missing_pct": missing_pct,
        "num_cols": num_cols,
        "cat_cols": cat_cols,
        "date_cols": date_cols,
        "bool_cols": bool_cols,
        "health_score": health_score,
        "dtypes": {col: str(dtype) for col, dtype in df.dtypes.items()}
    }


def get_paginated_preview(df: pd.DataFrame, page: int = 1, page_size: int = 15) -> Tuple[pd.DataFrame, int]:
    """
    Returns a small slice of DataFrame for responsive UI rendering, preventing browser lag on large files.
    Returns (paginated_df, total_pages).
    """
    total_rows = len(df)
    total_pages = max(1, (total_rows + page_size - 1) // page_size)
    start_idx = (page - 1) * page_size
    end_idx = min(start_idx + page_size, total_rows)
    return df.iloc[start_idx:end_idx], total_pages
