/**
 * DataPilot AI - Main Application Router & UI Controller
 * Manages state, page transitions, rendering, and Plotly visualizations.
 */

// Global Application State
const state = {
  currentPage: "home",
  activeDatasetId: null,
  activeDataset: null,
  datasetsList: [],
  chartState: {
    selectedGoal: "compare_categories",
    currentChartType: "Bar Chart",
    xCol: null,
    yCol: null,
    aggFunc: "mean",
    colorCol: null
  },
  mlState: {
    targetCol: null,
    taskType: "Classification",
    selectedFeatures: [],
    testSize: 0.2,
    trainedResults: null
  }
};

// UI Notification Helper
function showToast(message, type = "info") {
  const container = document.getElementById("toast-container");
  if (!container) return;

  const toast = document.createElement("div");
  toast.className = `toast`;
  if (type === "success") toast.style.borderLeft = "4px solid #10B981";
  else if (type === "error") toast.style.borderLeft = "4px solid #EF4444";
  else if (type === "warning") toast.style.borderLeft = "4px solid #F59E0B";
  else toast.style.borderLeft = "4px solid #B9ADF5";

  toast.innerHTML = `<span>${message}</span>`;
  container.appendChild(toast);

  setTimeout(() => {
    toast.style.opacity = "0";
    toast.style.transform = "translateY(10px)";
    toast.style.transition = "all 0.2s ease";
    setTimeout(() => toast.remove(), 200);
  }, 3500);
}

// Format numbers nicely
function formatNumber(num) {
  if (num === null || num === undefined) return "—";
  return Number(num).toLocaleString();
}

// Initialize Application
document.addEventListener("DOMContentLoaded", async () => {
  setupNavigation();
  setupDatasetSelector();
  setupQuickSampleButton();

  try {
    await refreshDatasetsList();
    if (state.datasetsList.length > 0) {
      await setActiveDataset(state.datasetsList[0].id);
    } else {
      // Auto-load E-Commerce sample for immediate rich academic experience
      try {
        const sampleRes = await DataPilotAPI.loadSample("ecommerce_churn");
        if (sampleRes.dataset) {
          await refreshDatasetsList();
          await setActiveDataset(sampleRes.dataset.id);
          showToast("Loaded sample dataset: E-Commerce Customer Churn", "success");
        }
      } catch (err) {
        navigateTo("upload");
      }
    }
  } catch (err) {
    console.error("Initialization failed:", err);
    navigateTo("upload");
  }
});

// Setup Sidebar Navigation
function setupNavigation() {
  const navItems = document.querySelectorAll(".sidebar-nav .nav-item");
  navItems.forEach(item => {
    item.addEventListener("click", () => {
      const page = item.getAttribute("data-page");
      navigateTo(page);
    });
  });
}

// Router
function navigateTo(page) {
  state.currentPage = page;

  // Update sidebar active state
  document.querySelectorAll(".sidebar-nav .nav-item").forEach(el => {
    if (el.getAttribute("data-page") === page) el.classList.add("active");
    else el.classList.remove("active");
  });

  // Update header text
  updateHeader(page);

  // Render Page Content
  renderCurrentPage();
}

function updateHeader(page) {
  const titles = {
    home: { title: "Home / Overview", subtitle: "Intelligent dataset understanding and semantic profiling" },
    upload: { title: "Upload Dataset", subtitle: "Ingest CSV and Excel spreadsheets with instant validation and profiling" },
    explorer: { title: "Data Explorer", subtitle: "Interactive exploratory data analysis, descriptive statistics, and distributions" },
    cleaning: { title: "Smart Data Cleaning", subtitle: "Transparent automated flaw detection, 3-part explanations, and auditable transformations" },
    charts: { title: "Chart Guide", subtitle: "Beginner-friendly guided chart recommendations grounded in your actual data" },
    sql: { title: "SQL Assistant", subtitle: "High-performance in-memory DuckDB analytical queries with read-only security sandbox" },
    analyst: { title: "AI Data Analyst", subtitle: "Grounded natural language insights with deterministic calculations" },
    ml: { title: "Machine Learning Lab", subtitle: "Scikit-learn predictive modeling studio: leakage safeguards, benchmarking, and what-if live predictions" },
    reports: { title: "Reports & Exports", subtitle: "Download cleaned CSVs, multi-sheet Excel workbooks, and ReportLab academic PDF dossiers" },
    settings: { title: "Settings & Theme", subtitle: "System environment, configuration, and design system color specifications" }
  };

  const info = titles[page] || titles.home;
  document.getElementById("page-header-title").textContent = info.title;
  document.getElementById("page-header-subtitle").textContent = info.subtitle;
}

// Refresh Datasets
async function refreshDatasetsList() {
  try {
    const res = await DataPilotAPI.listDatasets();
    state.datasetsList = res.datasets || [];
    updateDatasetSelectorUI();
  } catch (err) {
    console.error("Failed to list datasets:", err);
  }
}

function updateDatasetSelectorUI() {
  const selector = document.getElementById("dataset-selector");
  if (!selector) return;

  selector.innerHTML = "";
  if (state.datasetsList.length === 0) {
    selector.innerHTML = '<option value="">No dataset loaded</option>';
    return;
  }

  state.datasetsList.forEach(ds => {
    const opt = document.createElement("option");
    opt.value = ds.id;
    opt.textContent = `${ds.name} (${formatNumber(ds.total_rows)} rows)`;
    if (ds.id === state.activeDatasetId) opt.selected = true;
    selector.appendChild(opt);
  });
}

function setupDatasetSelector() {
  const selector = document.getElementById("dataset-selector");
  if (!selector) return;
  selector.addEventListener("change", async (e) => {
    const dId = e.target.value;
    if (dId) {
      await setActiveDataset(dId);
    }
  });
}

function setupQuickSampleButton() {
  const btn = document.getElementById("btn-quick-sample");
  if (!btn) return;
  btn.addEventListener("click", () => {
    navigateTo("upload");
    const sampleSection = document.getElementById("samples-section");
    if (sampleSection) {
      sampleSection.scrollIntoView({ behavior: "smooth" });
    }
  });
}

async function setActiveDataset(datasetId) {
  try {
    const ds = await DataPilotAPI.getDataset(datasetId);
    state.activeDatasetId = datasetId;
    state.activeDataset = ds;

    // Reset ML trained results on dataset switch
    state.mlState.trainedResults = null;
    state.mlState.targetCol = null;

    // Update Sidebar Widget
    document.getElementById("sidebar-dataset-name").textContent = ds.name;
    document.getElementById("sidebar-dataset-stats").textContent = `${formatNumber(ds.total_rows)} rows • ${formatNumber(ds.total_cols)} cols`;
    const badge = document.getElementById("sidebar-health-badge");
    badge.textContent = `${ds.health_score}%`;
    if (ds.health_score >= 80) badge.className = "badge badge-lime";
    else if (ds.health_score >= 50) badge.className = "badge badge-warning";
    else badge.className = "badge badge-danger";

    updateDatasetSelectorUI();
    renderCurrentPage();
  } catch (err) {
    showToast(`Failed to switch dataset: ${err.message}`, "error");
  }
}

// Render Router
function renderCurrentPage() {
  const container = document.getElementById("main-content");
  if (!container) return;

  // Upload and Settings can render even without active dataset
  if (!state.activeDatasetId && state.currentPage !== "upload" && state.currentPage !== "settings") {
    container.innerHTML = `
      <div class="empty-state">
        <div class="empty-state-icon">📁</div>
        <h2 class="empty-state-title">No Active Dataset Loaded</h2>
        <p class="empty-state-text">Upload your own CSV or Excel spreadsheet, or load one of our realistic academic sample datasets to get started.</p>
        <button class="btn btn-primary btn-lg" onclick="navigateTo('upload')">Go to Upload Dataset</button>
      </div>
    `;
    return;
  }

  switch (state.currentPage) {
    case "home":
      renderHomePage(container);
      break;
    case "upload":
      renderUploadPage(container);
      break;
    case "explorer":
      renderExplorerPage(container);
      break;
    case "cleaning":
      renderCleaningPage(container);
      break;
    case "charts":
      renderChartsPage(container);
      break;
    case "sql":
      renderSQLPage(container);
      break;
    case "analyst":
      renderAnalystPage(container);
      break;
    case "ml":
      renderMLPage(container);
      break;
    case "reports":
      renderReportsPage(container);
      break;
    case "settings":
      renderSettingsPage(container);
      break;
    default:
      renderHomePage(container);
  }
}

/* ==========================================================================
   PAGE 1: HOME / OVERVIEW
   ========================================================================== */
async function renderHomePage(container) {
  container.innerHTML = `
    <div class="card" style="text-align: center; padding: 40px;">
      <div class="spinner"></div>
      <p style="margin-top: 10px; color: var(--text-secondary);">Analyzing schema and inferring dataset semantics...</p>
    </div>
  `;

  try {
    const overview = await DataPilotAPI.getOverview(state.activeDatasetId);
    const ds = state.activeDataset;

    container.innerHTML = `
      <!-- High-Level KPIs -->
      <div class="kpi-grid">
        <div class="kpi-card">
          <span class="kpi-label">Total Observations</span>
          <span class="kpi-value">${formatNumber(overview.total_rows)}</span>
          <span class="kpi-hint">Cleaned / Working Rows</span>
        </div>
        <div class="kpi-card">
          <span class="kpi-label">Total Features</span>
          <span class="kpi-value">${formatNumber(overview.total_cols)}</span>
          <span class="kpi-hint">${overview.numeric_count} numeric, ${overview.categorical_count} categorical</span>
        </div>
        <div class="kpi-card">
          <span class="kpi-label">Inferred Domain</span>
          <span class="kpi-value" style="font-size: 21px;">${overview.domain}</span>
          <span class="kpi-hint">${overview.inferred_subject}</span>
        </div>
        <div class="kpi-card">
          <span class="kpi-label">Dataset Health</span>
          <span class="kpi-value" style="color: ${ds.health_score >= 80 ? 'var(--text-primary)' : 'var(--warning)'};">${ds.health_score}%</span>
          <span class="kpi-hint">${ds.memory_str} memory footprint</span>
        </div>
      </div>

      <!-- Plain English Dataset Understanding -->
      <div class="card">
        <div class="card-header">
          <div>
            <h2 class="card-title">📖 Intelligent Dataset Understanding</h2>
            <p class="card-subtitle">Auto-generated plain-English synthesis derived from column distributions and schema heuristics</p>
          </div>
          <span class="badge badge-lavender">Deterministic Ground Truth</span>
        </div>
        <p style="font-size: 16px; line-height: 1.6; color: var(--text-primary); margin-bottom: 16px;">
          ${overview.dataset_description}
        </p>

        <!-- Context Injection Box -->
        <div style="background: #F8F9FA; border: 1px solid var(--border-color); border-radius: var(--radius-md); padding: 14px 18px; margin-top: 14px;">
          <label class="form-label" style="font-size: 13.5px; margin-bottom: 4px;">Optional User Context or Notes:</label>
          <div style="display: flex; gap: 10px;">
            <input type="text" id="user-context-input" class="form-input" placeholder="e.g., Data for marketing campaign analysis in Q3" value="${overview.user_context || ''}" />
            <button class="btn btn-secondary btn-sm" id="btn-save-context">Save Context</button>
          </div>
          <p class="form-hint">Providing context enriches explanations without modifying the underlying data rows.</p>
        </div>
      </div>

      <!-- Tailored Analysis Suggestions Grid -->
      <h3 class="section-heading">💡 Recommended Analytical Pathways</h3>
      <div class="rec-grid" id="suggestions-grid">
        ${overview.analysis_suggestions.map(sug => `
          <div class="rec-card">
            <div>
              <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                <span style="font-size: 20px;">${sug.icon || '📊'}</span>
                <span class="badge badge-lime">${sug.type || 'Analysis'}</span>
              </div>
              <h4 style="font-size: 16px; font-weight: 600; color: var(--text-primary); margin-bottom: 6px;">${sug.title}</h4>
              <p style="font-size: 13.5px; color: var(--text-secondary); line-height: 1.4;">${sug.description}</p>
            </div>
            <button class="btn btn-secondary btn-sm" onclick="navigateTo('${sug.suggested_page || 'explorer'}')">
              Explore in ${sug.suggested_page_label || 'Workspace'} &rarr;
            </button>
          </div>
        `).join('')}
      </div>

      <!-- Semantic Column Dictionary -->
      <div class="card">
        <div class="card-header">
          <div>
            <h2 class="card-title">📚 Semantic Column Dictionary</h2>
            <p class="card-subtitle">Programmatic data types vs inferred real-world column meanings with safe sample values</p>
          </div>
          <span class="badge badge-gray">${overview.column_dictionary.length} Columns Documented</span>
        </div>

        <div class="table-responsive">
          <table class="data-table">
            <thead>
              <tr>
                <th>Column Name</th>
                <th>Programmatic Type</th>
                <th>Inferred Real-World Meaning</th>
                <th>Safe Sample Value</th>
                <th>Missing Values</th>
              </tr>
            </thead>
            <tbody>
              ${overview.column_dictionary.map(col => `
                <tr>
                  <td style="font-weight: 600; color: var(--text-primary);">${col.column_name}</td>
                  <td><code style="background: #F1F3F5; padding: 2px 6px; border-radius: 4px; font-size: 12.5px;">${col.programmatic_type}</code></td>
                  <td>${col.inferred_semantic_meaning}</td>
                  <td style="color: var(--text-secondary);">${col.example_value}</td>
                  <td>
                    ${col.missing_count > 0 
                      ? `<span class="badge badge-danger">${formatNumber(col.missing_count)} nulls</span>` 
                      : `<span class="badge badge-success">0 nulls</span>`}
                  </td>
                </tr>
              `).join('')}
            </tbody>
          </table>
        </div>
      </div>
    `;

    // Bind Context Save Button
    document.getElementById("btn-save-context")?.addEventListener("click", async () => {
      const val = document.getElementById("user-context-input").value;
      try {
        await DataPilotAPI.updateContext(state.activeDatasetId, val);
        showToast("Context saved and dataset understanding updated!", "success");
        renderHomePage(container);
      } catch (err) {
        showToast(`Failed to update context: ${err.message}`, "error");
      }
    });

  } catch (err) {
    container.innerHTML = `
      <div class="alert alert-danger">
        <strong>Error loading dataset overview:</strong> ${err.message}
      </div>
    `;
  }
}

/* ==========================================================================
   PAGE 2: UPLOAD DATASET
   ========================================================================== */
async function renderUploadPage(container) {
  container.innerHTML = `
    <!-- Upload Dropzone Card -->
    <div class="card">
      <div class="card-header">
        <div>
          <h2 class="card-title">Upload New Dataset</h2>
          <p class="card-subtitle">Upload a local CSV or multi-sheet Excel (.xlsx, .xls) spreadsheet (up to 50MB)</p>
        </div>
        <span class="badge badge-gray">CSV &amp; Excel Supported</span>
      </div>

      <div class="upload-dropzone" id="dropzone">
        <div class="upload-icon">📤</div>
        <h3 style="font-size: 17px; font-weight: 600; margin-bottom: 6px;">Drag and drop your spreadsheet here</h3>
        <p style="font-size: 14px; color: var(--text-secondary); margin-bottom: 16px;">Or click the button below to browse files from your computer</p>
        <input type="file" id="file-input" accept=".csv,.xlsx,.xls" style="display: none;" />
        <button class="btn btn-primary" id="btn-browse-file">Browse Local Files</button>
      </div>

      <div id="upload-status" style="margin-top: 14px;"></div>
    </div>

    <!-- Pre-Packaged Academic Datasets -->
    <div class="card" id="samples-section">
      <div class="card-header">
        <div>
          <h2 class="card-title">🎓 Or Load a Pre-Packaged Academic Dataset</h2>
          <p class="card-subtitle">Realistic research datasets curated with real-world flaws, multi-class targets, and benchmarks</p>
        </div>
        <span class="badge badge-lime">1-Click Quick Load</span>
      </div>

      <div class="samples-grid" id="samples-container">
        <div style="padding: 20px; text-align: center; grid-column: 1 / -1;">
          <div class="spinner"></div>
          <p style="color: var(--text-secondary); margin-top: 8px;">Loading academic samples...</p>
        </div>
      </div>
    </div>

    <!-- Active Dataset Preview (if loaded) -->
    <div id="upload-preview-container"></div>
  `;

  // Fetch Samples
  try {
    const samplesRes = await DataPilotAPI.getSampleDatasets();
    const samplesContainer = document.getElementById("samples-container");
    if (samplesContainer && samplesRes.samples) {
      samplesContainer.innerHTML = samplesRes.samples.map(s => `
        <div class="sample-card">
          <div>
            <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 8px;">
              <span class="badge badge-lavender">${s.badge}</span>
              <span style="font-size: 11.5px; color: var(--text-muted); text-transform: uppercase; font-weight: 600;">${s.type}</span>
            </div>
            <h4 style="font-size: 15.5px; font-weight: 700; color: var(--text-primary); margin-bottom: 6px;">${s.name}</h4>
            <p style="font-size: 13px; color: var(--text-secondary); line-height: 1.4; margin-bottom: 14px;">${s.description}</p>
          </div>
          <button class="btn btn-secondary btn-sm" onclick="handleLoadSample('${s.key}')">Load Sample &rarr;</button>
        </div>
      `).join('');
    }
  } catch (err) {
    console.error("Failed to fetch samples:", err);
  }

  // Setup Dropzone Drag & Drop
  const dropzone = document.getElementById("dropzone");
  const fileInput = document.getElementById("file-input");
  const btnBrowse = document.getElementById("btn-browse-file");

  btnBrowse?.addEventListener("click", () => fileInput.click());

  dropzone?.addEventListener("dragover", (e) => {
    e.preventDefault();
    dropzone.classList.add("dragover");
  });

  dropzone?.addEventListener("dragleave", () => dropzone.classList.remove("dragover"));

  dropzone?.addEventListener("drop", (e) => {
    e.preventDefault();
    dropzone.classList.remove("dragover");
    if (e.dataTransfer.files.length > 0) {
      handleFileUpload(e.dataTransfer.files[0]);
    }
  });

  fileInput?.addEventListener("change", (e) => {
    if (e.target.files.length > 0) {
      handleFileUpload(e.target.files[0]);
    }
  });

  // Render preview if dataset active
  if (state.activeDatasetId) {
    renderUploadPreview(document.getElementById("upload-preview-container"));
  }
}

async function handleFileUpload(file) {
  const statusDiv = document.getElementById("upload-status");
  if (statusDiv) {
    statusDiv.innerHTML = `
      <div class="alert alert-info">
        <div class="spinner"></div>
        <span>Uploading and profiling <strong>${file.name}</strong>...</span>
      </div>
    `;
  }

  try {
    const res = await DataPilotAPI.uploadDataset(file);
    if (res.success && res.dataset) {
      showToast(`Uploaded ${file.name} successfully!`, "success");
      await refreshDatasetsList();
      await setActiveDataset(res.dataset.id);
      navigateTo("home");
    }
  } catch (err) {
    if (statusDiv) {
      statusDiv.innerHTML = `
        <div class="alert alert-danger">
          <strong>Upload Error:</strong> ${err.message}
        </div>
      `;
    }
  }
}

window.handleLoadSample = async function(sampleKey) {
  const statusDiv = document.getElementById("upload-status");
  if (statusDiv) {
    statusDiv.innerHTML = `
      <div class="alert alert-info">
        <div class="spinner"></div>
        <span>Loading sample dataset...</span>
      </div>
    `;
  }

  try {
    const res = await DataPilotAPI.loadSample(sampleKey);
    if (res.success && res.dataset) {
      showToast(res.message, "success");
      await refreshDatasetsList();
      await setActiveDataset(res.dataset.id);
      navigateTo("home");
    }
  } catch (err) {
    showToast(`Error loading sample: ${err.message}`, "error");
  }
};

async function renderUploadPreview(container) {
  if (!container || !state.activeDatasetId) return;

  try {
    const preview = await DataPilotAPI.getPreview(state.activeDatasetId, 1, 10);
    container.innerHTML = `
      <div class="card" style="margin-top: 24px;">
        <div class="card-header">
          <div>
            <h3 class="card-title">Currently Active Dataset: ${state.activeDataset.name}</h3>
            <p class="card-subtitle">Showing initial 10 records of ${formatNumber(preview.total_rows)} total rows</p>
          </div>
          <button class="btn btn-secondary btn-sm" onclick="navigateTo('explorer')">Open in Data Explorer &rarr;</button>
        </div>

        <div class="table-responsive">
          <table class="data-table">
            <thead>
              <tr>
                ${preview.columns.map(c => `<th>${c}</th>`).join('')}
              </tr>
            </thead>
            <tbody>
              ${preview.rows.map(row => `
                <tr>
                  ${preview.columns.map(c => `<td>${row[c] !== null && row[c] !== undefined ? row[c] : '<i style="color:var(--text-muted)">null</i>'}</td>`).join('')}
                </tr>
              `).join('')}
            </tbody>
          </table>
        </div>
      </div>
    `;
  } catch (err) {
    console.error("Preview render failed:", err);
  }
}

/* ==========================================================================
   PAGE 3: DATA EXPLORER
   ========================================================================== */
let explorerPageNumber = 1;
let explorerSearchQuery = "";

async function renderExplorerPage(container) {
  container.innerHTML = `
    <!-- Top Filter & Search Bar -->
    <div class="card" style="padding: 16px 20px;">
      <div style="display: flex; justify-content: space-between; align-items: center; gap: 14px; flex-wrap: wrap;">
        <div style="display: flex; align-items: center; gap: 10px; flex: 1; min-width: 280px;">
          <input type="text" id="explorer-search" class="form-input" placeholder="Search values across rows..." value="${explorerSearchQuery}" />
          <button class="btn btn-secondary btn-sm" id="btn-explorer-search">Search</button>
          ${explorerSearchQuery ? `<button class="btn btn-sm" id="btn-clear-search" style="color: var(--text-secondary);">Clear</button>` : ''}
        </div>
        <div style="display: flex; gap: 10px;">
          <button class="btn btn-secondary btn-sm" id="btn-view-profile">View Full Profiling Tables</button>
        </div>
      </div>
    </div>

    <!-- Paginated Table Container -->
    <div class="card">
      <div class="card-header">
        <h3 class="card-title">Dataset Records</h3>
        <span class="badge badge-gray" id="explorer-row-count-badge">Loading...</span>
      </div>
      <div id="explorer-table-content">
        <div style="text-align: center; padding: 32px;"><div class="spinner"></div></div>
      </div>
    </div>

    <!-- Exploratory Visualizations Section -->
    <h3 class="section-heading">📈 Exploratory Data Visualizations</h3>
    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(480px, 1fr)); gap: 20px;">
      
      <!-- Correlation Heatmap Card -->
      <div class="card">
        <div class="card-header">
          <div>
            <h4 class="card-title">Feature Correlation Matrix</h4>
            <p class="card-subtitle">Pairwise correlation between numerical variables</p>
          </div>
          <div style="display: flex; gap: 6px;">
            <button class="btn btn-secondary btn-sm" id="btn-corr-pearson" style="font-weight: 600;">Pearson</button>
            <button class="btn btn-secondary btn-sm" id="btn-corr-spearman">Spearman</button>
          </div>
        </div>
        <div id="plot-correlation" style="min-height: 400px; display: flex; align-items: center; justify-content: center;">
          <div class="spinner"></div>
        </div>
      </div>

      <!-- Missing Values Card -->
      <div class="card">
        <div class="card-header">
          <div>
            <h4 class="card-title">Missing Values Inspection</h4>
            <p class="card-subtitle">Null counts and percentages across all features</p>
          </div>
        </div>
        <div id="plot-missing" style="min-height: 400px; display: flex; align-items: center; justify-content: center;">
          <div class="spinner"></div>
        </div>
      </div>
    </div>

    <!-- Single Feature Distribution Card -->
    <div class="card" style="margin-top: 20px;">
      <div class="card-header">
        <div>
          <h4 class="card-title">Feature Distribution Deep-Dive</h4>
          <p class="card-subtitle">Histogram + Box plot for numericals; category frequency bar for categoricals</p>
        </div>
        <div style="display: flex; align-items: center; gap: 10px;">
          <label style="font-size: 13.5px; font-weight: 600;">Select Column:</label>
          <select class="form-select" id="select-dist-col" style="width: 220px; padding: 6px 10px; font-size: 13.5px;"></select>
        </div>
      </div>
      <div id="plot-distribution" style="min-height: 400px; display: flex; align-items: center; justify-content: center;">
        <div class="spinner"></div>
      </div>
    </div>

    <!-- Profiling Modal Container (Hidden by default) -->
    <div id="profiling-tables-container" style="display: none; margin-top: 24px;"></div>
  `;

  // Bind Search
  document.getElementById("btn-explorer-search")?.addEventListener("click", () => {
    explorerSearchQuery = document.getElementById("explorer-search").value;
    explorerPageNumber = 1;
    loadExplorerPageData();
  });

  document.getElementById("btn-clear-search")?.addEventListener("click", () => {
    explorerSearchQuery = "";
    document.getElementById("explorer-search").value = "";
    explorerPageNumber = 1;
    loadExplorerPageData();
  });

  document.getElementById("btn-view-profile")?.addEventListener("click", toggleProfilingTables);

  // Load Table Data
  loadExplorerPageData();

  // Load Visualizations
  loadCorrelationPlot("pearson");
  loadMissingPlot();
  setupDistributionFeature();
}

async function loadExplorerPageData() {
  const tableContent = document.getElementById("explorer-table-content");
  if (!tableContent) return;

  try {
    const preview = await DataPilotAPI.getPreview(state.activeDatasetId, explorerPageNumber, 15, explorerSearchQuery);
    
    document.getElementById("explorer-row-count-badge").textContent = `${formatNumber(preview.total_rows)} rows matching`;

    tableContent.innerHTML = `
      <div class="table-responsive">
        <table class="data-table">
          <thead>
            <tr>
              ${preview.columns.map(c => `<th>${c} <span style="font-weight: 400; font-size: 11px; color: var(--text-muted);">(${preview.dtypes[c] || 'obj'})</span></th>`).join('')}
            </tr>
          </thead>
          <tbody>
            ${preview.rows.map(row => `
              <tr>
                ${preview.columns.map(c => `<td>${row[c] !== null && row[c] !== undefined ? row[c] : '<i style="color:var(--text-muted)">null</i>'}</td>`).join('')}
              </tr>
            `).join('')}
          </tbody>
        </table>
      </div>

      <div class="pagination-bar">
        <span>Page ${preview.page} of ${preview.total_pages} (${formatNumber(preview.total_rows)} rows)</span>
        <div class="pagination-controls">
          <button class="btn btn-secondary btn-sm" id="btn-prev-page" ${preview.page <= 1 ? 'disabled' : ''}>&larr; Previous</button>
          <button class="btn btn-secondary btn-sm" id="btn-next-page" ${preview.page >= preview.total_pages ? 'disabled' : ''}>Next &rarr;</button>
        </div>
      </div>
    `;

    document.getElementById("btn-prev-page")?.addEventListener("click", () => {
      if (explorerPageNumber > 1) {
        explorerPageNumber--;
        loadExplorerPageData();
      }
    });

    document.getElementById("btn-next-page")?.addEventListener("click", () => {
      if (explorerPageNumber < preview.total_pages) {
        explorerPageNumber++;
        loadExplorerPageData();
      }
    });

  } catch (err) {
    tableContent.innerHTML = `<div class="alert alert-danger">${err.message}</div>`;
  }
}

async function loadCorrelationPlot(method = "pearson") {
  const container = document.getElementById("plot-correlation");
  if (!container) return;

  try {
    const res = await DataPilotAPI.getCorrelationVis(state.activeDatasetId, method);
    if (res.has_figure && res.figure) {
      Plotly.newPlot(container, res.figure.data, res.figure.layout, { responsive: true, displayModeBar: false });
    } else {
      container.innerHTML = `<p style="color: var(--text-secondary);">${res.message || 'At least 2 numerical features required.'}</p>`;
    }
  } catch (err) {
    container.innerHTML = `<p style="color: var(--danger);">Failed to load correlation chart.</p>`;
  }
}

async function loadMissingPlot() {
  const container = document.getElementById("plot-missing");
  if (!container) return;

  try {
    const res = await DataPilotAPI.getMissingVis(state.activeDatasetId);
    if (res.has_figure && res.figure) {
      Plotly.newPlot(container, res.figure.data, res.figure.layout, { responsive: true, displayModeBar: false });
    } else {
      container.innerHTML = `<div style="text-align: center; color: var(--success); font-weight: 600;">✓ Excellent Data Completeness: Zero missing values detected.</div>`;
    }
  } catch (err) {
    container.innerHTML = `<p style="color: var(--danger);">Failed to load missing values chart.</p>`;
  }
}

async function setupDistributionFeature() {
  const select = document.getElementById("select-dist-col");
  if (!select) return;

  try {
    const preview = await DataPilotAPI.getPreview(state.activeDatasetId, 1, 1);
    select.innerHTML = preview.columns.map(c => `<option value="${c}">${c}</option>`).join('');

    const loadDist = async (col) => {
      const container = document.getElementById("plot-distribution");
      container.innerHTML = `<div class="spinner"></div>`;
      try {
        const res = await DataPilotAPI.getDistributionVis(state.activeDatasetId, col);
        if (res.has_figure && res.figure) {
          Plotly.newPlot(container, res.figure.data, res.figure.layout, { responsive: true, displayModeBar: false });
        } else {
          container.innerHTML = `<p style="color: var(--text-secondary);">${res.message || 'Unable to plot distribution.'}</p>`;
        }
      } catch (err) {
        container.innerHTML = `<p style="color: var(--danger);">Distribution plot error.</p>`;
      }
    };

    if (preview.columns.length > 0) {
      loadDist(preview.columns[0]);
    }

    select.addEventListener("change", (e) => loadDist(e.target.value));

  } catch (err) {
    console.error("Distribution setup failed:", err);
  }
}

async function toggleProfilingTables() {
  const container = document.getElementById("profiling-tables-container");
  if (!container) return;

  if (container.style.display === "block") {
    container.style.display = "none";
    document.getElementById("btn-view-profile").textContent = "View Full Profiling Tables";
    return;
  }

  container.style.display = "block";
  document.getElementById("btn-view-profile").textContent = "Hide Profiling Tables";
  container.innerHTML = `<div class="card" style="text-align: center; padding: 32px;"><div class="spinner"></div></div>`;

  try {
    const profile = await DataPilotAPI.getProfile(state.activeDatasetId);
    container.innerHTML = `
      <!-- Numerical Summary -->
      <div class="card">
        <div class="card-header">
          <h4 class="card-title">Descriptive Numerical Statistics</h4>
          <span class="badge badge-gray">${profile.numerical_summary.length} Numerical Columns</span>
        </div>
        <div class="table-responsive">
          <table class="data-table">
            <thead>
              <tr>
                <th>Column</th><th>Count</th><th>Missing</th><th>Mean</th><th>Std Dev</th><th>Min</th><th>Median</th><th>Max</th><th>Skewness</th><th>Outliers</th>
              </tr>
            </thead>
            <tbody>
              ${profile.numerical_summary.map(r => `
                <tr>
                  <td style="font-weight: 600;">${r.Column}</td>
                  <td>${formatNumber(r.Count)}</td>
                  <td>${r.Missing > 0 ? `<span class="badge badge-warning">${r.Missing}</span>` : '0'}</td>
                  <td>${r.Mean}</td><td>${r['Std Dev']}</td><td>${r.Min}</td>
                  <td style="font-weight: 600;">${r.Median}</td><td>${r.Max}</td>
                  <td>${r.Skewness}</td>
                  <td>${r['Outliers (IQR)'] > 0 ? `<span class="badge badge-danger">${r['Outliers (IQR)']}</span>` : '0'}</td>
                </tr>
              `).join('')}
            </tbody>
          </table>
        </div>
      </div>

      <!-- Categorical Summary -->
      <div class="card" style="margin-top: 20px;">
        <div class="card-header">
          <h4 class="card-title">Categorical Cardinality &amp; Frequencies</h4>
          <span class="badge badge-gray">${profile.categorical_summary.length} Categorical Columns</span>
        </div>
        <div class="table-responsive">
          <table class="data-table">
            <thead>
              <tr>
                <th>Column</th><th>Distinct Values</th><th>Top Category</th><th>Frequency</th><th>Top Share %</th><th>Cardinality</th>
              </tr>
            </thead>
            <tbody>
              ${profile.categorical_summary.map(r => `
                <tr>
                  <td style="font-weight: 600;">${r.Column}</td>
                  <td>${formatNumber(r['Unique Values'])}</td>
                  <td style="font-weight: 500;">${r['Top Category']}</td>
                  <td>${formatNumber(r['Top Frequency'])}</td>
                  <td>${r['Top Category %']}</td>
                  <td><span class="badge ${r.Cardinality === 'High' ? 'badge-danger' : 'badge-lavender'}">${r.Cardinality}</span></td>
                </tr>
              `).join('')}
            </tbody>
          </table>
        </div>
      </div>
    `;
    container.scrollIntoView({ behavior: "smooth" });
  } catch (err) {
    container.innerHTML = `<div class="alert alert-danger">${err.message}</div>`;
  }
}

/* ==========================================================================
   PAGE 4: SMART DATA CLEANING
   ========================================================================== */
async function renderCleaningPage(container) {
  container.innerHTML = `
    <div class="card" style="text-align: center; padding: 40px;">
      <div class="spinner"></div>
      <p style="margin-top: 10px; color: var(--text-secondary);">Scanning dataset for duplicates, nulls, outliers, and formatting flaws...</p>
    </div>
  `;

  try {
    const issuesData = await DataPilotAPI.getCleaningIssues(state.activeDatasetId);
    const auditData = await DataPilotAPI.getCleaningAudit(state.activeDatasetId);
    const ds = state.activeDataset;

    container.innerHTML = `
      <!-- Cleaning Header & Actions -->
      <div class="card" style="padding: 20px 24px;">
        <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 14px;">
          <div>
            <h2 class="card-title" style="font-size: 19px;">Automated Data Quality Audit</h2>
            <p class="card-subtitle">
              Detected ${issuesData.total_issues} issues • Current Dataset Health: <strong>${issuesData.health_score}%</strong>
            </p>
          </div>
          <div style="display: flex; align-items: center; gap: 10px;">
            <button class="btn btn-secondary btn-sm" id="btn-cleaning-undo" ${issuesData.can_undo ? '' : 'disabled'}>
              ↩ Undo Last Step
            </button>
            <button class="btn btn-secondary btn-sm" id="btn-cleaning-reset">
              🔄 Reset to Raw Data
            </button>
            <button class="btn btn-primary" id="btn-auto-clean-all" ${issuesData.total_issues === 0 ? 'disabled' : ''}>
              ⚡ Auto-Clean All Confirmed Issues
            </button>
          </div>
        </div>
      </div>

      <!-- Detected Issues List -->
      <h3 class="section-heading">
        <span>🔍 Detected Issues (${issuesData.issues.length})</span>
      </h3>

      ${issuesData.issues.length === 0 ? `
        <div class="alert alert-success" style="font-size: 15px;">
          <strong>✓ Your data looks good!</strong> No pending cleaning issues were detected in the active dataset.
        </div>
      ` : `
        <div id="issues-list">
          ${issuesData.issues.map(iss => `
            <div class="issue-card ${iss.requires_confirmation ? 'review-needed' : 'confirmed'}">
              <div style="display: flex; justify-content: space-between; align-items: flex-start;">
                <div>
                  <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 4px;">
                    <span class="badge ${iss.requires_confirmation ? 'badge-warning' : 'badge-lavender'}">${iss.type}</span>
                    <h4 style="font-size: 16px; font-weight: 700; color: var(--text-primary);">${iss.name}</h4>
                  </div>
                  <span style="font-size: 13px; color: var(--text-secondary);">${iss.problem}</span>
                </div>
                <button class="btn btn-primary btn-sm" onclick="handleApplyFix('${iss.id}', '${iss.name}', '${iss.column || ''}')">
                  Apply Fix
                </button>
              </div>

              <!-- 3-Part Explanation: Found, Action, Why -->
              <div class="issue-three-part">
                <div>
                  <div class="issue-part-label">What Was Found</div>
                  <div>${iss.problem} (${formatNumber(iss.count)} records)</div>
                </div>
                <div>
                  <div class="issue-part-label">Recommended Action</div>
                  <div>${iss.recommended_action}</div>
                </div>
                <div>
                  <div class="issue-part-label">Why This Matters</div>
                  <div>${iss.reason}</div>
                </div>
              </div>
            </div>
          `).join('')}
        </div>
      `}

      <!-- Cleaning Audit Trail Log -->
      <div class="card" style="margin-top: 28px;">
        <div class="card-header">
          <div>
            <h3 class="card-title">📜 Cleaning Audit Trail</h3>
            <p class="card-subtitle">Transparent historical ledger of applied transformations for academic reproducibility</p>
          </div>
          <span class="badge badge-gray">${auditData.audit_trail.length} Operations Logged</span>
        </div>

        ${auditData.audit_trail.length === 0 ? `
          <p style="color: var(--text-secondary); text-align: center; padding: 20px;">
            No transformations applied yet. Dataset is in original uploaded state.
          </p>
        ` : `
          <div class="table-responsive">
            <table class="data-table">
              <thead>
                <tr>
                  <th>Step</th><th>Timestamp</th><th>Issue</th><th>Target</th><th>Action</th><th>Records Affected</th>
                </tr>
              </thead>
              <tbody>
                ${auditData.audit_trail.map(a => `
                  <tr>
                    <td style="font-weight: 700;">#${a.Step}</td>
                    <td style="color: var(--text-secondary); font-size: 13px;">${a.Timestamp}</td>
                    <td><strong>${a.Issue}</strong></td>
                    <td><code>${a.Target}</code></td>
                    <td>${a.Action} (${a.Method})</td>
                    <td><span class="badge badge-lime">${formatNumber(a['Affected Count'])} rows</span></td>
                  </tr>
                `).join('')}
              </tbody>
            </table>
          </div>
        `}
      </div>
    `;

    // Bind Auto Clean All
    document.getElementById("btn-auto-clean-all")?.addEventListener("click", async () => {
      try {
        const res = await DataPilotAPI.autoCleanAll(state.activeDatasetId);
        showToast(`Auto-cleaned ${res.applied_count} issues successfully!`, "success");
        await setActiveDataset(state.activeDatasetId);
        renderCleaningPage(container);
      } catch (err) {
        showToast(`Auto-clean failed: ${err.message}`, "error");
      }
    });

    // Bind Undo
    document.getElementById("btn-cleaning-undo")?.addEventListener("click", async () => {
      try {
        const res = await DataPilotAPI.undoCleaning(state.activeDatasetId);
        showToast("Last cleaning transformation reverted.", "info");
        await setActiveDataset(state.activeDatasetId);
        renderCleaningPage(container);
      } catch (err) {
        showToast(`Undo failed: ${err.message}`, "error");
      }
    });

    // Bind Reset
    document.getElementById("btn-cleaning-reset")?.addEventListener("click", async () => {
      if (confirm("Are you sure you want to revert all cleaning changes and return to the raw uploaded dataset?")) {
        try {
          await DataPilotAPI.resetCleaning(state.activeDatasetId);
          showToast("Dataset reset to original raw state.", "info");
          await setActiveDataset(state.activeDatasetId);
          renderCleaningPage(container);
        } catch (err) {
          showToast(`Reset failed: ${err.message}`, "error");
        }
      }
    });

  } catch (err) {
    container.innerHTML = `<div class="alert alert-danger">${err.message}</div>`;
  }
}

window.handleApplyFix = async function(issueId, issueName, colName) {
  let action = "impute_missing";
  if (issueId === "duplicates") action = "remove_duplicates";
  else if (issueId.startsWith("text_")) action = "standardize_text";
  else if (issueId.startsWith("date_")) action = "parse_dates";
  else if (issueId.startsWith("outliers_")) action = "handle_outliers";

  try {
    const res = await DataPilotAPI.applyCleaningFix(state.activeDatasetId, {
      issue_id: issueId,
      issue_type: issueName,
      target_column: colName || null,
      action: action
    });

    showToast(res.message, "success");
    await setActiveDataset(state.activeDatasetId);
    renderCurrentPage();
  } catch (err) {
    showToast(`Fix application failed: ${err.message}`, "error");
  }
};

/* ==========================================================================
   PAGE 5: CHART GUIDE (BEGINNER-FRIENDLY)
   ========================================================================== */
async function renderChartsPage(container) {
  container.innerHTML = `
    <div class="card" style="text-align: center; padding: 40px;">
      <div class="spinner"></div>
      <p style="margin-top: 10px; color: var(--text-secondary);">Inspecting schema and preparing chart recommendations...</p>
    </div>
  `;

  try {
    const goalsRes = await DataPilotAPI.getChartGoals();
    const goals = goalsRes.goals || [];

    container.innerHTML = `
      <!-- Step 1: Analytical Goal Selection -->
      <div class="card">
        <div class="card-header">
          <div>
            <h2 class="card-title">Step 1: What do you want to understand from your data?</h2>
            <p class="card-subtitle">Select your core analytical goal to receive dataset-aware visual recommendations</p>
          </div>
          <span class="badge badge-lime">Guided Assistant</span>
        </div>

        <div class="goals-grid" id="goals-container">
          ${goals.map(g => `
            <div class="goal-card ${g.key === state.chartState.selectedGoal ? 'active' : ''}" onclick="selectChartGoal('${g.key}')">
              <div class="goal-icon">${g.icon}</div>
              <h3 class="goal-title">${g.title}</h3>
              <p class="goal-desc">${g.description}</p>
              <div style="font-size: 11.5px; color: var(--text-muted); margin-top: 8px;">
                <i>Example: "${g.example}"</i>
              </div>
            </div>
          `).join('')}
        </div>
      </div>

      <!-- Step 2: Recommendations Container -->
      <div id="chart-recommendations-section">
        <div style="text-align: center; padding: 24px;"><div class="spinner"></div></div>
      </div>

      <!-- Step 3: Interactive Chart Viewer Container -->
      <div id="chart-viewer-section" style="display: none; margin-top: 24px;"></div>
    `;

    loadGoalRecommendations(state.chartState.selectedGoal);

  } catch (err) {
    container.innerHTML = `<div class="alert alert-danger">${err.message}</div>`;
  }
}

window.selectChartGoal = function(goalKey) {
  state.chartState.selectedGoal = goalKey;
  document.querySelectorAll(".goal-card").forEach(el => el.classList.remove("active"));
  event.currentTarget?.classList.add("active");
  loadGoalRecommendations(goalKey);
};

async function loadGoalRecommendations(goalKey) {
  const container = document.getElementById("chart-recommendations-section");
  if (!container) return;
  container.innerHTML = `<div style="text-align: center; padding: 24px;"><div class="spinner"></div></div>`;

  try {
    const res = await DataPilotAPI.getChartRecommendations(state.activeDatasetId, goalKey);
    const recs = res.recommendations || [];

    if (recs.length === 0) {
      container.innerHTML = `
        <div class="alert alert-warning">
          No suitable charts could be automatically recommended for this goal with the available column datatypes.
        </div>
      `;
      return;
    }

    container.innerHTML = `
      <h3 class="section-heading">Step 2: Recommended Chart Types for "${res.goal_title}"</h3>
      <div class="rec-grid">
        ${recs.map((rec, idx) => `
          <div class="rec-card ${idx === 0 ? 'active' : ''}" id="rec-card-${idx}">
            <div>
              <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                <h4 style="font-size: 17px; font-weight: 700; color: var(--text-primary);">${rec.chart_type}</h4>
                <span class="badge ${rec.badge === 'Highly Recommended' ? 'badge-lime' : 'badge-lavender'}">${rec.badge}</span>
              </div>
              <p style="font-size: 13.5px; color: var(--text-secondary); margin-bottom: 12px; line-height: 1.45;">
                ${rec.why_useful}
              </p>
              <div style="font-size: 12.5px; background: #F8F9FA; padding: 8px 10px; border-radius: 6px; margin-bottom: 12px;">
                <strong>Columns Needed:</strong> ${rec.columns_needed}
              </div>
            </div>
            <button class="btn btn-primary btn-sm" onclick='openChartViewer(${JSON.stringify(rec)})'>
              Generate ${rec.chart_type} &rarr;
            </button>
          </div>
        `).join('')}
      </div>
    `;

    // Automatically open first recommended chart
    if (recs.length > 0) {
      openChartViewer(recs[0]);
    }

  } catch (err) {
    container.innerHTML = `<div class="alert alert-danger">${err.message}</div>`;
  }
}

window.openChartViewer = async function(rec) {
  state.chartState.currentChartType = rec.chart_type;
  state.chartState.xCol = rec.suggested_x;
  state.chartState.yCol = rec.suggested_y;
  state.chartState.aggFunc = rec.suggested_agg || "mean";
  state.chartState.colorCol = rec.suggested_color || null;

  const viewer = document.getElementById("chart-viewer-section");
  if (!viewer) return;
  viewer.style.display = "block";

  try {
    const preview = await DataPilotAPI.getPreview(state.activeDatasetId, 1, 1);
    const cols = preview.columns;

    viewer.innerHTML = `
      <div class="card">
        <div class="card-header">
          <div>
            <h3 class="card-title">Interactive Chart: ${rec.chart_type}</h3>
            <p class="card-subtitle">Adjust axes and aggregations below to explore your data</p>
          </div>
          <span class="badge badge-lavender">Plotly Interactive</span>
        </div>

        <!-- Chart Controls -->
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 14px; background: #F8F9FA; padding: 14px 18px; border-radius: var(--radius-md); margin-bottom: 18px;">
          <div>
            <label class="form-label" style="font-size: 13px;">X-Axis Feature:</label>
            <select class="form-select" id="chart-select-x" style="font-size: 13px; padding: 7px 10px;">
              <option value="">(None)</option>
              ${cols.map(c => `<option value="${c}" ${c === state.chartState.xCol ? 'selected' : ''}>${c}</option>`).join('')}
            </select>
          </div>
          <div>
            <label class="form-label" style="font-size: 13px;">Y-Axis Metric:</label>
            <select class="form-select" id="chart-select-y" style="font-size: 13px; padding: 7px 10px;">
              <option value="">(None)</option>
              ${cols.map(c => `<option value="${c}" ${c === state.chartState.yCol ? 'selected' : ''}>${c}</option>`).join('')}
            </select>
          </div>
          <div>
            <label class="form-label" style="font-size: 13px;">Aggregation:</label>
            <select class="form-select" id="chart-select-agg" style="font-size: 13px; padding: 7px 10px;">
              <option value="mean" ${state.chartState.aggFunc === 'mean' ? 'selected' : ''}>Average (Mean)</option>
              <option value="sum" ${state.chartState.aggFunc === 'sum' ? 'selected' : ''}>Total (Sum)</option>
              <option value="count" ${state.chartState.aggFunc === 'count' ? 'selected' : ''}>Count of Records</option>
              <option value="median" ${state.chartState.aggFunc === 'median' ? 'selected' : ''}>Median</option>
              <option value="min" ${state.chartState.aggFunc === 'min' ? 'selected' : ''}>Minimum</option>
              <option value="max" ${state.chartState.aggFunc === 'max' ? 'selected' : ''}>Maximum</option>
            </select>
          </div>
          <div style="display: flex; align-items: flex-end;">
            <button class="btn btn-primary" id="btn-update-chart" style="width: 100%;">Update Chart</button>
          </div>
        </div>

        <!-- Chart Plot Area -->
        <div id="plotly-active-chart" style="min-height: 440px; display: flex; align-items: center; justify-content: center;">
          <div class="spinner"></div>
        </div>

        <!-- Academic & Beginner Guidance Breakdown -->
        <div style="margin-top: 20px; display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 16px;">
          <div style="background: #FFFFFF; border: 1px solid var(--border-color); border-radius: var(--radius-md); padding: 14px 16px;">
            <h5 style="font-size: 13.5px; font-weight: 700; color: var(--text-primary); margin-bottom: 6px;">🎯 Axes Breakdown:</h5>
            <p style="font-size: 13px; color: var(--text-secondary); line-height: 1.4;">${rec.axes_explanation}</p>
          </div>
          <div style="background: #FFFFFF; border: 1px solid var(--border-color); border-radius: var(--radius-md); padding: 14px 16px;">
            <h5 style="font-size: 13.5px; font-weight: 700; color: var(--text-primary); margin-bottom: 6px;">👀 What to Look For:</h5>
            <p style="font-size: 13px; color: var(--text-secondary); line-height: 1.4;">${rec.what_to_look_for}</p>
          </div>
          <div style="background: #FFFFFF; border: 1px solid var(--border-color); border-radius: var(--radius-md); padding: 14px 16px;">
            <h5 style="font-size: 13.5px; font-weight: 700; color: var(--text-primary); margin-bottom: 6px;">⚠️ When to Avoid:</h5>
            <p style="font-size: 13px; color: var(--text-secondary); line-height: 1.4;">${rec.when_to_avoid}</p>
          </div>
        </div>

        <!-- Grounded Mathematical Insights -->
        <div id="chart-observations-box" style="margin-top: 16px;"></div>
      </div>
    `;

    // Render Chart
    await renderActivePlotlyChart();

    // Bind Update Button
    document.getElementById("btn-update-chart")?.addEventListener("click", async () => {
      state.chartState.xCol = document.getElementById("chart-select-x").value || null;
      state.chartState.yCol = document.getElementById("chart-select-y").value || null;
      state.chartState.aggFunc = document.getElementById("chart-select-agg").value || "mean";
      await renderActivePlotlyChart();
    });

    viewer.scrollIntoView({ behavior: "smooth" });

  } catch (err) {
    console.error("Failed to render chart controls:", err);
  }
};

async function renderActivePlotlyChart() {
  const container = document.getElementById("plotly-active-chart");
  const obsBox = document.getElementById("chart-observations-box");
  if (!container) return;

  container.innerHTML = `<div class="spinner"></div>`;

  try {
    const res = await DataPilotAPI.renderChart(state.activeDatasetId, {
      chart_type: state.chartState.currentChartType,
      x_col: state.chartState.xCol,
      y_col: state.chartState.yCol,
      agg_func: state.chartState.aggFunc,
      color_col: state.chartState.colorCol
    });

    if (res.figure) {
      Plotly.newPlot(container, res.figure.data, res.figure.layout, { responsive: true, displayModeBar: true });
    }

    if (obsBox && res.observations && res.observations.length > 0) {
      obsBox.innerHTML = `
        <div class="alert alert-info" style="margin-bottom: 0;">
          <div>
            <strong style="display: block; margin-bottom: 4px;">📊 Grounded Mathematical Observations:</strong>
            <ul style="padding-left: 20px; font-size: 13.5px;">
              ${res.observations.map(obs => `<li>${obs}</li>`).join('')}
            </ul>
          </div>
        </div>
      `;
    } else if (obsBox) {
      obsBox.innerHTML = "";
    }

  } catch (err) {
    container.innerHTML = `<div class="alert alert-danger">${err.message}</div>`;
  }
}

/* ==========================================================================
   PAGE 6: SQL ASSISTANT
   ========================================================================== */
async function renderSQLPage(container) {
  container.innerHTML = `
    <!-- Natural Language Query Bar -->
    <div class="card" style="padding: 16px 20px;">
      <label class="form-label" style="font-size: 13.5px;">Convert Question to SQL (Natural Language):</label>
      <div style="display: flex; gap: 10px;">
        <input type="text" id="nl-sql-input" class="form-input" placeholder="e.g., Top 5 categories by total revenue" />
        <button class="btn btn-secondary btn-sm" id="btn-generate-sql">Generate SQL</button>
      </div>
    </div>

    <!-- SQL Query Editor -->
    <div class="card">
      <div class="card-header">
        <div>
          <h2 class="card-title">DuckDB Analytical Query Editor</h2>
          <p class="card-subtitle">Query table <code>data</code> using standard in-memory analytical SQL</p>
        </div>
        <span class="badge badge-success">🔒 Read-Only Sandbox Active</span>
      </div>

      <div class="sql-editor-container">
        <textarea id="sql-editor" class="sql-textarea" spellcheck="false">SELECT * FROM data LIMIT 10;</textarea>
      </div>

      <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 14px;">
        <div style="display: flex; gap: 8px;">
          <button class="btn btn-primary" id="btn-run-sql">▶ Run Query</button>
          <button class="btn btn-secondary btn-sm" id="btn-explain-sql">Explain Query</button>
        </div>
        <button class="btn btn-secondary btn-sm" id="btn-download-sql-csv" style="display: none;">
          📥 Download Results as CSV
        </button>
      </div>

      <!-- Query Templates -->
      <div style="margin-top: 16px; padding-top: 14px; border-top: 1px solid var(--border-color-light);">
        <label style="font-size: 12.5px; font-weight: 700; color: var(--text-secondary); text-transform: uppercase;">
          Pre-Built Query Templates for this Dataset:
        </label>
        <div class="chips-container" id="sql-templates-container">
          <span style="font-size: 12.5px; color: var(--text-muted);">Loading templates...</span>
        </div>
      </div>
    </div>

    <!-- Query Explanation Output -->
    <div id="sql-explanation-box" style="display: none; margin-bottom: 20px;"></div>

    <!-- Query Results Panel -->
    <div class="card" id="sql-results-card" style="display: none;">
      <div class="card-header">
        <div>
          <h3 class="card-title">Query Results</h3>
          <p class="card-subtitle" id="sql-execution-stats">0 rows returned</p>
        </div>
      </div>
      <div id="sql-results-table"></div>
    </div>
  `;

  // Fetch Templates
  try {
    const tRes = await DataPilotAPI.getSQLTemplates(state.activeDatasetId);
    const tBox = document.getElementById("sql-templates-container");
    if (tBox && tRes.templates) {
      tBox.innerHTML = tRes.templates.map(t => `
        <span class="chip" onclick="loadSQLTemplate('${encodeURIComponent(t.sql)}')">${t.title}</span>
      `).join('');
    }
  } catch (err) {
    console.error("Templates failed:", err);
  }

  // Bind Run Query
  document.getElementById("btn-run-sql")?.addEventListener("click", executeUserSQL);

  // Bind Explain Query
  document.getElementById("btn-explain-sql")?.addEventListener("click", explainUserSQL);

  // Bind Generate SQL
  document.getElementById("btn-generate-sql")?.addEventListener("click", async () => {
    const q = document.getElementById("nl-sql-input").value.trim();
    if (!q) return;
    try {
      const res = await DataPilotAPI.generateSQL(state.activeDatasetId, q);
      document.getElementById("sql-editor").value = res.generated_sql;
      showToast("Generated SQL query from your question!", "success");
    } catch (err) {
      showToast(`SQL generation failed: ${err.message}`, "error");
    }
  });

  // Bind Download CSV
  document.getElementById("btn-download-sql-csv")?.addEventListener("click", () => {
    const query = document.getElementById("sql-editor").value;
    DataPilotAPI.downloadSQLResults(state.activeDatasetId, query);
  });
}

window.loadSQLTemplate = function(encodedSQL) {
  document.getElementById("sql-editor").value = decodeURIComponent(encodedSQL);
};

async function executeUserSQL() {
  const query = document.getElementById("sql-editor").value.trim();
  const resultsCard = document.getElementById("sql-results-card");
  const statsElem = document.getElementById("sql-execution-stats");
  const tableElem = document.getElementById("sql-results-table");
  const dlBtn = document.getElementById("btn-download-sql-csv");

  if (!query) return;

  resultsCard.style.display = "block";
  tableElem.innerHTML = `<div style="text-align: center; padding: 32px;"><div class="spinner"></div></div>`;

  try {
    const res = await DataPilotAPI.executeSQL(state.activeDatasetId, query);

    if (!res.success) {
      statsElem.textContent = `Query error (${res.execution_time_ms} ms)`;
      tableElem.innerHTML = `<div class="alert alert-danger">${res.error}</div>`;
      dlBtn.style.display = "none";
      return;
    }

    statsElem.textContent = `${formatNumber(res.row_count)} rows fetched in ${res.execution_time_ms} ms`;
    dlBtn.style.display = "inline-flex";

    if (res.rows.length === 0) {
      tableElem.innerHTML = `<p style="padding: 16px; color: var(--text-secondary);">Query executed successfully. 0 rows returned.</p>`;
      return;
    }

    tableElem.innerHTML = `
      <div class="table-responsive">
        <table class="data-table">
          <thead>
            <tr>${res.columns.map(c => `<th>${c}</th>`).join('')}</tr>
          </thead>
          <tbody>
            ${res.rows.slice(0, 100).map(r => `
              <tr>${res.columns.map(c => `<td>${r[c] !== null && r[c] !== undefined ? r[c] : '<i style="color:var(--text-muted)">null</i>'}</td>`).join('')}</tr>
            `).join('')}
          </tbody>
        </table>
      </div>
      ${res.row_count > 100 ? `<div class="pagination-bar"><span>Showing top 100 rows in preview. Use Download CSV for full result set.</span></div>` : ''}
    `;

  } catch (err) {
    statsElem.textContent = "Execution failed";
    tableElem.innerHTML = `<div class="alert alert-danger">${err.message}</div>`;
  }
}

async function explainUserSQL() {
  const query = document.getElementById("sql-editor").value.trim();
  const box = document.getElementById("sql-explanation-box");
  if (!box || !query) return;

  box.style.display = "block";
  box.innerHTML = `<div class="card"><div class="spinner"></div></div>`;

  try {
    const res = await DataPilotAPI.explainSQL(state.activeDatasetId, query);
    box.innerHTML = `
      <div class="card">
        <div class="card-header">
          <h4 class="card-title">📖 Beginner Query Breakdown</h4>
          <span class="badge badge-lavender">Academic Explanation</span>
        </div>
        <p style="font-size: 14.5px; line-height: 1.5; color: var(--text-primary); margin-bottom: 14px;">
          ${res.summary}
        </p>
        <div style="display: grid; gap: 8px;">
          ${Object.entries(res.clauses).map(([clause, desc]) => `
            <div style="background: #F8F9FA; padding: 10px 14px; border-radius: 6px; font-size: 13.5px;">
              <strong style="color: var(--text-primary);">${clause}:</strong> ${desc}
            </div>
          `).join('')}
        </div>
      </div>
    `;
  } catch (err) {
    box.innerHTML = `<div class="alert alert-danger">${err.message}</div>`;
  }
}

/* ==========================================================================
   PAGE 7: AI DATA ANALYST
   ========================================================================== */
async function renderAnalystPage(container) {
  container.innerHTML = `
    <!-- Question Input Card -->
    <div class="card">
      <div class="card-header">
        <div>
          <h2 class="card-title">Ask Your AI Data Analyst</h2>
          <p class="card-subtitle">Ask questions in plain English. Numerical findings are grounded in real calculations.</p>
        </div>
        <span class="badge badge-lime">Zero Hallucinations</span>
      </div>

      <div style="display: flex; gap: 10px;">
        <input type="text" id="analyst-query-input" class="form-input" style="font-size: 15px; padding: 11px 14px;" placeholder="e.g., Which category contributes most to overall volume?" />
        <button class="btn btn-primary" id="btn-ask-analyst">Ask Question</button>
      </div>

      <!-- Suggested Question Chips -->
      <div style="margin-top: 14px;">
        <span style="font-size: 12.5px; font-weight: 700; color: var(--text-secondary); text-transform: uppercase;">
          Suggested Questions for this Dataset:
        </span>
        <div class="chips-container" id="analyst-chips-container">
          <span style="font-size: 12.5px; color: var(--text-muted);">Loading suggested questions...</span>
        </div>
      </div>
    </div>

    <!-- Result Container -->
    <div id="analyst-result-container"></div>
  `;

  // Fetch Suggested Questions
  try {
    const qRes = await DataPilotAPI.getSuggestedQuestions(state.activeDatasetId);
    const cBox = document.getElementById("analyst-chips-container");
    if (cBox && qRes.questions) {
      cBox.innerHTML = qRes.questions.map(q => `
        <span class="chip" onclick="runAnalystQuestion('${encodeURIComponent(q)}')">${q}</span>
      `).join('');
    }
  } catch (err) {
    console.error("Suggested questions error:", err);
  }

  // Bind Ask Button
  document.getElementById("btn-ask-analyst")?.addEventListener("click", () => {
    const q = document.getElementById("analyst-query-input").value.trim();
    if (q) runAnalystQuestion(encodeURIComponent(q));
  });
}

window.runAnalystQuestion = async function(encodedQ) {
  const question = decodeURIComponent(encodedQ);
  const input = document.getElementById("analyst-query-input");
  if (input) input.value = question;

  const resultContainer = document.getElementById("analyst-result-container");
  if (!resultContainer) return;

  resultContainer.innerHTML = `
    <div class="card" style="text-align: center; padding: 40px;">
      <div class="spinner"></div>
      <p style="margin-top: 10px; color: var(--text-secondary);">Calculating mathematical metrics on ${state.activeDataset.name}...</p>
    </div>
  `;

  try {
    const res = await DataPilotAPI.askAnalyst(state.activeDatasetId, question);

    resultContainer.innerHTML = `
      <div class="analyst-result-card">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
          <span class="badge badge-gray">Question: "${res.question}"</span>
          <span class="badge ${res.mode === 'llm' ? 'badge-lavender' : 'badge-lime'}">
            ${res.mode === 'llm' ? 'LLM Synthesis' : '100% Offline Deterministic Math'}
          </span>
        </div>

        <!-- Primary Key Finding -->
        <div class="analyst-key-finding">
          ${res.primary_finding}
        </div>

        <!-- Bullet Points -->
        ${res.bullet_points.length > 0 ? `
          <ul style="padding-left: 20px; font-size: 15px; line-height: 1.6; color: var(--text-primary); margin-bottom: 18px;">
            ${res.bullet_points.map(bp => `<li>${bp}</li>`).join('')}
          </ul>
        ` : ''}

        <!-- Accompanying Plotly Chart (if present) -->
        ${res.has_chart ? `
          <div style="margin: 20px 0; border: 1px solid var(--border-color); border-radius: var(--radius-md); padding: 12px;">
            <div id="analyst-chart" style="min-height: 380px;"></div>
          </div>
        ` : ''}

        <!-- Expandable Calculation Details -->
        <details style="margin-top: 16px; background: #F8F9FA; border: 1px solid var(--border-color); border-radius: var(--radius-md); padding: 12px 16px;">
          <summary style="font-size: 13.5px; font-weight: 700; color: var(--text-primary); cursor: pointer;">
            🔬 How Was This Calculated? (Academic Methodology)
          </summary>
          <p style="font-size: 13px; color: var(--text-secondary); margin-top: 8px; line-height: 1.45;">
            ${res.calculation_details}
          </p>
        </details>
      </div>
    `;

    if (res.has_chart && res.chart_figure) {
      Plotly.newPlot("analyst-chart", res.chart_figure.data, res.chart_figure.layout, { responsive: true, displayModeBar: false });
    }

  } catch (err) {
    resultContainer.innerHTML = `<div class="alert alert-danger">${err.message}</div>`;
  }
};

/* ==========================================================================
   PAGE 8: MACHINE LEARNING LAB
   ========================================================================== */
async function renderMLPage(container) {
  container.innerHTML = `
    <div class="card" style="text-align: center; padding: 40px;">
      <div class="spinner"></div>
      <p style="margin-top: 10px; color: var(--text-secondary);">Initializing Scikit-learn predictive modeling studio...</p>
    </div>
  `;

  try {
    const schema = await DataPilotAPI.getMLSchema(state.activeDatasetId);
    const cols = schema.columns || [];

    if (cols.length < 2) {
      container.innerHTML = `
        <div class="empty-state">
          <div class="empty-state-icon">⚠️</div>
          <h2 class="empty-state-title">Dataset Unsuitable for Machine Learning</h2>
          <p class="empty-state-text">Predictive modeling requires at least 1 feature column and 1 target column (minimum 2 columns total).</p>
        </div>
      `;
      return;
    }

    // Default target
    const defaultTarget = state.mlState.targetCol || schema.default_target || cols[cols.length - 1];

    container.innerHTML = `
      <!-- Step 1: Target Feature & Task Auto-Detection -->
      <div class="card">
        <div class="card-header">
          <div>
            <h2 class="card-title">Step 1: Select Target Feature (y) &amp; Modeling Task</h2>
            <p class="card-subtitle">Choose the feature you want to predict. DataPilot AI automatically infers whether it is Classification or Regression.</p>
          </div>
          <span class="badge badge-lavender">Scikit-Learn Pipeline</span>
        </div>

        <div class="form-row">
          <div>
            <label class="form-label">Choose Target Feature (y):</label>
            <select class="form-select" id="ml-target-select">
              ${cols.map(c => `<option value="${c}" ${c === defaultTarget ? 'selected' : ''}>${c}</option>`).join('')}
            </select>
          </div>
          <div>
            <label class="form-label">Task Type Selection:</label>
            <div style="display: flex; gap: 14px; margin-top: 8px;">
              <label style="display: flex; align-items: center; gap: 6px; font-size: 14.5px; cursor: pointer;">
                <input type="radio" name="ml-task" value="Classification" id="task-classification" checked />
                Classification
              </label>
              <label style="display: flex; align-items: center; gap: 6px; font-size: 14.5px; cursor: pointer;">
                <input type="radio" name="ml-task" value="Regression" id="task-regression" />
                Regression
              </label>
            </div>
          </div>
        </div>

        <!-- Target Inspection Card -->
        <div id="ml-target-inspection-box" style="margin-top: 16px;">
          <div class="spinner"></div>
        </div>
      </div>

      <!-- Step 2: Feature Selection & Leakage Safeguards -->
      <div class="card" id="ml-features-card" style="display: none;">
        <div class="card-header">
          <div>
            <h3 class="card-title">Step 2: Feature Selection (X) &amp; Target Leakage Safeguards</h3>
            <p class="card-subtitle">Features with extreme correlation (|r| &ge; 0.95) or unique identifier patterns are flagged</p>
          </div>
          <span class="badge badge-gray" id="features-selected-count">0 Selected</span>
        </div>

        <!-- Leakage Alerts Container -->
        <div id="ml-leakage-alerts"></div>

        <!-- Feature Checkbox Grid -->
        <div style="margin-top: 12px;">
          <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
            <label class="form-label" style="font-size: 13.5px;">Select features to include in training:</label>
            <div style="display: flex; gap: 8px;">
              <button class="btn btn-sm btn-secondary" id="btn-select-all-features">Select All</button>
              <button class="btn btn-sm btn-secondary" id="btn-smart-features">Smart Selection</button>
            </div>
          </div>
          <div id="ml-features-checkbox-grid" style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 10px; max-height: 240px; overflow-y: auto; background: #F8F9FA; padding: 14px; border-radius: var(--radius-md); border: 1px solid var(--border-color);"></div>
        </div>
      </div>

      <!-- Step 3: Train Config & Split -->
      <div class="card" id="ml-train-config-card" style="display: none;">
        <div class="card-header">
          <h3 class="card-title">Step 3: Training Strategy &amp; Test Split</h3>
        </div>

        <div class="form-row">
          <div>
            <label class="form-label">Train / Test Split Ratio:</label>
            <div class="slider-container">
              <input type="range" class="slider-input" id="ml-split-slider" min="10" max="40" step="5" value="20" />
              <span class="slider-value" id="ml-split-val">20%</span>
            </div>
            <p class="form-hint" id="ml-split-hint">Train on 80% of data, evaluate on 20% out-of-sample test records.</p>
          </div>
          <div style="display: flex; align-items: flex-end;">
            <button class="btn btn-primary btn-lg" id="btn-start-ml-train" style="width: 100%;">
              🚀 Train Models &amp; Evaluate Leaderboard
            </button>
          </div>
        </div>
      </div>

      <!-- Step 4: Leaderboard & Diagnostics -->
      <div id="ml-results-container"></div>

      <!-- Step 5: What-If Live Prediction Studio -->
      <div id="ml-prediction-studio" style="display: none; margin-top: 24px;"></div>
    `;

    // Target change event
    const targetSelect = document.getElementById("ml-target-select");
    targetSelect.addEventListener("change", (e) => inspectMLTarget(e.target.value));

    // Split slider event
    const slider = document.getElementById("ml-split-slider");
    slider.addEventListener("input", (e) => {
      const val = e.target.value;
      document.getElementById("ml-split-val").textContent = `${val}%`;
      document.getElementById("ml-split-hint").textContent = `Train on ${100 - val}% of data, evaluate on ${val}% out-of-sample test records.`;
      state.mlState.testSize = val / 100.0;
    });

    // Inspect initial target
    await inspectMLTarget(defaultTarget);

    // Bind Train Button
    document.getElementById("btn-start-ml-train")?.addEventListener("click", executeMLTraining);

  } catch (err) {
    container.innerHTML = `<div class="alert alert-danger">${err.message}</div>`;
  }
}

async function inspectMLTarget(targetCol) {
  state.mlState.targetCol = targetCol;
  const box = document.getElementById("ml-target-inspection-box");
  const featCard = document.getElementById("ml-features-card");
  const configCard = document.getElementById("ml-train-config-card");
  if (!box) return;

  box.innerHTML = `<div class="spinner"></div>`;

  try {
    const res = await DataPilotAPI.inspectTarget(state.activeDatasetId, targetCol);
    state.mlState.taskType = res.task_type;

    // Update Radio buttons
    if (res.task_type === "Classification") {
      document.getElementById("task-classification").checked = true;
    } else if (res.task_type === "Regression") {
      document.getElementById("task-regression").checked = true;
    }

    if (!res.is_valid) {
      box.innerHTML = `
        <div class="alert alert-danger">
          <strong>Unsuitable Target Feature:</strong> ${res.description}
        </div>
      `;
      featCard.style.display = "none";
      configCard.style.display = "none";
      return;
    }

    // Show feature selection & config
    featCard.style.display = "block";
    configCard.style.display = "block";

    // Target summary box
    box.innerHTML = `
      <div class="alert alert-info" style="margin-bottom: 0;">
        <div>
          <strong style="color: var(--text-primary); font-size: 14.5px;">Auto-Detected Task: ${res.task_type}</strong>
          <p style="margin-top: 4px; font-size: 13.5px; color: var(--text-secondary);">${res.description}</p>
          ${res.class_distribution ? `
            <div style="margin-top: 6px; font-size: 12.5px; color: var(--text-secondary);">
              <strong>Class Counts:</strong> ${Object.entries(res.class_distribution).map(([k, v]) => `${k} (${v})`).join(', ')}
            </div>
          ` : ''}
          ${res.numeric_min !== null && res.numeric_min !== undefined ? `
            <div style="margin-top: 6px; font-size: 12.5px; color: var(--text-secondary);">
              <strong>Range:</strong> Min ${res.numeric_min} • Median ${res.numeric_median} • Max ${res.numeric_max}
            </div>
          ` : ''}
        </div>
      </div>
    `;

    // Render Leakage Alerts
    const leakageContainer = document.getElementById("ml-leakage-alerts");
    if (res.leakage_warnings && res.leakage_warnings.length > 0) {
      leakageContainer.innerHTML = res.leakage_warnings.map(lw => `
        <div class="alert alert-warning" style="font-size: 13.5px; margin-bottom: 10px;">
          ⚠️ <strong>Target Leakage / ID Alert:</strong> ${lw.warning}
        </div>
      `).join('');
    } else {
      leakageContainer.innerHTML = "";
    }

    // Render Features Checkboxes
    const grid = document.getElementById("ml-features-checkbox-grid");
    const smartDefaults = new Set(res.smart_default_features || []);

    grid.innerHTML = res.candidate_features.map(f => `
      <label style="display: flex; align-items: center; gap: 8px; font-size: 13.5px; cursor: pointer;">
        <input type="checkbox" class="feature-checkbox" value="${f}" ${smartDefaults.has(f) ? 'checked' : ''} />
        <span style="white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">${f}</span>
      </label>
    `).join('');

    updateSelectedFeaturesCount();

    // Bind Feature check change
    grid.querySelectorAll(".feature-checkbox").forEach(cb => {
      cb.addEventListener("change", updateSelectedFeaturesCount);
    });

    document.getElementById("btn-select-all-features")?.addEventListener("click", () => {
      grid.querySelectorAll(".feature-checkbox").forEach(cb => cb.checked = true);
      updateSelectedFeaturesCount();
    });

    document.getElementById("btn-smart-features")?.addEventListener("click", () => {
      grid.querySelectorAll(".feature-checkbox").forEach(cb => {
        cb.checked = smartDefaults.has(cb.value);
      });
      updateSelectedFeaturesCount();
    });

  } catch (err) {
    box.innerHTML = `<div class="alert alert-danger">${err.message}</div>`;
  }
}

function updateSelectedFeaturesCount() {
  const checked = document.querySelectorAll(".feature-checkbox:checked");
  const countBadge = document.getElementById("features-selected-count");
  if (countBadge) countBadge.textContent = `${checked.length} Selected`;
  state.mlState.selectedFeatures = Array.from(checked).map(c => c.value);

  const trainBtn = document.getElementById("btn-start-ml-train");
  if (trainBtn) trainBtn.disabled = checked.length === 0;
}

async function executeMLTraining() {
  const container = document.getElementById("ml-results-container");
  const studio = document.getElementById("ml-prediction-studio");
  if (!container) return;

  const targetCol = state.mlState.targetCol;
  const features = state.mlState.selectedFeatures;
  const taskType = document.querySelector('input[name="ml-task"]:checked')?.value || "Classification";
  const testSplit = state.mlState.testSize || 0.2;

  container.innerHTML = `
    <div class="card" style="text-align: center; padding: 48px;">
      <div class="spinner"></div>
      <h3 style="font-size: 18px; font-weight: 700; margin-top: 14px;">Training Scikit-Learn Pipelines...</h3>
      <p style="color: var(--text-secondary); margin-top: 6px;">
        Applying ColumnTransformer (StandardScaler, OneHotEncoder) strictly on train split &bull; Benchmarking candidate models
      </p>
    </div>
  `;

  try {
    const res = await DataPilotAPI.trainML(state.activeDatasetId, {
      target_col: targetCol,
      feature_cols: features,
      task_type: taskType,
      test_size: testSplit
    });

    state.mlState.trainedResults = res;

    container.innerHTML = `
      <!-- Leaderboard Card -->
      <div class="card" style="margin-top: 24px;">
        <div class="card-header">
          <div>
            <h3 class="card-title">🏆 Model Performance Leaderboard (${res.task_type})</h3>
            <p class="card-subtitle">Trained on ${formatNumber(res.training_sample_count)} samples, evaluated on ${formatNumber(res.test_sample_count)} test records</p>
          </div>
          <span class="badge badge-lime">Out-of-Sample Evaluation</span>
        </div>

        <!-- Top Performing Model Banner -->
        <div class="best-model-banner">
          <div>
            <span style="font-size: 13px; font-weight: 700; text-transform: uppercase; color: #3B5200;">Top Performing Algorithm:</span>
            <div style="font-size: 20px; font-weight: 800; color: #202124; margin-top: 2px;">${res.best_model_name}</div>
          </div>
          <span class="badge badge-lime">Recommended for Inference</span>
        </div>

        <!-- Leaderboard Table -->
        <div class="table-responsive">
          <table class="data-table">
            <thead>
              <tr>
                ${Object.keys(res.leaderboard[0] || {}).map(k => `<th>${k}</th>`).join('')}
              </tr>
            </thead>
            <tbody>
              ${res.leaderboard.map((m, idx) => `
                <tr style="${idx === 0 ? 'background-color: var(--accent-lime-tint); font-weight: 600;' : ''}">
                  ${Object.values(m).map(val => `<td>${val}</td>`).join('')}
                </tr>
              `).join('')}
            </tbody>
          </table>
        </div>

        <!-- Academic Metric Guide Expander -->
        <details style="margin-top: 16px; background: #F8F9FA; border: 1px solid var(--border-color); border-radius: var(--radius-md); padding: 12px 16px;">
          <summary style="font-size: 13.5px; font-weight: 700; color: var(--text-primary); cursor: pointer;">
            📖 Academic Metric Explanation Guide
          </summary>
          <div style="font-size: 13px; color: var(--text-secondary); margin-top: 8px; line-height: 1.5;">
            ${res.task_type === "Classification" ? `
              <p><strong>Accuracy:</strong> Proportion of correct predictions out of total samples.</p>
              <p><strong>Precision:</strong> Exactness (TP / (TP + FP)). High precision avoids false alarms.</p>
              <p><strong>Recall:</strong> Sensitivity (TP / (TP + FN)). High recall captures true positives.</p>
              <p><strong>F1-Score:</strong> Harmonic mean of Precision and Recall. Preferred metric for imbalanced classes.</p>
            ` : `
              <p><strong>MAE:</strong> Mean Absolute Error (|y - ŷ|). Expressed directly in original target units.</p>
              <p><strong>RMSE:</strong> Root Mean Squared Error. Heavily penalizes large prediction outliers.</p>
              <p><strong>R² Score:</strong> Coefficient of Determination (0 to 1.0). Proportion of variance explained by features.</p>
            `}
          </div>
        </details>
      </div>

      <!-- Diagnostic Charts Grid -->
      <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(460px, 1fr)); gap: 20px; margin-top: 20px;">
        <!-- Confusion Matrix or Actual vs Predicted -->
        <div class="card">
          <div class="card-header">
            <h4 class="card-title">${res.task_type === 'Classification' ? 'Confusion Matrix' : 'Actual vs. Predicted'}</h4>
          </div>
          <div id="ml-diag-plot" style="min-height: 380px;"></div>
        </div>

        <!-- Feature Importances -->
        <div class="card">
          <div class="card-header">
            <h4 class="card-title">Top Feature Importances</h4>
          </div>
          <div id="ml-imp-plot" style="min-height: 380px;"></div>
        </div>
      </div>
    `;

    // Render diagnostic plots
    if (res.task_type === "Classification" && res.confusion_matrix_fig) {
      Plotly.newPlot("ml-diag-plot", res.confusion_matrix_fig.data, res.confusion_matrix_fig.layout, { responsive: true, displayModeBar: false });
    } else if (res.regression_plot_fig) {
      Plotly.newPlot("ml-diag-plot", res.regression_plot_fig.data, res.regression_plot_fig.layout, { responsive: true, displayModeBar: false });
    }

    if (res.feature_importance_fig) {
      Plotly.newPlot("ml-imp-plot", res.feature_importance_fig.data, res.feature_importance_fig.layout, { responsive: true, displayModeBar: false });
    }

    // Render What-If Live Prediction Studio
    renderPredictionStudio(studio, res);

  } catch (err) {
    container.innerHTML = `<div class="alert alert-danger">${err.message}</div>`;
  }
}

function renderPredictionStudio(container, trainRes) {
  if (!container || !trainRes) return;
  container.style.display = "block";

  const specs = trainRes.feature_specs || {};
  const trainedModels = trainRes.leaderboard.map(m => m.Model);

  container.innerHTML = `
    <div class="card">
      <div class="card-header">
        <div>
          <h3 class="card-title">🔮 Interactive What-If Scenario Live Predictor</h3>
          <p class="card-subtitle">Adjust input features below to generate live model predictions in real time</p>
        </div>
        <div style="display: flex; align-items: center; gap: 8px;">
          <label style="font-size: 13px; font-weight: 600;">Model Algorithm:</label>
          <select class="form-select" id="ml-inference-model" style="font-size: 13px; padding: 6px 10px;">
            ${trainedModels.map(m => `<option value="${m}" ${m === trainRes.best_model_name ? 'selected' : ''}>${m}</option>`).join('')}
          </select>
        </div>
      </div>

      <!-- Dynamic Feature Inputs Grid -->
      <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(260px, 1fr)); gap: 16px; margin-bottom: 20px;">
        ${Object.entries(specs).map(([feat, spec]) => {
          if (spec.type === "numeric") {
            return `
              <div>
                <div style="display: flex; justify-content: space-between; font-size: 13px; margin-bottom: 4px;">
                  <span style="font-weight: 600;">${feat}</span>
                  <span id="pred-val-${feat}" style="font-weight: 700; color: var(--text-primary);">${spec.default}</span>
                </div>
                <input type="range" class="slider-input ml-pred-input" data-feature="${feat}" min="${spec.min}" max="${spec.max}" step="${(spec.max - spec.min) / 100}" value="${spec.default}" oninput="document.getElementById('pred-val-${feat}').textContent = this.value" style="width: 100%;" />
                <div style="display: flex; justify-content: space-between; font-size: 11px; color: var(--text-muted); margin-top: 2px;">
                  <span>${spec.min}</span><span>${spec.max}</span>
                </div>
              </div>
            `;
          } else {
            return `
              <div>
                <label class="form-label" style="font-size: 13px;">${feat}</label>
                <select class="form-select ml-pred-input" data-feature="${feat}">
                  ${spec.options.map(opt => `<option value="${opt}" ${opt === spec.default ? 'selected' : ''}>${opt}</option>`).join('')}
                </select>
              </div>
            `;
          }
        }).join('')}
      </div>

      <div style="display: flex; justify-content: flex-end;">
        <button class="btn btn-primary btn-lg" id="btn-run-live-prediction">Generate Live Prediction</button>
      </div>

      <!-- Output Display Box -->
      <div id="ml-prediction-output" style="margin-top: 20px;"></div>
    </div>
  `;

  document.getElementById("btn-run-live-prediction")?.addEventListener("click", executeLivePrediction);
}

async function executeLivePrediction() {
  const outputBox = document.getElementById("ml-prediction-output");
  const modelName = document.getElementById("ml-inference-model")?.value;
  if (!outputBox) return;

  const inputs = {};
  document.querySelectorAll(".ml-pred-input").forEach(el => {
    const feat = el.getAttribute("data-feature");
    inputs[feat] = el.type === "range" ? parseFloat(el.value) : el.value;
  });

  outputBox.innerHTML = `<div style="text-align: center; padding: 20px;"><div class="spinner"></div></div>`;

  try {
    const res = await DataPilotAPI.predictML(state.activeDatasetId, inputs, modelName);

    outputBox.innerHTML = `
      <div style="background: #F8FAFC; border: 1.5px solid var(--border-color); border-radius: var(--radius-md); padding: 20px;">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
          <span style="font-size: 12.5px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.5px; color: var(--text-secondary);">
            Model Inference Result
          </span>
          <span class="badge badge-lavender">Model: ${res.model_used}</span>
        </div>

        <div style="display: flex; align-items: baseline; gap: 12px; margin-bottom: 16px;">
          <span style="font-size: 34px; font-weight: 800; color: var(--text-primary); letter-spacing: -0.5px;">
            ${res.prediction}
          </span>
          <span style="font-size: 14.5px; color: var(--text-secondary); font-weight: 500;">
            (Predicted Target: ${state.mlState.targetCol})
          </span>
        </div>

        ${res.probabilities ? `
          <div style="margin-top: 14px; border-top: 1px solid var(--border-color-light); padding-top: 14px;">
            <label style="font-size: 13px; font-weight: 700; color: var(--text-secondary); margin-bottom: 10px; display: block;">
              Class Probability Distribution:
            </label>
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 12px;">
              ${Object.entries(res.probabilities).map(([cls, prob]) => `
                <div class="prob-item">
                  <div class="prob-header">
                    <span>${cls}</span>
                    <span>${prob}%</span>
                  </div>
                  <div class="prob-bar-track">
                    <div class="prob-bar-fill" style="width: ${prob}%;"></div>
                  </div>
                </div>
              `).join('')}
            </div>
          </div>
        ` : ''}
      </div>
    `;

  } catch (err) {
    outputBox.innerHTML = `<div class="alert alert-danger">${err.message}</div>`;
  }
}

/* ==========================================================================
   PAGE 9: REPORTS & EXPORTS
   ========================================================================== */
function renderReportsPage(container) {
  const ds = state.activeDataset;

  container.innerHTML = `
    <div class="card">
      <div class="card-header">
        <div>
          <h2 class="card-title">Automated Analytical Reports &amp; Exports</h2>
          <p class="card-subtitle">Export reproducible academic PDF dossiers, multi-tab Excel workbooks, and cleaned CSV datasets</p>
        </div>
        <span class="badge badge-lime">Academic Dossier Ready</span>
      </div>

      <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(320px, 1fr)); gap: 20px; margin-top: 10px;">
        <!-- Cleaned CSV Card -->
        <div class="card" style="box-shadow: none; border-color: var(--border-color-light); margin-bottom: 0;">
          <div style="font-size: 28px; margin-bottom: 10px;">📄</div>
          <h3 style="font-size: 17px; font-weight: 700; color: var(--text-primary); margin-bottom: 6px;">Cleaned Dataset (CSV)</h3>
          <p style="font-size: 13.5px; color: var(--text-secondary); line-height: 1.45; margin-bottom: 18px;">
            Standard UTF-8 comma-separated file with all cleaning steps, imputed nulls, and deduplicated records applied.
          </p>
          <a class="btn btn-secondary" href="${DataPilotAPI.getCSVReportUrl(ds.id)}" target="_blank" download>
            📥 Download Cleaned CSV
          </a>
        </div>

        <!-- Excel Multi-Tab Dossier Card -->
        <div class="card" style="box-shadow: none; border-color: var(--border-color-light); margin-bottom: 0;">
          <div style="font-size: 28px; margin-bottom: 10px;">📊</div>
          <h3 style="font-size: 17px; font-weight: 700; color: var(--text-primary); margin-bottom: 6px;">Multi-Tab Excel Workbook (.xlsx)</h3>
          <p style="font-size: 13.5px; color: var(--text-secondary); line-height: 1.45; margin-bottom: 18px;">
            Formatted OpenPyXL workbook containing 5 dedicated tabs: Cleaned Data, Column Dictionary, Audit Trail, Numerical Profiling, and ML Leaderboard.
          </p>
          <a class="btn btn-secondary" href="${DataPilotAPI.getExcelReportUrl(ds.id)}" target="_blank" download>
            📥 Download Excel Dossier (.xlsx)
          </a>
        </div>

        <!-- Academic PDF Dossier Card -->
        <div class="card" style="box-shadow: none; border-color: var(--border-color-light); margin-bottom: 0;">
          <div style="font-size: 28px; margin-bottom: 10px;">📑</div>
          <h3 style="font-size: 17px; font-weight: 700; color: var(--text-primary); margin-bottom: 6px;">Academic PDF Dossier (.pdf)</h3>
          <p style="font-size: 13.5px; color: var(--text-secondary); line-height: 1.45; margin-bottom: 18px;">
            Dynamically compiled via ReportLab with formal project metadata, executive summary, cleaning audit logs, statistical methodologies, and model benchmarks.
          </p>
          <a class="btn btn-primary" href="${DataPilotAPI.getPDFReportUrl(ds.id)}" target="_blank" download>
            📥 Download Academic PDF Report
          </a>
        </div>
      </div>
    </div>
  `;
}

/* ==========================================================================
   PAGE 10: SETTINGS & THEME
   ========================================================================== */
async function renderSettingsPage(container) {
  container.innerHTML = `<div class="card" style="text-align: center; padding: 40px;"><div class="spinner"></div></div>`;

  try {
    const settings = await DataPilotAPI.getSettings();
    const t = settings.theme;

    container.innerHTML = `
      <!-- Design System Specifications Card -->
      <div class="card">
        <div class="card-header">
          <div>
            <h2 class="card-title">🎨 UI Design System &amp; Reference Palette</h2>
            <p class="card-subtitle">Active theme: <strong>${t.name}</strong> (Strictly locked to UI reference specifications)</p>
          </div>
          <span class="badge badge-lime">Palette Locked</span>
        </div>

        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 14px; margin-top: 14px;">
          <div style="border: 1px solid var(--border-color); border-radius: var(--radius-md); padding: 12px; background: #FFFFFF;">
            <div style="height: 36px; background: ${t.sidebar_bg}; border-radius: 4px; margin-bottom: 8px;"></div>
            <div style="font-size: 13px; font-weight: 700;">Sidebar</div>
            <code style="font-size: 12px; color: var(--text-secondary);">${t.sidebar_bg}</code>
          </div>

          <div style="border: 1px solid var(--border-color); border-radius: var(--radius-md); padding: 12px; background: #FFFFFF;">
            <div style="height: 36px; background: ${t.workspace_bg}; border-radius: 4px; margin-bottom: 8px; border: 1px solid #CCC;"></div>
            <div style="font-size: 13px; font-weight: 700;">Workspace</div>
            <code style="font-size: 12px; color: var(--text-secondary);">${t.workspace_bg}</code>
          </div>

          <div style="border: 1px solid var(--border-color); border-radius: var(--radius-md); padding: 12px; background: #FFFFFF;">
            <div style="height: 36px; background: ${t.primary_accent}; border-radius: 4px; margin-bottom: 8px;"></div>
            <div style="font-size: 13px; font-weight: 700;">Primary Accent (Lime)</div>
            <code style="font-size: 12px; color: var(--text-secondary);">${t.primary_accent}</code>
          </div>

          <div style="border: 1px solid var(--border-color); border-radius: var(--radius-md); padding: 12px; background: #FFFFFF;">
            <div style="height: 36px; background: ${t.secondary_accent}; border-radius: 4px; margin-bottom: 8px;"></div>
            <div style="font-size: 13px; font-weight: 700;">Secondary Accent (Lavender)</div>
            <code style="font-size: 12px; color: var(--text-secondary);">${t.secondary_accent}</code>
          </div>

          <div style="border: 1px solid var(--border-color); border-radius: var(--radius-md); padding: 12px; background: #FFFFFF;">
            <div style="height: 36px; background: ${t.primary_text}; border-radius: 4px; margin-bottom: 8px;"></div>
            <div style="font-size: 13px; font-weight: 700;">Primary Text</div>
            <code style="font-size: 12px; color: var(--text-secondary);">${t.primary_text}</code>
          </div>

          <div style="border: 1px solid var(--border-color); border-radius: var(--radius-md); padding: 12px; background: #FFFFFF;">
            <div style="height: 36px; background: ${t.border_color}; border-radius: 4px; margin-bottom: 8px;"></div>
            <div style="font-size: 13px; font-weight: 700;">Borders</div>
            <code style="font-size: 12px; color: var(--text-secondary);">${t.border_color}</code>
          </div>
        </div>
      </div>

      <!-- LLM Integration & Offline Safety -->
      <div class="card">
        <div class="card-header">
          <div>
            <h3 class="card-title">🤖 AI Data Analyst Configuration</h3>
            <p class="card-subtitle">Active Operating Mode: <strong>${settings.llm_providers.active_mode}</strong></p>
          </div>
        </div>

        <div style="font-size: 14px; line-height: 1.6; color: var(--text-secondary);">
          <p style="margin-bottom: 12px;">
            DataPilot AI runs <strong>100% offline</strong> using deterministic Python/Pandas mathematical computation. No sensitive data is transmitted externally.
          </p>
          <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 12px; margin-top: 14px;">
            <div style="background: #F8F9FA; padding: 12px; border-radius: 6px; border: 1px solid var(--border-color);">
              <div style="font-weight: 600; color: var(--text-primary);">Google Gemini API</div>
              <div style="font-size: 12.5px; color: ${settings.llm_providers.gemini_configured ? 'var(--success)' : 'var(--text-muted)'}; margin-top: 4px;">
                ${settings.llm_providers.gemini_configured ? '● Configured in .env' : '○ Not configured (Offline fallback active)'}
              </div>
            </div>
            <div style="background: #F8F9FA; padding: 12px; border-radius: 6px; border: 1px solid var(--border-color);">
              <div style="font-weight: 600; color: var(--text-primary);">Groq Cloud API</div>
              <div style="font-size: 12.5px; color: ${settings.llm_providers.groq_configured ? 'var(--success)' : 'var(--text-muted)'}; margin-top: 4px;">
                ${settings.llm_providers.groq_configured ? '● Configured in .env' : '○ Not configured (Offline fallback active)'}
              </div>
            </div>
            <div style="background: #F8F9FA; padding: 12px; border-radius: 6px; border: 1px solid var(--border-color);">
              <div style="font-weight: 600; color: var(--text-primary);">OpenAI API</div>
              <div style="font-size: 12.5px; color: ${settings.llm_providers.openai_configured ? 'var(--success)' : 'var(--text-muted)'}; margin-top: 4px;">
                ${settings.llm_providers.openai_configured ? '● Configured in .env' : '○ Not configured (Offline fallback active)'}
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- System Environment Card -->
      <div class="card">
        <div class="card-header">
          <h3 class="card-title">🖥️ Workspace Runtime Environment</h3>
          <span class="badge badge-gray">Version ${settings.version}</span>
        </div>
        <div style="font-size: 14px; color: var(--text-secondary); display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 12px;">
          <div><strong>Backend Engine:</strong> FastAPI + Uvicorn</div>
          <div><strong>SQL Engine:</strong> DuckDB (In-Memory Sandbox)</div>
          <div><strong>Visualizations:</strong> Plotly.js + Plotly Python</div>
          <div><strong>ML Framework:</strong> Scikit-Learn Pipelines</div>
          <div><strong>Active Datasets:</strong> ${state.datasetsList.length} in memory</div>
          <div><strong>Frontend Architecture:</strong> HTML5 + Modern CSS + Modular JS</div>
        </div>
      </div>
    `;

  } catch (err) {
    container.innerHTML = `<div class="alert alert-danger">${err.message}</div>`;
  }
}

