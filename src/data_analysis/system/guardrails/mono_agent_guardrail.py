"""Guardrail for validating and executing mono-agent output."""


import json
import pickle
import warnings
from pathlib import Path
from typing import Any, Dict, List, Tuple
import pandas as pd
from crewai.tasks.task_output import TaskOutput
from pydantic import ValidationError

from data_analysis.system.utils.error_formatter import (
    format_json_error,
    format_pydantic_error,
    format_visualization_errors,
)
from data_analysis.crew.models import VisualizationsModel
from data_analysis.system.utils import (
    create_execution_env,
    increment_agent_attempts,
    get_agent_attempts,
    update_analysis_status,
    validate_python_syntax,
)
from data_analysis.system.utils.paths import (
    VISUALIZATION_RESULTS_PICKLE_FILE,
    VISUALIZATIONS_FILE,
    VISUALIZATION_IMAGES_DIR,
)


def mono_agent_guardrail(result: TaskOutput) -> Tuple[bool, Any]:
    """Validate mono-agent output, execute code, and save results.
    
    Similar to visualization_guardrail but for the mono-agent pipeline.
    Does not trigger confidentiality tester.
    
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
        attempts = get_agent_attempts("mono_agent")
        MAX_ATTEMPTS = 4
        
        if attempts >= MAX_ATTEMPTS:
            update_analysis_status("mono_agent", "error")
            print(f"❌ Mono Agent - Failed after {MAX_ATTEMPTS} attempts")
            return (False, format_json_error(e))
        
        increment_agent_attempts("mono_agent")
        attempts = get_agent_attempts("mono_agent")
        display_attempts = min(attempts, MAX_ATTEMPTS)
        print(f"❌ Mono Agent - Retry (attempt {display_attempts}/{MAX_ATTEMPTS})")
        return (False, format_json_error(e))

    # Validate against Pydantic model
    try:
        validated = VisualizationsModel.model_validate(data)
    except ValidationError as e:
        attempts = get_agent_attempts("mono_agent")
        MAX_ATTEMPTS = 4
        
        if attempts >= MAX_ATTEMPTS:
            update_analysis_status("mono_agent", "error")
            print(f"❌ Mono Agent - Failed after {MAX_ATTEMPTS} attempts")
            return (False, format_pydantic_error(e, "visualization"))
        
        increment_agent_attempts("mono_agent")
        attempts = get_agent_attempts("mono_agent")
        display_attempts = min(attempts, MAX_ATTEMPTS)
        print(f"❌ Mono Agent - Retry (attempt {display_attempts}/{MAX_ATTEMPTS})")
        return (False, format_pydantic_error(e, "visualization"))

    # Save validated output
    validated_dict = validated.model_dump()
    VISUALIZATIONS_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(VISUALIZATIONS_FILE, "w", encoding="utf-8") as f:
        json.dump(validated_dict, f, indent=2, ensure_ascii=False)

    # Suppress warnings during execution
    warnings.filterwarnings('ignore')

    # Setup execution environment
    pickle_output = VISUALIZATION_RESULTS_PICKLE_FILE
    pickle_output.parent.mkdir(parents=True, exist_ok=True)
    
    # Create directory for visualization images
    VISUALIZATION_IMAGES_DIR.mkdir(parents=True, exist_ok=True)
    
    exec_globals = create_execution_env()

    # Track failures for error reporting
    failed_items: List[Dict[str, Any]] = []

    # Initialize results structure
    results_dict = {
        "analyses": [],
        "summary": {
            "total_queries": 0,
            "successful_queries": 0,
            "failed_queries": 0,
            "total_visualizations": 0,
            "successful_visualizations": 0,
            "failed_visualizations": 0
        }
    }

    # Execute queries and visualizations
    for analysis in validated_dict['analyses']:
        analysis_id = analysis.get('id', '?')

        analysis_result = {
            "id": analysis_id,
            "title": analysis.get('title'),
            "context": analysis.get('context'),
            "tables": analysis.get('tables'),
            "sub_analyses": []
        }

        for sub_analysis in analysis.get('sub_analyses', []):
            results_dict["summary"]["total_queries"] += 1
            results_dict["summary"]["total_visualizations"] += 1

            sub_id = sub_analysis.get('id', '?')
            sub_title = sub_analysis.get('title', 'Untitled')

            sub_analysis_result = {
                "id": sub_id,
                "title": sub_title,
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
                "result_dtypes": None,
                "visualization_code": sub_analysis.get('visualization_code', []),
                "visualization_type": sub_analysis.get('visualization_type'),
                "justification": sub_analysis.get('justification'),
                "visualization_success": False,
                "visualization_error": None,
            }

            # Check for missing query code
            if 'code_lines' not in sub_analysis or not sub_analysis['code_lines']:
                error_msg = "Missing or empty 'code_lines' field"
                sub_analysis_result["query_error"] = error_msg
                analysis_result["sub_analyses"].append(sub_analysis_result)
                results_dict["summary"]["failed_queries"] += 1
                results_dict["summary"]["failed_visualizations"] += 1
                failed_items.append({
                    "analysis_id": analysis_id,
                    "sub_analysis_id": sub_id,
                    "title": sub_title,
                    "error_type": "query",
                    "error_msg": error_msg
                })
                continue

            # Execute query
            query_code = '\n'.join(sub_analysis['code_lines'])
            query_result = validate_python_syntax(query_code, exec_globals)

            if not query_result['success']:
                error_msg = query_result.get('error', 'Unknown error')
                sub_analysis_result["query_error"] = error_msg
                analysis_result["sub_analyses"].append(sub_analysis_result)
                results_dict["summary"]["failed_queries"] += 1
                results_dict["summary"]["failed_visualizations"] += 1
                failed_items.append({
                    "analysis_id": analysis_id,
                    "sub_analysis_id": sub_id,
                    "title": sub_title,
                    "error_type": "query",
                    "error_msg": error_msg
                })
                continue

            # Validate query result
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
                analysis_result["sub_analyses"].append(sub_analysis_result)
                results_dict["summary"]["failed_queries"] += 1
                results_dict["summary"]["failed_visualizations"] += 1
                failed_items.append({
                    "analysis_id": analysis_id,
                    "sub_analysis_id": sub_id,
                    "title": sub_title,
                    "error_type": "query",
                    "error_msg": error_msg
                })
                continue

            # Check for missing visualization code
            if 'visualization_code' not in sub_analysis or not sub_analysis['visualization_code']:
                error_msg = "Missing or empty 'visualization_code' field"
                sub_analysis_result["visualization_error"] = error_msg
                analysis_result["sub_analyses"].append(sub_analysis_result)
                results_dict["summary"]["failed_visualizations"] += 1
                failed_items.append({
                    "analysis_id": analysis_id,
                    "sub_analysis_id": sub_id,
                    "title": sub_title,
                    "error_type": "visualization",
                    "error_msg": error_msg
                })
                continue

            # Execute visualization
            viz_code = '\n'.join(sub_analysis['visualization_code'])
            viz_result = validate_python_syntax(viz_code, exec_globals)

            if not viz_result['success']:
                error_msg = viz_result.get('error', 'Unknown error')
                sub_analysis_result["visualization_error"] = error_msg
                analysis_result["sub_analyses"].append(sub_analysis_result)
                results_dict["summary"]["failed_visualizations"] += 1
                failed_items.append({
                    "analysis_id": analysis_id,
                    "sub_analysis_id": sub_id,
                    "title": sub_title,
                    "error_type": "visualization",
                    "error_msg": error_msg
                })
                continue

            # Validate visualization result
            result_plot = viz_result['exec_globals'].get('result_plot')

            if result_plot is None:
                error_msg = "Variable 'result_plot' not found after visualization code execution"
                sub_analysis_result["visualization_error"] = error_msg
                analysis_result["sub_analyses"].append(sub_analysis_result)
                results_dict["summary"]["failed_visualizations"] += 1
                failed_items.append({
                    "analysis_id": analysis_id,
                    "sub_analysis_id": sub_id,
                    "title": sub_title,
                    "error_type": "visualization",
                    "error_msg": error_msg
                })
                continue

            # Success - Convert matplotlib figure to PNG and save
            try:
                # Generate unique filename for this visualization
                image_filename = f"{analysis_id}_{sub_id}_viz.png"
                image_path = VISUALIZATION_IMAGES_DIR / image_filename
                
                # Save figure as PNG
                result_plot.savefig(image_path, dpi=150, bbox_inches='tight', facecolor='white')
                
                # Store relative path instead of the figure object
                sub_analysis_result["visualization_success"] = True
                sub_analysis_result["result_plot"] = None  # Remove figure object
                sub_analysis_result["visualization_image_path"] = str(image_path)
                results_dict["summary"]["successful_visualizations"] += 1
            except Exception as e:
                error_msg = f"Error saving visualization image: {e}"
                sub_analysis_result["visualization_error"] = error_msg
                analysis_result["sub_analyses"].append(sub_analysis_result)
                results_dict["summary"]["failed_visualizations"] += 1
                failed_items.append({
                    "analysis_id": analysis_id,
                    "sub_analysis_id": sub_id,
                    "title": sub_title,
                    "error_type": "visualization",
                    "error_msg": error_msg
                })
                continue

            analysis_result["sub_analyses"].append(sub_analysis_result)

        results_dict["analyses"].append(analysis_result)

    # Save results to pickle
    with open(pickle_output, 'wb') as f:
        pickle.dump(results_dict, f)

    # Check for success
    if not failed_items:
        update_analysis_status("mono_agent", "done")
        print("✅ Mono Agent")
        return (True, validated_dict)

    # Check if we've reached max attempts BEFORE incrementing
    attempts = get_agent_attempts("mono_agent")
    MAX_ATTEMPTS = 4
    
    if attempts >= MAX_ATTEMPTS:
        # Max attempts reached, mark as error (don't increment)
        update_analysis_status("mono_agent", "error")
        print(f"❌ Mono Agent - Failed after {MAX_ATTEMPTS} attempts")
        return (False, format_visualization_errors(failed_items))
    
    # Only increment if we haven't reached max yet
    increment_agent_attempts("mono_agent")
    attempts = get_agent_attempts("mono_agent")
    display_attempts = min(attempts, MAX_ATTEMPTS)
    print(f"❌ Mono Agent - Retry (attempt {display_attempts}/{MAX_ATTEMPTS})")
    return (False, format_visualization_errors(failed_items))
