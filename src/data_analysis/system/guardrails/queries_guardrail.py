"""Guardrail for validating and executing query builder output."""


import json
import pickle
import warnings
from typing import Any, Dict, List, Tuple
import pandas as pd
from crewai.tasks.task_output import TaskOutput
from pydantic import ValidationError
from data_analysis.system.utils.error_formatter import (
    format_json_error,
    format_pydantic_error,
    format_query_errors,
)
from data_analysis.crew.models import QueriesModel
from data_analysis.system.utils import (
    analyze_and_save_query_results,
    create_execution_env,
    increment_agent_attempts,
    get_agent_attempts,
    update_analysis_status,
    validate_python_syntax,
    mark_following_agents_as_error,
)
from data_analysis.system.utils.paths import (
    QUERIES_FILE,
    OUTPUT_AGENT_DIR,
    OUTPUT_EXECUTE_CODE_DIR,
    QUERY_RESULTS_PICKLE_FILE,
)


def queries_guardrail(result: TaskOutput) -> Tuple[bool, Any]:
    """Validate query builder output, execute queries, and save results.
    
    Args:
        result: The task output from CrewAI.
    
    Returns:
        Tuple of (success, validated_data or error_message).
    """
    output_text = result.raw

    # Parse JSON
    try:
        data = json.loads(output_text)
    except json.JSONDecodeError as e:
        attempts = get_agent_attempts("query_builder")
        MAX_ATTEMPTS = 4
        
        if attempts >= MAX_ATTEMPTS:
            update_analysis_status("query_builder", "error")
            mark_following_agents_as_error("query_builder", mono_mode=False)
            print(f"❌ Query Builder - Failed after {MAX_ATTEMPTS} attempts")
            return (False, format_json_error(e))
        
        increment_agent_attempts("query_builder")
        attempts = get_agent_attempts("query_builder")
        display_attempts = min(attempts, MAX_ATTEMPTS)
        print(f"❌ Query Builder - Retry (attempt {display_attempts}/{MAX_ATTEMPTS})")
        return (False, format_json_error(e))

    # Validate against Pydantic model
    try:
        validated = QueriesModel.model_validate(data)
    except ValidationError as e:
        attempts = get_agent_attempts("query_builder")
        MAX_ATTEMPTS = 4
        
        if attempts >= MAX_ATTEMPTS:
            update_analysis_status("query_builder", "error")
            mark_following_agents_as_error("query_builder", mono_mode=False)
            print(f"❌ Query Builder - Failed after {MAX_ATTEMPTS} attempts")
            return (False, format_pydantic_error(e, "query"))
        
        increment_agent_attempts("query_builder")
        attempts = get_agent_attempts("query_builder")
        display_attempts = min(attempts, MAX_ATTEMPTS)
        print(f"❌ Query Builder - Retry (attempt {display_attempts}/{MAX_ATTEMPTS})")
        return (False, format_pydantic_error(e, "query"))

    # Save validated output
    validated_dict = validated.model_dump()
    QUERIES_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(QUERIES_FILE, "w", encoding="utf-8") as f:
        json.dump(validated_dict, f, indent=2, ensure_ascii=False)

    # Suppress warnings during execution
    warnings.filterwarnings('ignore')

    # Setup execution environment
    OUTPUT_EXECUTE_CODE_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_AGENT_DIR.mkdir(parents=True, exist_ok=True)
    exec_globals = create_execution_env()

    # Track failures for error reporting
    failed_queries: List[Dict[str, Any]] = []

    # Initialize results structure
    results_dict = {
        "analyses": [],
        "summary": {
            "total_queries": 0,
            "successful_queries": 0,
            "failed_queries": 0
        }
    }

    # Execute queries for each sub-analysis
    for analysis in data['analyses']:
        analysis_id = analysis.get('id', '?')

        analysis_result = {
            "id": analysis.get('id'),
            "title": analysis.get('title'),
            "context": analysis.get('context'),
            "tables": analysis.get('tables'),
            "sub_analyses": []
        }

        for sub_analysis in analysis['sub_analyses']:
            results_dict["summary"]["total_queries"] += 1
            sub_id = sub_analysis.get('id', '?')
            sub_title = sub_analysis.get('title', 'Untitled')

            sub_analysis_result = {
                "id": sub_analysis.get('id'),
                "title": sub_analysis.get('title'),
                "why": sub_analysis.get('why'),
                "answers": sub_analysis.get('answers', []),
                "tables_columns": sub_analysis.get('tables_columns', []),
                "type": sub_analysis.get('type'),
                "code_lines": sub_analysis.get('code_lines', []),
                "query_success": False,
                "query_error": None,
                "result_dataframe": None,
                "result_shape": None,
                "result_columns": None,
                "result_dtypes": None
            }

            # Check for missing code
            if 'code_lines' not in sub_analysis or not sub_analysis['code_lines']:
                error_msg = "Missing or empty 'code_lines' field"
                sub_analysis_result["query_error"] = error_msg
                analysis_result["sub_analyses"].append(sub_analysis_result)
                results_dict["summary"]["failed_queries"] += 1
                failed_queries.append({
                    "analysis_id": analysis_id,
                    "sub_analysis_id": sub_id,
                    "title": sub_title,
                    "error_type": "missing_code",
                    "error_msg": error_msg
                })
                continue

            # Execute query code
            query_code = '\n'.join(sub_analysis['code_lines'])
            query_result = validate_python_syntax(query_code, exec_globals)

            if not query_result['success']:
                error_msg = query_result.get('error', 'Unknown error')
                sub_analysis_result["query_error"] = error_msg
                analysis_result["sub_analyses"].append(sub_analysis_result)
                results_dict["summary"]["failed_queries"] += 1
                failed_queries.append({
                    "analysis_id": analysis_id,
                    "sub_analysis_id": sub_id,
                    "title": sub_title,
                    "error_type": "execution_error",
                    "error_msg": error_msg
                })
                continue

            # Validate result is a DataFrame
            query_output = query_result['exec_globals'].get('result')

            if query_output is not None and isinstance(query_output, pd.DataFrame):
                sub_analysis_result["query_success"] = True
                sub_analysis_result["result_dataframe"] = query_output
                sub_analysis_result["result_shape"] = query_output.shape
                sub_analysis_result["result_columns"] = query_output.columns.tolist()
                sub_analysis_result["result_dtypes"] = query_output.dtypes.astype(str).to_dict()
                results_dict["summary"]["successful_queries"] += 1
            else:
                error_msg = "Result is not a DataFrame (variable 'result' missing or invalid)"
                sub_analysis_result["query_error"] = error_msg
                results_dict["summary"]["failed_queries"] += 1
                failed_queries.append({
                    "analysis_id": analysis_id,
                    "sub_analysis_id": sub_id,
                    "title": sub_title,
                    "error_type": "not_dataframe",
                    "error_msg": error_msg
                })
                continue

            analysis_result["sub_analyses"].append(sub_analysis_result)

        results_dict["analyses"].append(analysis_result)

    # Save results to pickle
    with open(QUERY_RESULTS_PICKLE_FILE, 'wb') as f:
        pickle.dump(results_dict, f)

    # Check for success
    if not failed_queries:
        update_analysis_status("query_builder", "done")
        print("✅ Query Builder")
        update_analysis_status("query_analysis", "in_progress")
        analyze_and_save_query_results()
        update_analysis_status("query_analysis", "done")
        print("✅ Query Analysis")
        update_analysis_status("visualization_designer", "in_progress")
        return (True, validated_dict)

    # Check if we've reached max attempts BEFORE incrementing
    attempts = get_agent_attempts("query_builder")
    MAX_ATTEMPTS = 4
    
    if attempts >= MAX_ATTEMPTS:
        # Max attempts reached, mark as error (don't increment)
        update_analysis_status("query_builder", "error")
        mark_following_agents_as_error("query_builder", mono_mode=False)
        print(f"❌ Query Builder - Failed after {MAX_ATTEMPTS} attempts")
        return (False, format_query_errors(failed_queries))
    
    # Only increment if we haven't reached max yet
    increment_agent_attempts("query_builder")
    attempts = get_agent_attempts("query_builder")
    display_attempts = min(attempts, MAX_ATTEMPTS)
    print(f"❌ Query Builder - Retry (attempt {display_attempts}/{MAX_ATTEMPTS})")
    return (False, format_query_errors(failed_queries))
