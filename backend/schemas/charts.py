"""
DataPilot AI - Pydantic Schemas for Chart Guide & Visualizations
"""

from typing import Dict, List, Any, Optional
from pydantic import BaseModel, Field


class GoalInfo(BaseModel):
    key: str
    title: str
    description: str
    icon: str
    example: str


class ChartRecommendationItem(BaseModel):
    chart_type: str
    badge: str
    suggested_x: Optional[str] = None
    suggested_y: Optional[str] = None
    suggested_agg: Optional[str] = None
    suggested_color: Optional[str] = None
    why_useful: str
    columns_needed: str
    axes_explanation: str
    what_to_look_for: str
    when_to_avoid: str


class ChartRecommendationsResponse(BaseModel):
    dataset_id: str
    goal_key: str
    goal_title: str
    recommendations: List[Dict[str, Any]]
    available_numerical: List[str]
    available_categorical: List[str]
    available_dates: List[str]


class RenderChartRequest(BaseModel):
    chart_type: str
    x_col: Optional[str] = None
    y_col: Optional[str] = None
    agg_func: Optional[str] = "mean"
    color_col: Optional[str] = None
    theme: Optional[str] = "Professional SaaS"


class RenderChartResponse(BaseModel):
    dataset_id: str
    chart_type: str
    figure: Dict[str, Any]  # Plotly figure JSON
    observations: List[str]  # Grounded mathematical findings
    x_col: Optional[str] = None
    y_col: Optional[str] = None

