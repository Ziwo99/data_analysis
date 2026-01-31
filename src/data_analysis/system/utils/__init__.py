"""Utility functions for data analysis."""


from .code_execution import (
    create_execution_env,
    validate_python_syntax,
)
from .queries_analyser import (
    analyze_dataframe,
    analyze_and_save_query_results,
    analyze_query_results,
    get_query_analysis_json,
)
from .saved_analyses import (
    create_source_data_zip,
    delete_analysis,
    get_analysis_metadata,
    get_current_source_data_files,
    get_saved_analyses,
    get_saved_analysis_names,
    get_source_data_files,
    load_analysis,
    sanitize_folder_name,
    save_analysis,
    update_existing_analyses_with_model,
    validate_analysis_name,
)
from .metadata_extractor import (
    extract_and_save_schema_metadata,
    extract_csv_schema_metadata,
    get_raw_schema_metadata_json,
    load_raw_schema_metadata,
)
from .analysis_status import (
    DEFAULT_AGENTS_STATUS,
    MONO_DEFAULT_AGENTS_STATUS,
    get_agent_attempts,
    increment_agent_attempts,
    mark_following_agents_as_error,
    update_analysis_status,
)
from .upload_handler import (
    save_uploaded_files,
)


__all__ = [
    # DataFrame analysis
    "analyze_dataframe",
    "analyze_query_results",
    "analyze_and_save_query_results",
    "get_query_analysis_json",
    # Code execution
    "validate_python_syntax",
    "create_execution_env",
    # Analysis status
    "DEFAULT_AGENTS_STATUS",
    "MONO_DEFAULT_AGENTS_STATUS",
    "update_analysis_status",
    "increment_agent_attempts",
    "get_agent_attempts",
    "mark_following_agents_as_error",
    # Schema extraction
    "extract_csv_schema_metadata",
    "extract_and_save_schema_metadata",
    "load_raw_schema_metadata",
    "get_raw_schema_metadata_json",
    # Upload handling
    "save_uploaded_files",
    # Saved analyses
    "get_saved_analyses",
    "get_saved_analysis_names",
    "get_analysis_metadata",
    "validate_analysis_name",
    "sanitize_folder_name",
    "save_analysis",
    "load_analysis",
    "delete_analysis",
    "get_source_data_files",
    "get_current_source_data_files",
    "create_source_data_zip",
    "update_existing_analyses_with_model",
]
