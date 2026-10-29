"""
Automated Integration Tests for DataPilot AI FastAPI Endpoints
Tests all core API routes: Datasets, Profiling, Cleaning, Charts,
SQL Sandbox, AI Analyst, ML Lab, and Reports.
"""

import pytest
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)


def test_health_check():
    res = client.get("/api/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "healthy"
    assert "version" in data


def test_settings_theme_palette():
    res = client.get("/api/settings")
    assert res.status_code == 200
    data = res.json()
    assert "theme" in data
    assert data["theme"]["sidebar_bg"] == "#222225"
    assert data["theme"]["workspace_bg"] == "#E8E8E8"
    assert data["theme"]["primary_accent"] == "#D8F45B"
    assert data["theme"]["secondary_accent"] == "#B9ADF5"


def test_sample_datasets_and_load():
    # 1. List samples
    res = client.get("/api/datasets/samples")
    assert res.status_code == 200
    samples = res.json().get("samples", [])
    assert len(samples) >= 4

    # 2. Load e-commerce sample
    load_res = client.post("/api/datasets/load-sample", json={"sample_key": "ecommerce_churn"})
    assert load_res.status_code == 200
    dataset = load_res.json()["dataset"]
    dataset_id = dataset["id"]
    assert dataset["total_rows"] > 1000

    # 3. Preview
    prev_res = client.get(f"/api/datasets/{dataset_id}/preview?page=1&page_size=10")
    assert prev_res.status_code == 200
    prev_data = prev_res.json()
    assert len(prev_data["rows"]) == 10
    assert len(prev_data["columns"]) > 5

    # 4. Overview
    overview_res = client.get(f"/api/datasets/{dataset_id}/overview")
    assert overview_res.status_code == 200
    ov_data = overview_res.json()
    assert "dataset_description" in ov_data
    assert len(ov_data["column_dictionary"]) > 0

    # 5. Visualizations
    corr_res = client.get(f"/api/datasets/{dataset_id}/visualizations/correlation?method=pearson")
    assert corr_res.status_code == 200
    assert corr_res.json()["has_figure"] is True

    miss_res = client.get(f"/api/datasets/{dataset_id}/visualizations/missing")
    assert miss_res.status_code == 200
    assert miss_res.json()["has_figure"] is True


def test_cleaning_workflow():
    # Load dataset with injected flaws
    load_res = client.post("/api/datasets/load-sample", json={"sample_key": "ecommerce_churn"})
    dataset_id = load_res.json()["dataset"]["id"]

    # 1. Detect issues
    issues_res = client.get(f"/api/datasets/{dataset_id}/cleaning/issues")
    assert issues_res.status_code == 200
    issues_data = issues_res.json()
    assert issues_data["total_issues"] > 0

    # 2. Auto-clean all confirmed issues
    clean_res = client.post(f"/api/datasets/{dataset_id}/cleaning/auto-clean")
    assert clean_res.status_code == 200
    clean_data = clean_res.json()
    assert clean_data["applied_count"] > 0
    assert clean_data["can_undo"] is True

    # 3. Verify audit trail
    audit_res = client.get(f"/api/datasets/{dataset_id}/cleaning/audit")
    assert audit_res.status_code == 200
    assert len(audit_res.json()["audit_trail"]) > 0

    # 4. Undo
    undo_res = client.post(f"/api/datasets/{dataset_id}/cleaning/undo")
    assert undo_res.status_code == 200
    assert undo_res.json()["success"] is True

    # 5. Reset
    reset_res = client.post(f"/api/datasets/{dataset_id}/cleaning/reset")
    assert reset_res.status_code == 200
    assert reset_res.json()["success"] is True


def test_chart_guide_recommendations_and_render():
    load_res = client.post("/api/datasets/load-sample", json={"sample_key": "patient_health"})
    dataset_id = load_res.json()["dataset"]["id"]

    # 1. Goals
    goals_res = client.get("/api/datasets/charts/goals")
    assert goals_res.status_code == 200
    assert len(goals_res.json()["goals"]) >= 5

    # 2. Recommendations for compare_categories
    rec_res = client.get(f"/api/datasets/{dataset_id}/charts/recommendations?goal=compare_categories")
    assert rec_res.status_code == 200
    recs = rec_res.json()["recommendations"]
    assert len(recs) > 0

    # 3. Render chart
    render_res = client.post(f"/api/datasets/{dataset_id}/charts/render", json={
        "chart_type": "Bar Chart",
        "x_col": "Smoking_Status",
        "y_col": "Health_Risk_Score",
        "agg_func": "mean"
    })
    assert render_res.status_code == 200
    r_data = render_res.json()
    assert "figure" in r_data
    assert len(r_data["observations"]) > 0


def test_sql_assistant_sandbox_and_execution():
    load_res = client.post("/api/datasets/load-sample", json={"sample_key": "patient_health"})
    dataset_id = load_res.json()["dataset"]["id"]

    # 1. Safe query execution
    sql_res = client.post(f"/api/datasets/{dataset_id}/sql/execute", json={
        "query": "SELECT Smoking_Status, ROUND(AVG(Health_Risk_Score), 2) AS avg_risk FROM data GROUP BY Smoking_Status ORDER BY avg_risk DESC;"
    })
    assert sql_res.status_code == 200
    data = sql_res.json()
    assert data["success"] is True
    assert len(data["rows"]) > 0
    assert data["execution_time_ms"] >= 0

    # 2. Block malicious query in security sandbox
    bad_res = client.post(f"/api/datasets/{dataset_id}/sql/execute", json={
        "query": "DROP TABLE data;"
    })
    assert bad_res.status_code == 200
    assert bad_res.json()["success"] is False
    assert "Security Sandbox Notice" in bad_res.json()["error"]

    # 3. Explain query
    explain_res = client.post(f"/api/datasets/{dataset_id}/sql/explain", json={
        "query": "SELECT * FROM data WHERE Age > 50 LIMIT 5;"
    })
    assert explain_res.status_code == 200
    assert "SELECT Clause" in explain_res.json()["clauses"]


def test_ai_data_analyst():
    load_res = client.post("/api/datasets/load-sample", json={"sample_key": "patient_health"})
    dataset_id = load_res.json()["dataset"]["id"]

    res = client.post(f"/api/datasets/{dataset_id}/analyst/ask", json={
        "question": "What is the correlation between BMI and Blood Pressure?"
    })
    assert res.status_code == 200
    data = res.json()
    assert len(data["primary_finding"]) > 0
    assert "calculation_details" in data
    assert "mode" in data and len(data["mode"]) > 0


def test_ml_lab_classification_and_prediction():
    load_res = client.post("/api/datasets/load-sample", json={"sample_key": "patient_health"})
    dataset_id = load_res.json()["dataset"]["id"]

    # 1. Target inspection
    insp_res = client.get(f"/api/datasets/{dataset_id}/ml/inspect-target?target=Diabetic_Status")
    assert insp_res.status_code == 200
    insp_data = insp_res.json()
    assert insp_data["task_type"] == "Classification"
    assert insp_data["is_valid"] is True

    # 2. Attempt prediction before training -> must fail gracefully with clear explanation
    early_pred_res = client.post(f"/api/datasets/{dataset_id}/ml/predict", json={
        "inputs": {"Age": 50, "BMI": 30}
    })
    assert early_pred_res.status_code == 400
    assert "No trained model available" in early_pred_res.json()["detail"]

    # 3. Train models
    train_res = client.post(f"/api/datasets/{dataset_id}/ml/train", json={
        "target_col": "Diabetic_Status",
        "feature_cols": ["Age", "BMI", "Blood_Pressure", "Glucose_Level", "Smoking_Status"],
        "task_type": "Classification",
        "test_size": 0.2
    })
    assert train_res.status_code == 200
    train_data = train_res.json()
    assert train_data["success"] is True
    assert len(train_data["leaderboard"]) > 0
    assert train_data["best_model_name"] is not None

    # 4. Live inference after training
    pred_res = client.post(f"/api/datasets/{dataset_id}/ml/predict", json={
        "inputs": {
            "Age": 55,
            "BMI": 31.5,
            "Blood_Pressure": 140,
            "Glucose_Level": 130,
            "Smoking_Status": "Former"
        }
    })
    assert pred_res.status_code == 200
    pred_data = pred_res.json()
    assert pred_data["success"] is True
    assert "prediction" in pred_data
    assert "probabilities" in pred_data


def test_reports_and_exports():
    load_res = client.post("/api/datasets/load-sample", json={"sample_key": "patient_health"})
    dataset_id = load_res.json()["dataset"]["id"]

    # 1. Cleaned CSV
    csv_res = client.get(f"/api/datasets/{dataset_id}/reports/csv")
    assert csv_res.status_code == 200
    assert "text/csv" in csv_res.headers.get("content-type", "")

    # 2. Multi-Tab Excel Workbook
    excel_res = client.get(f"/api/datasets/{dataset_id}/reports/excel")
    assert excel_res.status_code == 200
    assert len(excel_res.content) > 1000

    # 3. Academic PDF Dossier
    pdf_res = client.get(f"/api/datasets/{dataset_id}/reports/pdf")
    assert pdf_res.status_code == 200
    assert len(pdf_res.content) > 1000
