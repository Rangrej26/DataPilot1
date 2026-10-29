"""
DataPilot AI - Machine Learning Lab API Endpoints
"""

import json
from typing import Dict, List, Any, Optional
from fastapi import APIRouter, HTTPException, Query
import pandas as pd

from backend.services.dataset_store import dataset_store
from backend.schemas.ml import (
    MLTrainRequest, MLPredictRequest, TargetInspectionResponse
)
from modules.ml_lab import (
    auto_detect_ml_task, check_target_leakage,
    MLTrainingPipeline, get_available_models
)

router = APIRouter(prefix="/api/datasets", tags=["Machine Learning Lab"])


@router.get("/{dataset_id}/ml/schema", summary="Get ML schema: columns and types")
async def get_ml_schema(dataset_id: str):
    entry = dataset_store.get(dataset_id)
    if not entry:
        raise HTTPException(status_code=404, detail="Dataset not found.")

    df = entry.current_df
    num_cols = list(df.select_dtypes(include=["number"]).columns)
    cat_cols = list(df.select_dtypes(include=["object", "category", "string", "bool"]).columns)

    return {
        "dataset_id": dataset_id,
        "total_rows": len(df),
        "columns": list(df.columns),
        "numerical_columns": num_cols,
        "categorical_columns": cat_cols,
        "default_target": df.columns[-1] if len(df.columns) > 0 else None
    }


@router.get("/{dataset_id}/ml/inspect-target", summary="Inspect target column and detect task")
async def inspect_target(dataset_id: str, target: str = Query(...)):
    entry = dataset_store.get(dataset_id)
    if not entry:
        raise HTTPException(status_code=404, detail="Dataset not found.")

    df = entry.current_df
    if target not in df.columns:
        raise HTTPException(status_code=400, detail=f"Column '{target}' does not exist in dataset.")

    task_type, desc = auto_detect_ml_task(df, target)
    is_valid = task_type in ["Classification", "Regression"]

    series = df[target].dropna()
    unique_cnt = int(series.nunique())
    missing_cnt = int(df[target].isnull().sum())

    classes = None
    class_dist = None
    num_min = None
    num_max = None
    num_med = None

    if task_type == "Classification" or (not pd.api.types.is_numeric_dtype(series) and unique_cnt <= 25):
        top_cats = series.value_counts().head(10).to_dict()
        classes = [str(k) for k in top_cats.keys()]
        class_dist = {str(k): int(v) for k, v in top_cats.items()}
    elif pd.api.types.is_numeric_dtype(series):
        num_min = round(float(series.min()), 2)
        num_max = round(float(series.max()), 2)
        num_med = round(float(series.median()), 2)

    candidate_features = [c for c in df.columns if c != target]
    leakage = check_target_leakage(df, target, candidate_features)

    # Smart defaults: exclude IDs, tracking codes, names, and single-value columns
    smart_defaults = [
        c for c in candidate_features
        if not any(k in c.lower() for k in ["_id", "id", "code", "name", "token", "uuid"])
        and 1 < df[c].nunique() <= 100
    ]
    if not smart_defaults:
        smart_defaults = candidate_features[:8]

    return {
        "target_col": target,
        "task_type": task_type,
        "description": desc,
        "is_valid": is_valid,
        "unique_count": unique_cnt,
        "missing_count": missing_cnt,
        "classes": classes,
        "class_distribution": class_dist,
        "numeric_min": num_min,
        "numeric_max": num_max,
        "numeric_median": num_med,
        "leakage_warnings": leakage,
        "candidate_features": candidate_features,
        "smart_default_features": smart_defaults,
        "available_models": get_available_models(task_type if is_valid else "Classification")
    }


@router.post("/{dataset_id}/ml/train", summary="Train baseline models and evaluate performance")
async def train_ml(dataset_id: str, req: MLTrainRequest):
    entry = dataset_store.get(dataset_id)
    if not entry:
        raise HTTPException(status_code=404, detail="Dataset not found.")

    df = entry.current_df
    if req.target_col not in df.columns:
        raise HTTPException(status_code=400, detail=f"Target column '{req.target_col}' not found.")

    if not req.feature_cols:
        raise HTTPException(status_code=400, detail="Please select at least one feature column for training.")

    pipeline = MLTrainingPipeline(
        df=df,
        target_col=req.target_col,
        feature_cols=req.feature_cols,
        task_type=req.task_type,
        test_size=req.test_size or 0.2
    )

    ok, err = pipeline.prepare_data()
    if not ok:
        raise HTTPException(status_code=400, detail=f"Data preparation error: {err}")

    results = pipeline.train_and_compare(selected_models=req.selected_models)
    if not results:
        raise HTTPException(status_code=400, detail=f"Training failed: {pipeline.model_errors}")

    # Store trained pipeline on the dataset entry for live predictions
    entry.ml_pipeline = pipeline

    # Generate diagnostic plots
    cm_json = None
    reg_json = None
    if pipeline.task_type == "Classification":
        cm_fig = pipeline.get_confusion_matrix_plot(theme_name="Professional SaaS")
        if cm_fig:
            cm_json = json.loads(cm_fig.to_json())
    else:
        reg_fig = pipeline.get_regression_prediction_plot(theme_name="Professional SaaS")
        if reg_fig:
            reg_json = json.loads(reg_fig.to_json())

    imp_fig = pipeline.get_feature_importance_plot(theme_name="Professional SaaS")
    imp_json = json.loads(imp_fig.to_json()) if imp_fig else None

    # Compute sample feature inputs with min/max/default for the prediction UI
    feature_specs = {}
    for f in pipeline.feature_cols:
        s = df[f].dropna()
        if pd.api.types.is_numeric_dtype(s):
            feature_specs[f] = {
                "type": "numeric",
                "min": round(float(s.min()), 2),
                "max": round(float(s.max()), 2),
                "median": round(float(s.median()), 2),
                "default": round(float(s.median()), 2)
            }
        else:
            cats = [str(x) for x in s.unique() if pd.notnull(x)][:25]
            feature_specs[f] = {
                "type": "categorical",
                "options": cats if cats else ["Unknown"],
                "default": cats[0] if cats else "Unknown"
            }

    return {
        "success": True,
        "task_type": pipeline.task_type,
        "target_col": pipeline.target_col,
        "best_model_name": pipeline.best_model_name,
        "leaderboard": results,
        "training_sample_count": len(pipeline.X_train_raw) if pipeline.X_train_raw is not None else 0,
        "test_sample_count": len(pipeline.X_test_raw) if pipeline.X_test_raw is not None else 0,
        "features_used": pipeline.feature_cols,
        "feature_specs": feature_specs,
        "confusion_matrix_fig": cm_json,
        "regression_plot_fig": reg_json,
        "feature_importance_fig": imp_json
    }


@router.post("/{dataset_id}/ml/predict", summary="Run interactive live inference on trained model")
async def run_prediction(dataset_id: str, req: MLPredictRequest):
    entry = dataset_store.get(dataset_id)
    if not entry:
        raise HTTPException(status_code=404, detail="Dataset not found.")

    pipeline = entry.ml_pipeline
    if not pipeline or not pipeline.trained_models:
        raise HTTPException(
            status_code=400,
            detail="No trained model available. You must successfully train a model first before running live predictions."
        )

    res = pipeline.predict_single_instance(req.inputs, model_name=req.model_name)
    if "error" in res:
        raise HTTPException(status_code=400, detail=res["error"])

    return {
        "success": True,
        "prediction": res.get("prediction"),
        "model_used": res.get("model_used"),
        "task_type": res.get("task_type"),
        "probabilities": res.get("probabilities")
    }

