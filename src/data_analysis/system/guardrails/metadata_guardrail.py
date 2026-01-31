"""Guardrail for validating schema interpreter output."""


import json
from typing import Any, Tuple
from crewai.tasks.task_output import TaskOutput
from pydantic import ValidationError
from data_analysis.system.utils.error_formatter import (
    format_json_error,
    format_pydantic_error,
)
from data_analysis.crew.models import EnrichedMetadataModel
from data_analysis.system.utils import (
    increment_agent_attempts,
    get_agent_attempts,
    update_analysis_status,
    mark_following_agents_as_error,
)
from data_analysis.system.utils.paths import ENRICHED_METADATA_FILE


def metadata_guardrail(result: TaskOutput) -> Tuple[bool, Any]:
    """Validate schema interpreter output and save result.
    
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
        attempts = get_agent_attempts("schema_interpreter")
        MAX_ATTEMPTS = 4
        
        if attempts >= MAX_ATTEMPTS:
            update_analysis_status("schema_interpreter", "error")
            mark_following_agents_as_error("schema_interpreter", mono_mode=False)
            print(f"❌ Schema Interpreter - Failed after {MAX_ATTEMPTS} attempts")
            return (False, format_json_error(e))
        
        increment_agent_attempts("schema_interpreter")
        attempts = get_agent_attempts("schema_interpreter")
        display_attempts = min(attempts, MAX_ATTEMPTS)
        print(f"❌ Schema Interpreter - Retry (attempt {display_attempts}/{MAX_ATTEMPTS})")
        return (False, format_json_error(e))

    # Validate against Pydantic model
    try:
        validated = EnrichedMetadataModel.model_validate(data)
    except ValidationError as e:
        attempts = get_agent_attempts("schema_interpreter")
        MAX_ATTEMPTS = 4
        
        if attempts >= MAX_ATTEMPTS:
            update_analysis_status("schema_interpreter", "error")
            mark_following_agents_as_error("schema_interpreter", mono_mode=False)
            print(f"❌ Schema Interpreter - Failed after {MAX_ATTEMPTS} attempts")
            return (False, format_pydantic_error(e, "enriched_metadata"))
        
        increment_agent_attempts("schema_interpreter")
        attempts = get_agent_attempts("schema_interpreter")
        display_attempts = min(attempts, MAX_ATTEMPTS)
        print(f"❌ Schema Interpreter - Retry (attempt {display_attempts}/{MAX_ATTEMPTS})")
        return (False, format_pydantic_error(e, "enriched_metadata"))

    # Save validated output
    validated_dict = validated.model_dump()
    ENRICHED_METADATA_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(ENRICHED_METADATA_FILE, "w", encoding="utf-8") as f:
        json.dump(validated_dict, f, indent=2, ensure_ascii=False)

    # Update agent status and trigger next agent
    update_analysis_status("schema_interpreter", "done")
    print("✅ Schema Interpreter")
    update_analysis_status("business_analyst", "in_progress")

    return (True, validated_dict)
