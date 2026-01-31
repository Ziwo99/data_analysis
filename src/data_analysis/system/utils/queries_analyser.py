"""Query analysis utilities."""


from __future__ import annotations
import json
import pickle
from pathlib import Path
from typing import Any, Dict, List
import pandas as pd
from data_analysis.system.utils.paths import (
    OUTPUT_SCRIPT_DIR,
    QUERY_ANALYSIS_FILE,
    QUERY_RESULTS_PICKLE_FILE,
)


# ============================================================================
# DataFrame Statistical Analysis
# ============================================================================

def analyze_dataframe(df: pd.DataFrame) -> Dict[str, Any]:
    """Compute statistical summary of a pandas DataFrame.
    
    Args:
        df: The DataFrame to analyze.
    
    Returns:
        Dictionary containing row count, column count, and per-column statistics.
    """
    schema: Dict[str, Any] = {
        "row_count": int(len(df)),
        "column_count": int(len(df.columns)),
        "columns": {},
    }

    for column in df.columns:
        series = df[column]

        # Handle unhashable types (e.g., lists, dicts)
        try:
            unique_count = int(series.nunique(dropna=True))
        except TypeError:
            unique_count = None

        info = {
            "type": str(series.dtype),
            "nullable": bool(series.isnull().any()),
            "null_count": int(series.isnull().sum()),
            "unique_count": unique_count,
        }

        # Add numeric statistics
        if pd.api.types.is_numeric_dtype(series):
            info.update({
                "min": float(series.min()) if pd.notna(series.min()) else None,
                "max": float(series.max()) if pd.notna(series.max()) else None,
                "mean": float(series.mean()) if pd.notna(series.mean()) else None,
                "std": float(series.std()) if pd.notna(series.std()) else None,
            })

        # Add string statistics
        elif pd.api.types.is_string_dtype(series):
            non_null = series.dropna()
            info.update({
                "avg_length": float(non_null.str.len().mean()) if not non_null.empty else None,
                "max_length": int(non_null.str.len().max()) if not non_null.empty else None,
            })

        schema["columns"][column] = info

    return schema


# ============================================================================
# Query Results Analysis
# ============================================================================

def analyze_query_results() -> Dict[str, Any]:
    """Analyze executed query results from pickle file.
    
    Reads query_results.pkl and analyzes each DataFrame.
    
    Returns:
        Dictionary with analysis results for all queries.
    """
    if not QUERY_RESULTS_PICKLE_FILE.exists():
        return {"error": f"Pickle file not found: {QUERY_RESULTS_PICKLE_FILE}"}

    with QUERY_RESULTS_PICKLE_FILE.open("rb") as f:
        results_dict = pickle.load(f)

    analyses_output: List[Dict[str, Any]] = []

    for analysis in results_dict.get("analyses", []):
        analysis_entry = {
            "id": analysis.get("id"),
            "title": analysis.get("title"),
            "queries": [],
        }

        for sub_analysis in analysis.get("sub_analyses", []):
            query_entry = {
                "id": sub_analysis.get("id"),
                "title": sub_analysis.get("title"),
                "type": sub_analysis.get("type"),
            }

            result_dataframe = sub_analysis.get("result_dataframe")

            if result_dataframe is not None and isinstance(result_dataframe, pd.DataFrame):
                query_entry["analysis"] = analyze_dataframe(result_dataframe)
            elif sub_analysis.get("query_error"):
                query_entry["error"] = sub_analysis.get("query_error")
            else:
                query_entry["error"] = "No result DataFrame found"

            analysis_entry["queries"].append(query_entry)

        analyses_output.append(analysis_entry)

    return {"analyses": analyses_output}

def analyze_and_save_query_results() -> Path:
    """Analyze query results and save to JSON.
    
    Returns:
        Path to saved JSON file.
    """
    analysis_results = analyze_query_results()

    OUTPUT_SCRIPT_DIR.mkdir(parents=True, exist_ok=True)

    with open(QUERY_ANALYSIS_FILE, "w", encoding="utf-8") as f:
        json.dump(analysis_results, f, ensure_ascii=False, indent=2)

    return QUERY_ANALYSIS_FILE

def get_query_analysis_json() -> str:
    """Get query analysis as JSON string.
    
    Used by QueriesAnalyser for visualization agent.
    
    Returns:
        JSON string of query analysis.
    
    Raises:
        FileNotFoundError: If analysis file does not exist.
    """
    if not QUERY_ANALYSIS_FILE.exists():
        raise FileNotFoundError(
            f"Query analysis file not found: {QUERY_ANALYSIS_FILE}. "
            "Run analyze_and_save_query_results() first."
        )

    with open(QUERY_ANALYSIS_FILE, "r", encoding="utf-8") as f:
        return f.read()

