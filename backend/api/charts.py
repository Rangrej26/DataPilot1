"""
DataPilot AI - Beginner-Friendly Chart Guide API Endpoints
"""

import json
from typing import Dict, List, Any, Optional
from fastapi import APIRouter, HTTPException, Query

from backend.services.dataset_store import dataset_store
from backend.schemas.charts import RenderChartRequest, RenderChartResponse
from modules.chart_guide import (
    ANALYTICAL_GOALS, get_chart_recommendations,
    generate_guided_chart, derive_chart_insights,
    inspect_dataset_for_visualization
)

router = APIRouter(prefix="/api/datasets", tags=["Chart Guide"])


@router.get("/charts/goals", summary="List all supported analytical charting goals")
async def get_chart_goals():
    return {
        "goals": [
            {
                "key": key,
                "title": info["title"],
                "description": info["description"],
                "icon": info["icon"],
                "example": info["example"]
            }
            for key, info in ANALYTICAL_GOALS.items()
        ]
    }


@router.get("/{dataset_id}/charts/recommendations", summary="Get tailored chart recommendations for a goal")
async def get_recommendations(
    dataset_id: str,
    goal: str = Query(default="compare_categories")
):
    entry = dataset_store.get(dataset_id)
    if not entry:
        raise HTTPException(status_code=404, detail="Dataset not found.")

    if goal not in ANALYTICAL_GOALS:
        goal = "compare_categories"

    goal_info = ANALYTICAL_GOALS[goal]
    rec_data = get_chart_recommendations(entry.current_df, goal)
    inspection = inspect_dataset_for_visualization(entry.current_df)

    return {
        "dataset_id": dataset_id,
        "goal_key": goal,
        "goal_title": goal_info["title"],
        "goal_description": goal_info["description"],
        "recommendations": rec_data.get("recommendations", []),
        "available_numerical": inspection["num_cols"],
        "available_categorical": inspection["cat_cols"],
        "available_dates": inspection["date_cols"] + inspection["potential_dates"]
    }


@router.post("/{dataset_id}/charts/render", summary="Render interactive Plotly chart with grounded interpretations")
async def render_chart(dataset_id: str, req: RenderChartRequest):
    entry = dataset_store.get(dataset_id)
    if not entry:
        raise HTTPException(status_code=404, detail="Dataset not found.")

    df = entry.current_df
    res = generate_guided_chart(
        df=df,
        chart_type=req.chart_type,
        x_col=req.x_col,
        y_col=req.y_col,
        agg_func=req.agg_func or "mean",
        color_col=req.color_col,
        theme_name="Professional SaaS"
    )

    fig = getattr(res, "fig", None)
    err = getattr(res, "err", None)

    if fig is None and hasattr(res, "__getitem__"):
        try:
            fig = res[0]
        except Exception:
            pass

    if fig is None:
        raise HTTPException(status_code=400, detail=f"Failed to generate chart: {err or 'Unknown error'}")

    # Derive mathematically grounded observations
    observations = derive_chart_insights(
        df=df,
        chart_type=req.chart_type,
        x_col=req.x_col,
        y_col=req.y_col,
        agg_func=req.agg_func or "mean",
        color_col=req.color_col
    )

    return {
        "dataset_id": dataset_id,
        "chart_type": req.chart_type,
        "x_col": req.x_col,
        "y_col": req.y_col,
        "figure": json.loads(fig.to_json()),
        "observations": observations
    }

