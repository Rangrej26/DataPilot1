/**
 * DataPilot AI - API Client Wrapper
 * Handles typed HTTP requests, file uploads, and error extraction.
 */

const API_BASE = "";

class DataPilotAPI {
  static async request(endpoint, options = {}) {
    const url = `${API_BASE}${endpoint}`;
    const defaultHeaders = {};

    if (!(options.body instanceof FormData)) {
      defaultHeaders["Content-Type"] = "application/json";
    }

    const config = {
      ...options,
      headers: {
        ...defaultHeaders,
        ...(options.headers || {})
      }
    };

    try {
      const response = await fetch(url, config);
      const data = await response.json();

      if (!response.ok) {
        const errorMsg = data.detail || data.error || `HTTP Error ${response.status}`;
        throw new Error(errorMsg);
      }

      return data;
    } catch (err) {
      console.error(`API Error on [${options.method || 'GET'} ${endpoint}]:`, err);
      throw err;
    }
  }

  // System & Settings
  static getHealth() {
    return this.request("/api/health");
  }

  static getSettings() {
    return this.request("/api/settings");
  }

  // Datasets
  static getSampleDatasets() {
    return this.request("/api/datasets/samples");
  }

  static loadSample(sampleKey, sheetName = null) {
    return this.request("/api/datasets/load-sample", {
      method: "POST",
      body: JSON.stringify({ sample_key: sampleKey, sheet_name: sheetName })
    });
  }

  static uploadDataset(file, sheetName = null) {
    const formData = new FormData();
    formData.append("file", file);
    if (sheetName) {
      formData.append("sheet_name", sheetName);
    }
    return this.request("/api/datasets/upload", {
      method: "POST",
      body: formData
    });
  }

  static listDatasets() {
    return this.request("/api/datasets");
  }

  static getDataset(datasetId) {
    return this.request(`/api/datasets/${datasetId}`);
  }

  static deleteDataset(datasetId) {
    return this.request(`/api/datasets/${datasetId}`, { method: "DELETE" });
  }

  static getPreview(datasetId, page = 1, pageSize = 15, search = "") {
    const params = new URLSearchParams({ page, page_size: pageSize });
    if (search) params.append("search", search);
    return this.request(`/api/datasets/${datasetId}/preview?${params.toString()}`);
  }

  static getProfile(datasetId) {
    return this.request(`/api/datasets/${datasetId}/profile`);
  }

  static getOverview(datasetId) {
    return this.request(`/api/datasets/${datasetId}/overview`);
  }

  static updateContext(datasetId, context) {
    return this.request(`/api/datasets/${datasetId}/overview/context`, {
      method: "POST",
      body: JSON.stringify({ context })
    });
  }

  static getCorrelationVis(datasetId, method = "pearson") {
    return this.request(`/api/datasets/${datasetId}/visualizations/correlation?method=${method}`);
  }

  static getMissingVis(datasetId) {
    return this.request(`/api/datasets/${datasetId}/visualizations/missing`);
  }

  static getDistributionVis(datasetId, column) {
    return this.request(`/api/datasets/${datasetId}/visualizations/distribution?column=${encodeURIComponent(column)}`);
  }

  // Cleaning
  static getCleaningIssues(datasetId) {
    return this.request(`/api/datasets/${datasetId}/cleaning/issues`);
  }

  static applyCleaningFix(datasetId, payload) {
    return this.request(`/api/datasets/${datasetId}/cleaning/apply`, {
      method: "POST",
      body: JSON.stringify(payload)
    });
  }

  static autoCleanAll(datasetId) {
    return this.request(`/api/datasets/${datasetId}/cleaning/auto-clean`, {
      method: "POST"
    });
  }

  static undoCleaning(datasetId) {
    return this.request(`/api/datasets/${datasetId}/cleaning/undo`, {
      method: "POST"
    });
  }

  static resetCleaning(datasetId) {
    return this.request(`/api/datasets/${datasetId}/cleaning/reset`, {
      method: "POST"
    });
  }

  static getCleaningAudit(datasetId) {
    return this.request(`/api/datasets/${datasetId}/cleaning/audit`);
  }

  static getCleaningComparison(datasetId) {
    return this.request(`/api/datasets/${datasetId}/cleaning/comparison`);
  }

  // Chart Guide
  static getChartGoals() {
    return this.request("/api/datasets/charts/goals");
  }

  static getChartRecommendations(datasetId, goal) {
    return this.request(`/api/datasets/${datasetId}/charts/recommendations?goal=${encodeURIComponent(goal)}`);
  }

  static renderChart(datasetId, payload) {
    return this.request(`/api/datasets/${datasetId}/charts/render`, {
      method: "POST",
      body: JSON.stringify(payload)
    });
  }

  // SQL Assistant
  static executeSQL(datasetId, query, maxRows = 500) {
    return this.request(`/api/datasets/${datasetId}/sql/execute`, {
      method: "POST",
      body: JSON.stringify({ query, max_rows: maxRows })
    });
  }

  static explainSQL(datasetId, query) {
    return this.request(`/api/datasets/${datasetId}/sql/explain`, {
      method: "POST",
      body: JSON.stringify({ query })
    });
  }

  static getSQLTemplates(datasetId) {
    return this.request(`/api/datasets/${datasetId}/sql/templates`);
  }

  static generateSQL(datasetId, question) {
    return this.request(`/api/datasets/${datasetId}/sql/generate`, {
      method: "POST",
      body: JSON.stringify({ question })
    });
  }

  // AI Data Analyst
  static getSuggestedQuestions(datasetId) {
    return this.request(`/api/datasets/${datasetId}/analyst/suggested-questions`);
  }

  static askAnalyst(datasetId, question) {
    return this.request(`/api/datasets/${datasetId}/analyst/ask`, {
      method: "POST",
      body: JSON.stringify({ question })
    });
  }

  // ML Lab
  static getMLSchema(datasetId) {
    return this.request(`/api/datasets/${datasetId}/ml/schema`);
  }

  static inspectTarget(datasetId, target) {
    return this.request(`/api/datasets/${datasetId}/ml/inspect-target?target=${encodeURIComponent(target)}`);
  }

  static trainML(datasetId, payload) {
    return this.request(`/api/datasets/${datasetId}/ml/train`, {
      method: "POST",
      body: JSON.stringify(payload)
    });
  }

  static predictML(datasetId, inputs, modelName = null) {
    return this.request(`/api/datasets/${datasetId}/ml/predict`, {
      method: "POST",
      body: JSON.stringify({ inputs, model_name: modelName })
    });
  }

  // Reports
  static getCSVReportUrl(datasetId) {
    return `${API_BASE}/api/datasets/${datasetId}/reports/csv`;
  }

  static getExcelReportUrl(datasetId) {
    return `${API_BASE}/api/datasets/${datasetId}/reports/excel`;
  }

  static getPDFReportUrl(datasetId) {
    return `${API_BASE}/api/datasets/${datasetId}/reports/pdf`;
  }

  static downloadSQLResults(datasetId, query) {
    return fetch(`${API_BASE}/api/datasets/${datasetId}/reports/sql-csv`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ query })
    })
      .then(res => {
        if (!res.ok) throw new Error("Export failed");
        return res.blob();
      })
      .then(blob => {
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url;
        a.download = "sql_results.csv";
        document.body.appendChild(a);
        a.click();
        a.remove();
      });
  }
}

