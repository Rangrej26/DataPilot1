"""
DataPilot AI - Pydantic Schemas for Dataset Ingestion & Profiling
"""

from typing import Dict, List, Any, Optional
from pydantic import BaseModel, Field


class DatasetItem(BaseModel):
    id: str
    name: str
    file_type: str
    total_rows: int
    total_cols: int
    memory_str: str
    health_score: int
    created_at: float
    sheet_name: Optional[str] = None
    available_sheets: List[str] = Field(default_factory=list)


class DatasetPreviewResponse(BaseModel):
    dataset_id: str
    dataset_name: str
    page: int
    page_size: int
    total_pages: int
    total_rows: int
    columns: List[str]
    dtypes: Dict[str, str]
    rows: List[Dict[str, Any]]


class ColumnDictionaryItem(BaseModel):
    column_name: str
    programmatic_type: str
    inferred_semantic_meaning: str
    example_value: str
    missing_count: int
    is_confident: bool


class DatasetOverviewResponse(BaseModel):
    dataset_id: str
    domain: str
    inferred_subject: str
    dataset_description: str
    key_findings: List[str]
    column_dictionary: List[Dict[str, Any]]
    analysis_suggestions: List[Dict[str, Any]]
    user_context: Optional[str] = None
    total_rows: int
    total_cols: int
    numeric_count: int
    categorical_count: int
    datetime_count: int


class ContextUpdateRequest(BaseModel):
    context: str = Field(..., max_length=2000)


class LoadSampleRequest(BaseModel):
    sample_key: str
    sheet_name: Optional[str] = None


class ExcelSheetListResponse(BaseModel):
    dataset_id: str
    sheets: List[str]

