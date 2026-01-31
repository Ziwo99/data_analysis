"""Performance summary view - displays script and agent execution times and statistics."""


from datetime import datetime
import pandas as pd
import streamlit as st
from data_analysis.ui.components import load_agents_data
from data_analysis.ui.sections import (
    AVAILABLE_WINDOWS,
    AGENT_DISPLAY_NAMES,
    MONO_AVAILABLE_WINDOWS,
    MONO_AGENT_DISPLAY_NAMES,
)


# Scripts are system-level operations (not agents)
SCRIPTS = ["raw_schema", "query_analysis"]
SCRIPT_DISPLAY_NAMES = {
    "raw_schema": "Metadata Extraction",
    "query_analysis": "Query Analysis",
}


def _format_duration(start_time: str, end_time: str) -> str:
    """Format the duration between two ISO timestamps.
    
    Args:
        start_time: ISO format start timestamp.
        end_time: ISO format end timestamp.
    
    Returns:
        Human-readable duration string (e.g., "1m 30s").
    """
    if not start_time or not end_time:
        return "-"
    
    try:
        start = datetime.fromisoformat(start_time)
        end = datetime.fromisoformat(end_time)
        duration = (end - start).total_seconds()
        
        if duration < 1:
            return f"{duration*1000:.0f}ms"
        elif duration < 60:
            return f"{duration:.2f}s"
        else:
            minutes = int(duration // 60)
            seconds = int(duration % 60)
            return f"{minutes}m {seconds}s"
    except (ValueError, TypeError):
        return "-"


def _get_duration_seconds(start_time: str, end_time: str) -> float:
    """Get duration in seconds between two ISO timestamps.
    
    Args:
        start_time: ISO format start timestamp.
        end_time: ISO format end timestamp.
    
    Returns:
        Duration in seconds, or 0 if timestamps are invalid.
    """
    if not start_time or not end_time:
        return 0
    
    try:
        start = datetime.fromisoformat(start_time)
        end = datetime.fromisoformat(end_time)
        return (end - start).total_seconds()
    except (ValueError, TypeError):
        return 0


def _format_total_duration(seconds: float) -> str:
    """Format total duration in seconds to human-readable string.
    
    Args:
        seconds: Total duration in seconds.
    
    Returns:
        Formatted string (e.g., "2h 15m" or "45.3s").
    """
    if seconds <= 0:
        return "-"
    
    if seconds < 60:
        return f"{seconds:.2f}s"
    elif seconds < 3600:
        minutes = int(seconds // 60)
        secs = int(seconds % 60)
        return f"{minutes}m {secs}s"
    else:
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        return f"{hours}h {minutes}m"


def _get_status_icon(state: str) -> str:
    """Get status icon for a given state.
    
    Args:
        state: State string.
    
    Returns:
        Status icon emoji.
    """
    if state == "done":
        return "✅"
    elif state == "error":
        return "❌"
    elif state == "in_progress":
        return "🔄"
    else:
        return "⏳"


def render_performance_view():
    """Render the performance summary view with script and agent statistics."""
    
    # Get analysis name for display
    is_view_mode = st.session_state.get("is_view_mode", False)
    analysis_name = st.session_state.get("loaded_analysis_name", "") if is_view_mode else st.session_state.get("pending_analysis_name", "")
    
    # Check if mono mode
    mono_mode = st.session_state.get("pipeline_mode", "multi") == "mono"
    
    # Select the appropriate windows and display names based on mode
    windows = MONO_AVAILABLE_WINDOWS if mono_mode else AVAILABLE_WINDOWS
    display_names = MONO_AGENT_DISPLAY_NAMES if mono_mode else AGENT_DISPLAY_NAMES
    
    # Header with back button
    col1, col2, col3 = st.columns([1, 2, 2])
    
    with col1:
        if st.button("← Back to analysis", key="back_to_analysis_from_perf", type="secondary", use_container_width=True):
            st.session_state.current_page = "analysis"
            st.rerun()
    
    with col2:
        st.markdown(
            f'<div style="display: flex; justify-content: center;">'
            f'<div style="display: inline-flex; align-items: center; gap: 0.6rem; padding: 0.5rem 1rem; '
            f'background: linear-gradient(135deg, rgba(251, 191, 36, 0.15) 0%, rgba(245, 158, 11, 0.1) 100%); '
            f'border: 1px solid rgba(251, 191, 36, 0.4); border-radius: 999px; '
            f'box-shadow: 0 2px 10px rgba(251, 191, 36, 0.15);">'
            f'<span style="font-size: 1rem;">📊</span>'
            f'<span style="color: #fcd34d; font-weight: 600; font-size: 0.85rem;">Performance Summary</span>'
            f'<span style="color: #fbbf24; font-size: 0.75rem; opacity: 0.7; display: flex; align-items: center; line-height: 1;">—</span>'
            f'<span style="color: #fbbf24; font-size: 0.8rem;">{analysis_name}</span>'
            f'</div></div>',
            unsafe_allow_html=True
        )
    
    st.markdown('<div style="height: 1.5rem;"></div>', unsafe_allow_html=True)
    
    # Load agents data
    agents_data = load_agents_data()
    
    # Build table rows in pipeline order, separating scripts and agents
    all_rows = []
    script_total_seconds = 0
    agent_total_seconds = 0
    
    for item_name in windows:
        item = agents_data.get(item_name, {})
        state = item.get("state", "waiting")
        attempts = item.get("attempts", 0)
        start_time = item.get("start_time")
        end_time = item.get("end_time")
        
        # Format duration
        duration_str = _format_duration(start_time, end_time)
        duration_seconds = _get_duration_seconds(start_time, end_time)
        
        if item_name in SCRIPTS:
            display_name = SCRIPT_DISPLAY_NAMES.get(item_name, item_name)
            script_total_seconds += duration_seconds
            all_rows.append({
                "Task": display_name,
                "Type": "🔧 Script",
                "Execution Time": duration_str,
                "Attempts": "1",
                "Status": _get_status_icon(state),
            })
        else:
            display_name = display_names.get(item_name, item_name)
            agent_total_seconds += duration_seconds
            attempts_str = str(attempts) if attempts > 0 else "-"
            all_rows.append({
                "Task": display_name,
                "Type": "🤖 Agent",
            "Execution Time": duration_str,
                "Attempts": attempts_str,
                "Status": _get_status_icon(state),
    })
    
    # Create DataFrame and display
    df = pd.DataFrame(all_rows)
    
    st.markdown('<div style="height: 1.6rem;"></div>', unsafe_allow_html=True)
    
    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Task": st.column_config.TextColumn("Task", width="large"),
            "Type": st.column_config.TextColumn("Type", width="small"),
            "Execution Time": st.column_config.TextColumn("Execution Time", width="medium"),
            "Attempts": st.column_config.TextColumn("Attempts", width="small"),
            "Status": st.column_config.TextColumn("Status", width="small"),
        }
    )
    
    st.markdown('<div style="height: 2rem;"></div>', unsafe_allow_html=True)
    
    # Statistics cards
    total_seconds = script_total_seconds + agent_total_seconds
    script_count = sum(1 for item_name in windows if item_name in SCRIPTS)
    agent_count = sum(1 for item_name in windows if item_name not in SCRIPTS)
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.markdown(
            f'<div style="background: linear-gradient(135deg, rgba(59, 130, 246, 0.1) 0%, rgba(37, 99, 235, 0.05) 100%); '
            f'border: 1px solid rgba(59, 130, 246, 0.3); border-radius: 12px; padding: 1.5rem; text-align: center;">'
            f'<div style="font-size: 1.5rem; color: #64748b; margin-bottom: 0.75rem; font-weight: 500;">Scripts</div>'
            f'<div style="font-size: 2rem; font-weight: 700; color: #3b82f6;">{script_count}</div>'
            f'</div>',
            unsafe_allow_html=True
        )
    
    with col2:
        st.markdown(
            f'<div style="background: linear-gradient(135deg, rgba(139, 92, 246, 0.1) 0%, rgba(124, 58, 237, 0.05) 100%); '
            f'border: 1px solid rgba(139, 92, 246, 0.3); border-radius: 12px; padding: 1.5rem; text-align: center;">'
            f'<div style="font-size: 1.5rem; color: #64748b; margin-bottom: 0.75rem; font-weight: 500;">Agents</div>'
            f'<div style="font-size: 2rem; font-weight: 700; color: #8b5cf6;">{agent_count}</div>'
            f'</div>',
            unsafe_allow_html=True
        )
    
    with col3:
        st.markdown(
            f'<div style="background: linear-gradient(135deg, rgba(16, 185, 129, 0.1) 0%, rgba(5, 150, 105, 0.05) 100%); '
            f'border: 1px solid rgba(16, 185, 129, 0.3); border-radius: 12px; padding: 1.5rem; text-align: center;">'
            f'<div style="font-size: 1.5rem; color: #64748b; margin-bottom: 0.75rem; font-weight: 500;">Script Time</div>'
            f'<div style="font-size: 2rem; font-weight: 700; color: #10b981;">{_format_total_duration(script_total_seconds)}</div>'
            f'</div>',
            unsafe_allow_html=True
        )
    
    with col4:
        st.markdown(
            f'<div style="background: linear-gradient(135deg, rgba(139, 92, 246, 0.1) 0%, rgba(124, 58, 237, 0.05) 100%); '
            f'border: 1px solid rgba(139, 92, 246, 0.3); border-radius: 12px; padding: 1.5rem; text-align: center;">'
            f'<div style="font-size: 1.5rem; color: #64748b; margin-bottom: 0.75rem; font-weight: 500;">Agent Time</div>'
            f'<div style="font-size: 2rem; font-weight: 700; color: #8b5cf6;">{_format_total_duration(agent_total_seconds)}</div>'
            f'</div>',
            unsafe_allow_html=True
        )
    
    with col5:
        st.markdown(
            f'<div style="background: linear-gradient(135deg, rgba(245, 158, 11, 0.1) 0%, rgba(217, 119, 6, 0.05) 100%); '
            f'border: 1px solid rgba(245, 158, 11, 0.3); border-radius: 12px; padding: 1.5rem; text-align: center;">'
            f'<div style="font-size: 1.5rem; color: #64748b; margin-bottom: 0.75rem; font-weight: 500;">Total Time</div>'
            f'<div style="font-size: 2rem; font-weight: 700; color: #f59e0b;">{_format_total_duration(total_seconds)}</div>'
            f'</div>',
            unsafe_allow_html=True
        )
    
