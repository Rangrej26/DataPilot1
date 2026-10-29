"""
Automated unit tests for modules.data_loader
"""

import os
import pytest

import pandas as pd
from modules.data_loader import (
    load_sample_dataset, get_dataset_metadata, get_paginated_preview
)

def test_load_ecommerce_csv():
    df, err = load_sample_dataset("ecommerce_churn")
    assert err is None, f"Failed with error: {err}"
    assert df is not None
    assert len(df) > 1000
    assert "Customer_ID" in df.columns
    assert "Age" in df.columns

def test_load_employee_excel_sheets():
    df_emp, err1 = load_sample_dataset("employee_attrition", sheet_name="Employees")
    assert err1 is None
    assert df_emp is not None
    assert "Monthly_Salary" in df_emp.columns

    df_dept, err2 = load_sample_dataset("employee_attrition", sheet_name="Department_Info")
    assert err2 is None
    assert df_dept is not None
    assert "Cost_Center" in df_dept.columns

def test_metadata_computation():
    df, _ = load_sample_dataset("ecommerce_churn")
    meta = get_dataset_metadata(df)
    assert meta["total_rows"] == len(df)
    assert meta["total_cols"] == len(df.columns)
    assert meta["duplicate_rows"] > 0
    assert meta["total_missing_cells"] > 0
    assert 0 <= meta["health_score"] <= 100

def test_pagination():
    df, _ = load_sample_dataset("ecommerce_churn")
    page_slice, total_pages = get_paginated_preview(df, page=1, page_size=20)
    assert len(page_slice) == 20
    assert total_pages == (len(df) + 19) // 20
