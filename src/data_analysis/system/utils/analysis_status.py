"""Analysis status tracking and management."""


import json
from datetime import datetime
from data_analysis.system.utils.paths import ANALYSIS_STATUS_FILE, CURRENT_ANALYSIS_DIR


# ============================================================================
# Default Status Configuration
# ============================================================================

DEFAULT_AGENTS_STATUS = {
    "raw_schema": {"state": "waiting", "attempts": 0, "start_time": None, "end_time": None},
    "schema_interpreter": {"state": "waiting", "attempts": 0, "start_time": None, "end_time": None},
    "business_analyst": {"state": "waiting", "attempts": 0, "start_time": None, "end_time": None},
    "query_builder": {"state": "waiting", "attempts": 0, "start_time": None, "end_time": None},
    "query_analysis": {"state": "waiting", "attempts": 0, "start_time": None, "end_time": None},
    "visualization_designer": {"state": "waiting", "attempts": 0, "start_time": None, "end_time": None},
    "confidentiality_tester": {"state": "waiting", "attempts": 0, "start_time": None, "end_time": None},
}

MONO_DEFAULT_AGENTS_STATUS = {
    "raw_schema": {"state": "waiting", "attempts": 0, "start_time": None, "end_time": None},
    "mono_agent": {"state": "waiting", "attempts": 0, "start_time": None, "end_time": None},
}


# ============================================================================
# Status Management Functions
# ============================================================================

def _load_analysis_status() -> dict:
    """Load current analysis status from file."""
    if ANALYSIS_STATUS_FILE.exists():
        try:
            with open(ANALYSIS_STATUS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            pass
    return {k: v.copy() for k, v in DEFAULT_AGENTS_STATUS.items()}

def _save_analysis_status(data: dict) -> None:
    """Save analysis status to file."""
    CURRENT_ANALYSIS_DIR.mkdir(parents=True, exist_ok=True)
    with open(ANALYSIS_STATUS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def update_analysis_status(agent_name: str, state: str = "done") -> None:
    """Update the status of an agent in the analysis.
    
    Args:
        agent_name: Name of the agent to update.
        state: New state ("waiting", "in_progress", "done", "error").
    """
    data = _load_analysis_status()

    current_agent = data.get(agent_name, {})
    current_attempts = current_agent.get("attempts", 0)
    current_state = current_agent.get("state", "waiting")
    current_start_time = current_agent.get("start_time")
    current_end_time = current_agent.get("end_time")

    start_time = current_start_time
    end_time = current_end_time

    # Increment attempts and set start time when entering in_progress
    if state == "in_progress":
        if current_state != "in_progress":
            current_attempts += 1
            start_time = datetime.now().isoformat()
            end_time = None
        elif start_time is None:
            # If already in_progress but start_time is None, set it now
            start_time = datetime.now().isoformat()

    # Set end time when completing
    if state == "done" and current_state != "done":
        end_time = datetime.now().isoformat()

    data[agent_name] = {
        "state": state,
        "attempts": current_attempts,
        "start_time": start_time,
        "end_time": end_time
    }

    _save_analysis_status(data)

def increment_agent_attempts(agent_name: str) -> None:
    """Increment attempts count for an agent (on guardrail failure).
    
    Args:
        agent_name: Name of the agent.
    """
    data = _load_analysis_status()

    current = data.get(agent_name, {"state": "in_progress", "attempts": 0})
    current_attempts = current.get("attempts", 0)
    MAX_ATTEMPTS = 4
    
    # Don't increment if already at max (safety check)
    if current_attempts >= MAX_ATTEMPTS:
        return
    
    current["attempts"] = current_attempts + 1
    data[agent_name] = current

    _save_analysis_status(data)

def get_agent_attempts(agent_name: str) -> int:
    """Get current attempts count for an agent.
    
    Args:
        agent_name: Name of the agent.
    
    Returns:
        Number of attempts.
    """
    data = _load_analysis_status()
    return data.get(agent_name, {}).get("attempts", 0)

def mark_following_agents_as_error(failed_agent: str, mono_mode: bool = False) -> None:
    """Mark all agents and scripts that come after the failed agent as 'error'.
    
    Args:
        failed_agent: Name of the agent that failed.
        mono_mode: If True, uses mono-agent pipeline sequence.
    """
    # Define pipeline sequences
    if mono_mode:
        pipeline = ["raw_schema", "mono_agent"]
    else:
        pipeline = ["raw_schema", "schema_interpreter", "business_analyst", "query_builder", 
                   "query_analysis", "visualization_designer", "confidentiality_tester"]
    
    # Find the index of the failed agent
    try:
        failed_index = pipeline.index(failed_agent)
    except ValueError:
        # Agent not found in pipeline, mark all as error
        failed_index = -1
    
    # Mark all following agents and scripts as error
    data = _load_analysis_status()
    for i in range(failed_index + 1, len(pipeline)):
        agent_name = pipeline[i]
        if agent_name in data:
            current = data[agent_name]
            # Only mark as error if not already done
            if current.get("state") != "done":
                data[agent_name] = {
                    "state": "error",
                    "attempts": current.get("attempts", 0),
                    "start_time": current.get("start_time"),
                    "end_time": datetime.now().isoformat() if current.get("start_time") else None
                }
    
    _save_analysis_status(data)

