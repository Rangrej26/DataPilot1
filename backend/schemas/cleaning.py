"""
DataPilot AI - Pydantic Schemas for Smart Data Cleaning
"""

from typing import Dict, List, Any, Optional
from pydantic import BaseModel, Field


class CleaningIssueItem(BaseModel):
    id: str
    issue_type: str
    target_column: Optional[str] = None
    affected_count: int
    what_found: str
    recommended_action: str
    why_it_matters: str
    action_type: str
    default_method: str
    status: str = "pending"  # pending, applied, dismissed


class CleaningIssuesResponse(BaseModel):
    dataset_id: str
    total_issues: int
    issues: List[Dict[str, Any]]
    health_score: int
    duplicate_rows: int
    missing_cells: int


class ApplyFixRequest(BaseModel):
    issue_id: str
    issue_type: str
    target_column: Optional[str] = None
    action: str
    method: Optional[str] = None


class BatchCleanRequest(BaseModel):
    issue_ids: Optional[List[str]] = None


class AuditEntryResponse(BaseModel):
    step: int
    timestamp: str
    issue: str
    target: str
    what_found: str
    what_changed: str
    why: str
    action: str
    method: str
    affected_count: int
    before_state: str
    after_state: str
    risks_limitations: str

