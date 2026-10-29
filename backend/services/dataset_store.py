"""
DataPilot AI - Dataset Memory Store & State Manager
Safely stores user datasets, metadata, cleaning sessions, and ML pipelines.
Avoids global mutable contamination by isolating datasets by UUID identifiers.
"""

import time
import uuid
import threading
from typing import Dict, List, Any, Optional
import pandas as pd

from modules.data_loader import (
    load_dataset, load_sample_dataset, get_dataset_metadata,
    AVAILABLE_SAMPLES, get_excel_sheet_names
)
from modules.cleaning_engine import CleaningSession
from modules.dataset_explainer import generate_dataset_overview
from modules.sql_engine import SQLExecutionEngine


class DatasetEntry:
    def __init__(
        self,
        dataset_id: str,
        name: str,
        df: pd.DataFrame,
        file_type: str = "csv",
        sheet_name: Optional[str] = None,
        available_sheets: Optional[List[str]] = None
    ):
        self.id = dataset_id
        self.name = name
        self.file_type = file_type
        self.sheet_name = sheet_name
        self.available_sheets = available_sheets or []
        self.raw_df = df.copy()
        self.current_df = df.copy()
        self.cleaning_session = CleaningSession(df)
        self.sql_engine = SQLExecutionEngine()
        self.sql_engine.register_table(self.name, self.current_df)
        self.ml_pipeline = None
        self.created_at = time.time()
        self.last_accessed_at = time.time()
        self.user_context: str = ""
        self._overview_cache: Optional[Dict[str, Any]] = None

    def refresh_sql_engine(self):
        """Re-registers current_df with the DuckDB engine."""
        self.sql_engine.register_table(self.name, self.current_df)

    def touch(self):
        self.last_accessed_at = time.time()

    def get_metadata(self) -> Dict[str, Any]:
        self.touch()
        return get_dataset_metadata(self.current_df)

    def get_overview(self, user_context: Optional[str] = None) -> Dict[str, Any]:
        self.touch()
        if user_context is not None:
            self.user_context = user_context
            self._overview_cache = None

        if self._overview_cache is None:
            self._overview_cache = generate_dataset_overview(
                self.current_df,
                file_name=self.name,
                user_context=self.user_context
            )
        return self._overview_cache

    def to_summary_dict(self) -> Dict[str, Any]:
        meta = self.get_metadata()
        return {
            "id": self.id,
            "name": self.name,
            "file_type": self.file_type,
            "sheet_name": self.sheet_name,
            "available_sheets": self.available_sheets,
            "total_rows": meta.get("total_rows", 0),
            "total_cols": meta.get("total_cols", 0),
            "memory_str": meta.get("memory_str", "0 KB"),
            "health_score": meta.get("health_score", 100),
            "created_at": self.created_at
        }


class DatasetStore:
    """Thread-safe dataset registry with TTL and size limits."""
    
    def __init__(self, max_datasets: int = 30, ttl_seconds: int = 14400):
        self._store: Dict[str, DatasetEntry] = {}
        self._lock = threading.Lock()
        self._max_datasets = max_datasets
        self._ttl_seconds = ttl_seconds

    def _cleanup_expired(self):
        now = time.time()
        expired_ids = [
            d_id for d_id, entry in self._store.items()
            if now - entry.last_accessed_at > self._ttl_seconds
        ]
        for d_id in expired_ids:
            del self._store[d_id]

        if len(self._store) > self._max_datasets:
            # Evict least recently accessed
            sorted_entries = sorted(self._store.items(), key=lambda item: item[1].last_accessed_at)
            excess = len(self._store) - self._max_datasets
            for i in range(excess):
                del self._store[sorted_entries[i][0]]

    def create(
        self,
        name: str,
        df: pd.DataFrame,
        file_type: str = "csv",
        sheet_name: Optional[str] = None,
        available_sheets: Optional[List[str]] = None
    ) -> DatasetEntry:
        with self._lock:
            self._cleanup_expired()
            dataset_id = str(uuid.uuid4())
            entry = DatasetEntry(
                dataset_id=dataset_id,
                name=name,
                df=df,
                file_type=file_type,
                sheet_name=sheet_name,
                available_sheets=available_sheets
            )
            self._store[dataset_id] = entry
            return entry

    def get(self, dataset_id: str) -> Optional[DatasetEntry]:
        with self._lock:
            entry = self._store.get(dataset_id)
            if entry:
                entry.touch()
            return entry

    def delete(self, dataset_id: str) -> bool:
        with self._lock:
            if dataset_id in self._store:
                del self._store[dataset_id]
                return True
            return False

    def list_all(self) -> List[Dict[str, Any]]:
        with self._lock:
            return [entry.to_summary_dict() for entry in self._store.values()]

    def load_sample(self, sample_key: str, sheet_name: Optional[str] = None) -> Optional[DatasetEntry]:
        if sample_key not in AVAILABLE_SAMPLES:
            return None

        meta = AVAILABLE_SAMPLES[sample_key]
        df, err = load_sample_dataset(sample_key, sheet_name=sheet_name)
        if df is None:
            return None

        available_sheets = []
        if meta["type"] == "excel":
            from modules.data_loader import SAMPLE_DATA_DIR
            import os
            file_path = os.path.join(SAMPLE_DATA_DIR, meta["filename"])
            available_sheets = get_excel_sheet_names(file_path)

        return self.create(
            name=meta["name"],
            df=df,
            file_type=meta["type"],
            sheet_name=sheet_name or (available_sheets[0] if available_sheets else None),
            available_sheets=available_sheets
        )


# Global singleton dataset store
dataset_store = DatasetStore()

