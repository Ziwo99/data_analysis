"""Utility functions for formatting guardrail error messages."""


import json
from typing import Any, Dict, List
from pydantic import ValidationError


def format_json_error(error: json.JSONDecodeError) -> str:
    """Format a JSON parsing error into a clear message.
    
    Args:
        error: The JSON decode error.
    
    Returns:
        Formatted error message.
    """
    return f"""❌ JSON ERROR

Problem: Malformed JSON at line {error.lineno}, column {error.colno}.
Detail: {error.msg}

Fix: Check JSON syntax (commas, quotes, braces)."""


def format_pydantic_error(error: ValidationError, context: str = "") -> str:
    """Format a Pydantic validation error into a clear message.
    
    Args:
        error: The Pydantic ValidationError.
        context: Optional context (e.g., "enriched_metadata", "business_analysis").
    
    Returns:
        Formatted error message with field details.
    """
    errors = error.errors()
    
    if not errors:
        return "❌ Unknown validation error"
    
    error_messages = []
    
    # Limit to 5 errors for readability
    for err in errors[:5]:
        location = " → ".join(str(loc) for loc in err.get("loc", []))
        error_type = err.get("type", "unknown")
        msg = err.get("msg", "")
        
        type_descriptions = {
            "missing": "missing field",
            "string_type": "must be a string",
            "int_type": "must be an integer",
            "list_type": "must be a list",
            "dict_type": "must be an object",
            "value_error": "invalid value",
            "type_error": "invalid type",
        }
        
        readable_type = type_descriptions.get(error_type, error_type)
        error_messages.append(f"  • {location}: {readable_type}")
        if msg and msg != readable_type:
            error_messages.append(f"    → {msg}")
    
    total_errors = len(errors)
    
    result = f"""❌ VALIDATION ERROR ({total_errors} issue{'s' if total_errors > 1 else ''})

Incorrect fields:
{chr(10).join(error_messages)}"""
    
    if total_errors > 5:
        result += f"\n  ... and {total_errors - 5} more errors"
    
    result += "\n\nFix: Check that all required fields are present with correct types."
    
    return result


def format_query_errors(failed_queries: List[Dict[str, Any]]) -> str:
    """Format query execution errors into a clear message.
    
    Args:
        failed_queries: List of failed query info dicts with keys:
            analysis_id, sub_analysis_id, title, error_type, error_msg
    
    Returns:
        Formatted error message with execution details.
    """
    if not failed_queries:
        return "✅ All queries executed successfully."
    
    error_messages = []
    
    for query in failed_queries[:5]:
        analysis_id = query.get("analysis_id", "?")
        sub_id = query.get("sub_analysis_id", "?")
        title = query.get("title", "Untitled")
        error_type = query.get("error_type", "unknown")
        error_msg = query.get("error_msg", "")
        
        location = f"Analysis {analysis_id} → Sub-analysis {sub_id}"
        truncated_msg = error_msg[:150] + "..." if len(error_msg) > 150 else error_msg
        
        error_messages.append(f"""
  [{location}] "{title}"
    Type: {error_type}
    Error: {truncated_msg}""")
    
    total = len(failed_queries)
    
    result = f"""❌ EXECUTION ERROR ({total} quer{'ies' if total > 1 else 'y'} failed)
{"".join(error_messages)}"""
    
    if total > 5:
        result += f"\n\n  ... and {total - 5} more failed queries"
    
    advice = _get_query_advice(failed_queries)
    result += f"\n\n💡 To fix:\n{advice}"
    
    return result


def format_visualization_errors(failed_viz: List[Dict[str, Any]]) -> str:
    """Format visualization execution errors into a clear message.
    
    Args:
        failed_viz: List of failed visualization info dicts.
    
    Returns:
        Formatted error message with visualization details.
    """
    if not failed_viz:
        return "✅ All visualizations executed successfully."
    
    query_errors = [v for v in failed_viz if v.get("error_type") == "query"]
    viz_errors = [v for v in failed_viz if v.get("error_type") == "visualization"]
    
    error_messages = []
    
    for viz in failed_viz[:5]:
        analysis_id = viz.get("analysis_id", "?")
        sub_id = viz.get("sub_analysis_id", "?")
        title = viz.get("title", "Untitled")
        error_type = viz.get("error_type", "unknown")
        error_msg = viz.get("error_msg", "")
        
        location = f"Analysis {analysis_id} → Sub-analysis {sub_id}"
        type_label = "Query" if error_type == "query" else "Visualization"
        truncated_msg = error_msg[:150] + "..." if len(error_msg) > 150 else error_msg
        
        error_messages.append(f"""
  [{location}] "{title}"
    Step: {type_label}
    Error: {truncated_msg}""")
    
    total = len(failed_viz)
    
    result = f"""❌ VISUALIZATION ERROR ({total} failure{'s' if total > 1 else ''})
{"".join(error_messages)}"""
    
    if total > 5:
        result += f"\n\n  ... and {total - 5} more errors"
    
    advice = _get_visualization_advice(query_errors, viz_errors)
    result += f"\n\n💡 To fix:\n{advice}"
    
    return result


def _get_query_advice(failed_queries: List[Dict[str, Any]]) -> str:
    """Generate advice based on query error patterns."""
    advice_parts = []
    
    error_msgs = [str(q.get("error_msg", "")).lower() for q in failed_queries]
    
    if any("no code" in msg for msg in error_msgs):
        advice_parts.append("- Add 'code_lines' field with Python code for each sub-analysis")
    
    if any("syntax" in msg for msg in error_msgs):
        advice_parts.append("- Check Python syntax (indentation, parentheses, quotes)")
    
    if any("nameerror" in msg for msg in error_msgs):
        advice_parts.append("- Check variable and table names (exact spelling)")
    
    if any("keyerror" in msg for msg in error_msgs):
        advice_parts.append("- Check column names (must exist in tables)")
    
    if any("not a dataframe" in msg for msg in error_msgs):
        advice_parts.append("- Ensure 'result' variable contains a pandas DataFrame")
    
    if not advice_parts:
        advice_parts.append("- Review the Python code for each failed sub-analysis")
    
    return "\n".join(advice_parts)


def _get_visualization_advice(query_errors: List, viz_errors: List) -> str:
    """Generate advice based on visualization error patterns."""
    advice_parts = []
    
    if query_errors:
        advice_parts.append("- Fix query errors first (visualizations depend on data)")
    
    if viz_errors:
        viz_msgs = [str(v.get("error_msg", "")).lower() for v in viz_errors]
        
        if any("no visualization_code" in msg for msg in viz_msgs):
            advice_parts.append("- Add 'visualization_code' field with matplotlib code")
        
        if any("result_plot" in msg for msg in viz_msgs):
            advice_parts.append("- Ensure code creates a 'result_plot' variable with the figure")
        
        if not any("no visualization_code" in msg or "result_plot" in msg for msg in viz_msgs):
            advice_parts.append("- Check matplotlib visualization code (syntax, parameters)")
    
    if not advice_parts:
        advice_parts.append("- Review the code for each failed sub-analysis")
    
    return "\n".join(advice_parts)

