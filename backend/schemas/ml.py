"""
DataPilot AI - Pydantic Schemas for Machine Learning Lab
"""

from typing import Dict, List, Any, Optional
from pydantic import BaseModel, Field


class TargetInspectionResponse(BaseModel):
    target_col: str
    task_type: str
    description: str
    is_valid: bool
    unique_count: int
    missing_count: int
    classes: Optional[List[str]] = None
    class_distribution: Optional[Dict[str, int]] = None
    numeric_min: Optional[float] = None
    numeric_max: Optional[float] = None
    numeric_median: Optional[float] = None
    leakage_warnings: List[Dict[str, Any]]
    candidate_features: List[str]
    smart_default_features: List[str]


class MLTrainRequest(BaseModel):
    target_col: str
    feature_cols: List[str]
    task_type: str  # Classification or Regression
    test_size: Optional[float] = Field(default=0.2, ge=0.1, le=0.5)
    selected_models: Optional[List[str]] = None


class MLTrainResponse(BaseModel):
    success: bool
    task_type: str
    target_col: str
    best_model_name: Optional[str] = None
    leaderboard: List[Dict[str, Any]]
    training_sample_count: int
    test_sample_count: int
    features_used: List[str]
    confusion_matrix_fig: Optional[Dict[str, Any]] = None
    regression_plot_fig: Optional[Dict[str, Any]] = None
    feature_importance_fig: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


class MLPredictRequest(BaseModel):
    inputs: Dict[str, Any]
    model_name: Optional[str] = None


class MLPredictResponse(BaseModel):
    success: bool
    prediction: Any
    model_used: str
    task_type: str
    probabilities: Optional[Dict[str, float]] = None
    error: Optional[str] = None

