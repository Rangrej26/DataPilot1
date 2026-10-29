"""
DataPilot AI - Machine Learning Lab & Predictive Modeling Engine
End-to-end reproducible modeling: task detection, leakage safeguards,
smart feature encoding, date extraction, scikit-learn ColumnTransformer pipelines,
multi-model benchmarking, confusion matrices, actual vs predicted plots,
feature importances, and interactive what-if live predictions.
"""

from typing import Dict, List, Tuple, Any, Optional
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, OneHotEncoder, LabelEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score, confusion_matrix,
    mean_absolute_error, mean_squared_error, r2_score
)
from sklearn.linear_model import LogisticRegression, LinearRegression, Ridge
from sklearn.tree import DecisionTreeClassifier, DecisionTreeRegressor
from sklearn.ensemble import (
    RandomForestClassifier, RandomForestRegressor,
    GradientBoostingClassifier, GradientBoostingRegressor
)
from modules.ui_components import get_theme_colors, get_plotly_theme


def auto_detect_ml_task(df: pd.DataFrame, target_col: str) -> Tuple[str, str]:
    """
    Infers whether target column is suited for Classification or Regression.
    Returns (task_type, details).
    """
    if target_col not in df.columns:
        return "Unknown", "Column does not exist in dataset."

    series = df[target_col].dropna()
    unique_cnt = series.nunique()
    
    if unique_cnt < 2:
        return "Invalid", "Target has fewer than 2 unique classes. Predictive modeling cannot be performed on constant values."

    # Categorical, boolean or string
    if not pd.api.types.is_numeric_dtype(series):
        if unique_cnt == 2:
            return "Classification", f"Binary Classification ({unique_cnt} distinct classes: {list(series.unique())})"
        elif unique_cnt <= 20:
            return "Classification", f"Multi-Class Classification ({unique_cnt} distinct classes)"
        else:
            return "Invalid", f"Target has {unique_cnt} unique text values. Categorical classification is not recommended for targets with >20 distinct classes (e.g. IDs or names). Please select a valid target."

    # Numeric targets
    if unique_cnt <= 10 and series.dtype in [int, "int64", "int32", bool]:
        return "Classification", f"Discrete Categorical Classification ({unique_cnt} integer classes: {sorted(list(series.unique()))})"
    else:
        return "Regression", f"Continuous Numeric Regression ({unique_cnt} unique values, range: {series.min():.2f} to {series.max():.2f})"


def get_available_models(task_type: str) -> List[str]:
    """Returns candidate baseline models supported for the specified task."""
    if task_type == "Classification":
        return ["Random Forest", "Gradient Boosting", "Logistic Regression", "Decision Tree"]
    return [
        "Random Forest Regressor",
        "Gradient Boosting Regressor",
        "Ridge Regression",
        "Linear Regression",
        "Decision Tree Regressor"
    ]


def check_target_leakage(df: pd.DataFrame, target_col: str, candidate_features: List[str]) -> List[Dict[str, Any]]:
    """
    Checks for potential data leakage (features with suspiciously high correlation >= 0.95 with target,
    or unique identifier columns that cause memorization).
    """
    warnings = []
    total_rows = len(df)
    if total_rows == 0 or target_col not in df.columns:
        return warnings

    # Convert target to numeric for correlation testing if possible
    target_series = df[target_col]
    if not pd.api.types.is_numeric_dtype(target_series):
        try:
            target_numeric = pd.Series(pd.factorize(target_series.astype(str))[0], index=df.index, dtype=float)
        except Exception:
            target_numeric = None
    else:
        target_numeric = target_series.astype(float)

    for col in candidate_features:
        if col == target_col or col not in df.columns:
            continue
        
        series = df[col]
        
        # 1. Check for identifier columns (ID / Code / UUID or 100% unique values)
        c_lower = col.lower()
        unique_cnt = series.nunique()
        if unique_cnt > 1 and unique_cnt >= int(total_rows * 0.95):
            warnings.append({
                "feature": col,
                "correlation": 1.0,
                "warning": f"Feature '{col}' appears to be a unique row identifier ({unique_cnt} distinct values for {total_rows} rows). Including IDs causes severe model overfitting / memorization."
            })
            continue
        elif any(k in c_lower for k in ["_id", "customer_id", "emp_id", "patient_id", "tracking_code", "uuid"]):
            warnings.append({
                "feature": col,
                "correlation": 1.0,
                "warning": f"Feature '{col}' has an identifier naming pattern. It is strongly recommended to exclude ID fields from training."
            })
            continue

        # 2. Check numerical correlation with target
        if target_numeric is not None and pd.api.types.is_numeric_dtype(series):
            try:
                corr = abs(float(series.corr(target_numeric)))
                if corr >= 0.95 and not np.isnan(corr):
                    warnings.append({
                        "feature": col,
                        "correlation": round(corr, 3),
                        "warning": f"Extreme correlation (r = {corr:.3f}) with target '{target_col}'. High probability of target leakage or duplicate feature."
                    })
            except Exception:
                pass

    return warnings


class MLTrainingPipeline:
    """
    Encapsulates preprocessing, train-test splitting, multi-model evaluation,
    and interactive inference.
    """
    def __init__(
        self,
        df: pd.DataFrame,
        target_col: str,
        feature_cols: List[str],
        task_type: str,
        test_size: float = 0.2,
        random_state: int = 42
    ):
        self.raw_df = df.copy()
        self.target_col = target_col
        # Ensure target is strictly excluded from feature inputs
        self.feature_cols = [c for c in feature_cols if c != target_col]
        self.task_type = task_type
        self.test_size = test_size
        self.random_state = random_state

        self.preprocessor = None
        self.label_encoder = None
        self.classes_ = []
        self.trained_models = {}
        self.model_errors = {}
        self.model_results = []
        self.best_model_name = None
        self.best_model = None
        self.X_train = None
        self.X_test = None
        self.y_train = None
        self.y_test = None
        self.transformed_feature_names = []
        self.datetime_features = []

    def _engineer_features(self, df_features: pd.DataFrame) -> Tuple[pd.DataFrame, List[str], List[str]]:
        """
        Engineers features: decomposes datetime and date-string features into numeric components,
        caps high-cardinality categorical features, and separates numeric and categorical features.
        """
        df_out = df_features.copy()
        self.datetime_features = []

        for col in df_features.columns:
            # Check already datetime64
            if pd.api.types.is_datetime64_any_dtype(df_features[col]):
                self.datetime_features.append(col)
                df_out[f"{col}_year"] = df_features[col].dt.year
                df_out[f"{col}_month"] = df_features[col].dt.month
                df_out[f"{col}_day"] = df_features[col].dt.day
                df_out[f"{col}_dayofweek"] = df_features[col].dt.dayofweek
                df_out.drop(columns=[col], inplace=True)
            elif any(k in col.lower() for k in ["date", "time", "timestamp"]) and not pd.api.types.is_numeric_dtype(df_features[col]):
                # Attempt date conversion for string dates
                try:
                    parsed_dt = pd.to_datetime(df_features[col], errors="coerce")
                    if parsed_dt.notnull().sum() >= max(5, int(len(df_features) * 0.5)):
                        self.datetime_features.append(col)
                        df_out[f"{col}_year"] = parsed_dt.dt.year.fillna(2024).astype(int)
                        df_out[f"{col}_month"] = parsed_dt.dt.month.fillna(1).astype(int)
                        df_out[f"{col}_day"] = parsed_dt.dt.day.fillna(1).astype(int)
                        df_out[f"{col}_dayofweek"] = parsed_dt.dt.dayofweek.fillna(0).astype(int)
                        df_out.drop(columns=[col], inplace=True)
                except Exception:
                    pass

        # Handle high cardinality in remaining categorical features
        cat_candidates = list(df_out.select_dtypes(include=["object", "category", "string", "bool"]).columns)
        for col in cat_candidates:
            if df_out[col].nunique() > 25:
                top_25 = df_out[col].value_counts().nlargest(25).index.tolist()
                df_out[col] = df_out[col].apply(lambda x: x if pd.isnull(x) or x in top_25 else "Other")

        num_features = list(df_out.select_dtypes(include=["number"]).columns)
        cat_features = list(df_out.select_dtypes(include=["object", "category", "string", "bool"]).columns)

        return df_out, num_features, cat_features

    def prepare_data(self) -> Tuple[bool, Optional[str]]:
        """
        Validates features, prepares X and y, and fits reproducible ColumnTransformer pipeline.
        """
        try:
            if not self.feature_cols:
                return False, "No valid feature columns selected for model training."

            # Drop rows where target is null
            clean_data = self.raw_df.dropna(subset=[self.target_col]).copy()
            if len(clean_data) < 20:
                return False, f"Dataset has only {len(clean_data)} valid rows after dropping target nulls. Minimum 20 rows are required for train/test splitting and model evaluation."

            # Target validation
            if self.task_type == "Regression":
                if not pd.api.types.is_numeric_dtype(clean_data[self.target_col]):
                    return False, f"Target column '{self.target_col}' contains non-numeric text data. Regression models require a continuous numeric target. Please select 'Classification' or choose a numeric target column."
                y_raw = clean_data[self.target_col].astype(float)
            else:  # Classification
                if pd.api.types.is_float_dtype(clean_data[self.target_col]) and clean_data[self.target_col].nunique() > 25:
                    return False, f"Target column '{self.target_col}' contains {clean_data[self.target_col].nunique()} continuous float values. Classification requires discrete classes. Please select 'Regression' instead."
                
                # Fit LabelEncoder for consistent internal integer classes
                self.label_encoder = LabelEncoder()
                y_raw = pd.Series(self.label_encoder.fit_transform(clean_data[self.target_col].astype(str)), index=clean_data.index)
                self.classes_ = list(self.label_encoder.classes_)
                
                if len(self.classes_) < 2:
                    return False, f"Target column '{self.target_col}' has only 1 class in valid rows. At least 2 classes are required."

            X_raw = clean_data[self.feature_cols]

            # Engineer features (datetime decomposition)
            X_engineered, num_features, cat_features = self._engineer_features(X_raw)

            if not num_features and not cat_features:
                return False, "Selected features do not contain any numeric, categorical, or datetime columns suitable for training."

            # Build transformers
            transformers = []
            if num_features:
                num_pipe = Pipeline([
                    ("imputer", SimpleImputer(strategy="median")),
                    ("scaler", StandardScaler())
                ])
                transformers.append(("num", num_pipe, num_features))

            if cat_features:
                cat_pipe = Pipeline([
                    ("imputer", SimpleImputer(strategy="most_frequent")),
                    ("encoder", OneHotEncoder(handle_unknown="ignore", sparse_output=False))
                ])
                transformers.append(("cat", cat_pipe, cat_features))

            self.preprocessor = ColumnTransformer(transformers=transformers, remainder="drop")

            # Split Train / Test
            stratify = None
            if self.task_type == "Classification":
                counts = y_raw.value_counts()
                # Scikit-learn requires at least 2 samples per class in test split for stratification
                # With test_size=0.2, min class count should be at least 5 for safe stratification
                if counts.min() >= 5 and len(counts) > 1:
                    stratify = y_raw

            self.X_train_raw, self.X_test_raw, self.y_train, self.y_test = train_test_split(
                X_engineered, y_raw, test_size=self.test_size, random_state=self.random_state, stratify=stratify
            )

            # Fit strictly on train data to prevent information leakage
            self.X_train = self.preprocessor.fit_transform(self.X_train_raw)
            self.X_test = self.preprocessor.transform(self.X_test_raw)

            # Extract transformed feature names for importance mapping
            names = []
            if num_features:
                names.extend(num_features)
            if cat_features:
                cat_encoder = self.preprocessor.named_transformers_["cat"].named_steps["encoder"]
                encoded_names = list(cat_encoder.get_feature_names_out(cat_features))
                names.extend(encoded_names)
            self.transformed_feature_names = names

            return True, None
        except Exception as e:
            return False, f"Data preparation error: {str(e)}"

    def train_and_compare(self, selected_models: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """
        Trains baseline models and compares their out-of-sample test metrics.
        Optionally trains only a specified subset of models.
        """
        self.model_results = []
        self.trained_models = {}
        self.model_errors = {}

        if self.task_type == "Classification":
            all_models = {
                "Random Forest": RandomForestClassifier(n_estimators=100, max_depth=8, random_state=self.random_state),
                "Gradient Boosting": GradientBoostingClassifier(n_estimators=80, random_state=self.random_state),
                "Logistic Regression": LogisticRegression(max_iter=1000, random_state=self.random_state),
                "Decision Tree": DecisionTreeClassifier(max_depth=6, random_state=self.random_state)
            }
            models = {k: v for k, v in all_models.items() if not selected_models or k in selected_models}
            if not models:
                models = all_models

            for name, model in models.items():
                try:
                    model.fit(self.X_train, self.y_train)
                    y_pred = model.predict(self.X_test)

                    acc = round(accuracy_score(self.y_test, y_pred), 3)
                    prec = round(precision_score(self.y_test, y_pred, average="weighted", zero_division=0), 3)
                    rec = round(recall_score(self.y_test, y_pred, average="weighted", zero_division=0), 3)
                    f1 = round(f1_score(self.y_test, y_pred, average="weighted", zero_division=0), 3)

                    self.trained_models[name] = model
                    self.model_results.append({
                        "Model": name,
                        "Accuracy": acc,
                        "Precision (Weighted)": prec,
                        "Recall (Weighted)": rec,
                        "F1-Score": f1
                    })
                except Exception as e:
                    self.model_errors[name] = str(e)

            # Sort by F1-Score descending
            self.model_results.sort(key=lambda x: x["F1-Score"], reverse=True)

        else:  # Regression
            all_models = {
                "Random Forest Regressor": RandomForestRegressor(n_estimators=100, max_depth=8, random_state=self.random_state),
                "Gradient Boosting Regressor": GradientBoostingRegressor(n_estimators=80, random_state=self.random_state),
                "Ridge Regression": Ridge(alpha=1.0),
                "Linear Regression": LinearRegression(),
                "Decision Tree Regressor": DecisionTreeRegressor(max_depth=6, random_state=self.random_state)
            }
            models = {k: v for k, v in all_models.items() if not selected_models or k in selected_models}
            if not models:
                models = all_models

            for name, model in models.items():
                try:
                    model.fit(self.X_train, self.y_train)
                    y_pred = model.predict(self.X_test)

                    mae = round(mean_absolute_error(self.y_test, y_pred), 2)
                    mse = round(mean_squared_error(self.y_test, y_pred), 2)
                    rmse = round(float(np.sqrt(mse)), 2)
                    r2 = round(r2_score(self.y_test, y_pred), 3)

                    self.trained_models[name] = model
                    self.model_results.append({
                        "Model": name,
                        "R² Score": r2,
                        "MAE": mae,
                        "RMSE": rmse,
                        "MSE": mse
                    })
                except Exception as e:
                    self.model_errors[name] = str(e)

            # Sort by R2 Score descending
            self.model_results.sort(key=lambda x: x["R² Score"], reverse=True)

        if self.model_results:
            self.best_model_name = self.model_results[0]["Model"]
            self.best_model = self.trained_models[self.best_model_name]

        return self.model_results

    def get_confusion_matrix_plot(self, model_name: Optional[str] = None, theme_name: str = "Professional Light") -> Optional[go.Figure]:
        """Plots an annotated Confusion Matrix heatmap for classification."""
        if self.task_type != "Classification":
            return None

        m_name = model_name or self.best_model_name
        if not m_name or m_name not in self.trained_models:
            return None

        model = self.trained_models[m_name]
        y_pred = model.predict(self.X_test)

        labels = np.unique(np.concatenate([self.y_test, y_pred]))
        cm = confusion_matrix(self.y_test, y_pred, labels=labels)

        # Map integer labels back to human-readable class names if encoder available
        if self.label_encoder is not None:
            display_labels = [str(self.label_encoder.classes_[i]) if i < len(self.label_encoder.classes_) else str(i) for i in labels]
        else:
            display_labels = [str(lbl) for lbl in labels]

        template = get_plotly_theme(theme_name)

        fig = go.Figure(data=go.Heatmap(
            z=cm,
            x=[f"Pred: {lbl}" for lbl in display_labels],
            y=[f"True: {lbl}" for lbl in display_labels],
            colorscale=[[0.0, "#FFFFFF"], [1.0, "#B9ADF5"]],
            text=cm,
            texttemplate="%{text}",
            textfont={"size": 14, "family": "Inter, sans-serif", "color": "#202124"},
            colorbar=dict(title="Count")
        ))

        fig.update_layout(
            title=f"Confusion Matrix: {m_name}",
            template=template,
            height=380,
            margin=dict(l=40, r=40, t=50, b=40)
        )
        return fig

    def get_regression_prediction_plot(self, model_name: Optional[str] = None, theme_name: str = "Professional Light") -> Optional[go.Figure]:
        """Plots Actual vs. Predicted values with 45-degree reference line."""
        if self.task_type != "Regression":
            return None

        m_name = model_name or self.best_model_name
        if not m_name or m_name not in self.trained_models:
            return None

        model = self.trained_models[m_name]
        y_pred = model.predict(self.X_test)

        plot_df = pd.DataFrame({
            "Actual": self.y_test,
            "Predicted": y_pred
        })

        template = get_plotly_theme(theme_name)
        colors = get_theme_colors(theme_name)

        fig = px.scatter(
            plot_df, x="Actual", y="Predicted",
            template=template,
            color_discrete_sequence=[colors[0]],
            title=f"Actual vs. Predicted ({m_name})"
        )

        min_val = min(plot_df["Actual"].min(), plot_df["Predicted"].min())
        max_val = max(plot_df["Actual"].max(), plot_df["Predicted"].max())

        # Perfect prediction line
        fig.add_shape(
            type="line", line=dict(dash="dash", color="#EF4444", width=2),
            x0=min_val, y0=min_val, x1=max_val, y1=max_val
        )

        fig.update_layout(height=380, margin=dict(l=40, r=40, t=50, b=40))
        return fig

    def get_feature_importance_plot(self, model_name: Optional[str] = None, theme_name: str = "Professional Light") -> Optional[go.Figure]:
        """Extracts and plots top 15 feature importances or coefficients."""
        m_name = model_name or self.best_model_name
        if not m_name or m_name not in self.trained_models:
            return None

        model = self.trained_models[m_name]
        importances = None

        if hasattr(model, "feature_importances_"):
            importances = model.feature_importances_
        elif hasattr(model, "coef_"):
            coef = model.coef_
            if coef.ndim > 1:
                importances = np.mean(np.abs(coef), axis=0)
            else:
                importances = np.abs(coef)

        if importances is None or len(importances) != len(self.transformed_feature_names):
            return None

        imp_df = pd.DataFrame({
            "Feature": self.transformed_feature_names,
            "Importance": importances
        }).sort_values("Importance", ascending=True).tail(15)

        template = get_plotly_theme(theme_name)

        fig = px.bar(
            imp_df, x="Importance", y="Feature",
            orientation="h",
            template=template,
            color="Importance",
            color_continuous_scale="Blues",
            title=f"Top Feature Importances ({m_name})"
        )
        fig.update_layout(height=420, margin=dict(l=40, r=40, t=50, b=40))
        return fig

    def predict_single_instance(self, input_dict: Dict[str, Any], model_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Executes real-time inference on user-provided feature values for what-if scenario testing.
        Applies identical preprocessing pipeline used during training.
        """
        m_name = model_name or self.best_model_name
        if not m_name or m_name not in self.trained_models:
            available = list(self.trained_models.keys())
            if available:
                m_name = available[0]
                model = self.trained_models[m_name]
            else:
                return {"error": "Trained model not available for inference."}
        else:
            model = self.trained_models[m_name]
        
        try:
            # Ensure all expected feature columns exist in input_dict
            aligned_dict = {}
            for col in self.feature_cols:
                if col in input_dict:
                    aligned_dict[col] = input_dict[col]
                else:
                    # Fallback to column median or mode from raw data
                    if pd.api.types.is_numeric_dtype(self.raw_df[col]):
                        aligned_dict[col] = self.raw_df[col].median()
                    else:
                        mode_s = self.raw_df[col].mode()
                        aligned_dict[col] = mode_s.iloc[0] if not mode_s.empty else "Unknown"

            # Build input DataFrame
            input_df = pd.DataFrame([aligned_dict])
            
            # Re-apply date decomposition if applicable
            for col in self.datetime_features:
                if col in input_df.columns:
                    val = pd.to_datetime(input_df[col], errors="coerce")
                    input_df[f"{col}_year"] = val.dt.year.fillna(2024).astype(int)
                    input_df[f"{col}_month"] = val.dt.month.fillna(1).astype(int)
                    input_df[f"{col}_day"] = val.dt.day.fillna(1).astype(int)
                    input_df[f"{col}_dayofweek"] = val.dt.dayofweek.fillna(0).astype(int)
                    input_df.drop(columns=[col], inplace=True)

            transformed = self.preprocessor.transform(input_df)
            raw_pred = model.predict(transformed)[0]

            if self.task_type == "Classification":
                if self.label_encoder is not None:
                    human_pred = str(self.label_encoder.inverse_transform([raw_pred])[0])
                else:
                    human_pred = str(raw_pred)

                result = {
                    "prediction": human_pred,
                    "model_used": m_name,
                    "task_type": self.task_type
                }

                if hasattr(model, "predict_proba"):
                    probs = model.predict_proba(transformed)[0]
                    if self.label_encoder is not None:
                        class_names = [str(c) for c in self.label_encoder.classes_]
                    else:
                        class_names = [str(c) for c in model.classes_]
                    prob_dict = {c: round(float(p) * 100, 1) for c, p in zip(class_names, probs)}
                    result["probabilities"] = prob_dict

                return result
            else:
                return {
                    "prediction": round(float(raw_pred), 2),
                    "model_used": m_name,
                    "task_type": self.task_type
                }
        except Exception as e:
            return {"error": f"Prediction failed: {str(e)}"}
