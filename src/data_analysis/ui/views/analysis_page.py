"""Analysis page - displays agent results and navigation."""


import streamlit as st
from streamlit_autorefresh import st_autorefresh
from data_analysis.ui.components import (
    render_navigation_bar,
    initialize_session_state,
    load_agents_data,
)
from data_analysis.ui.sections import (
    AVAILABLE_WINDOWS,
    MONO_AVAILABLE_WINDOWS,
)
from data_analysis.ui.sections import display_content
from data_analysis.system.utils import (
    save_analysis,
    create_source_data_zip,
    sanitize_folder_name,
)


def all_agents_done(agents_data: dict, mono_mode: bool = False) -> bool:
    """Check if all agents have completed their tasks (done or error).
    
    Args:
        agents_data: Dictionary containing agent status data.
        mono_mode: Whether running in mono-agent mode.
    
    Returns:
        True if all agents have status 'done' or 'error' (terminal states).
    """
    windows = MONO_AVAILABLE_WINDOWS if mono_mode else AVAILABLE_WINDOWS
    for agent_name in windows:
        agent = agents_data.get(agent_name, {})
        state = agent.get("state", "waiting")
        if state not in ["done", "error"]:
            return False
    return True

def has_errors(agents_data: dict, mono_mode: bool = False) -> bool:
    """Check if any agent has an error state.
    
    Args:
        agents_data: Dictionary containing agent status data.
        mono_mode: Whether running in mono-agent mode.
    
    Returns:
        True if any agent has status 'error'.
    """
    windows = MONO_AVAILABLE_WINDOWS if mono_mode else AVAILABLE_WINDOWS
    for agent_name in windows:
        agent = agents_data.get(agent_name, {})
        state = agent.get("state", "waiting")
        if state == "error":
            return True
    return False

def auto_save_analysis():
    """Auto-save analysis when all agents complete (done or error).
    
    Only saves once per session. Works even if some agents have errors.
    """
    # Check if already saved
    if st.session_state.get("analysis_saved", False):
        return
    
    # Get pending analysis info
    analysis_name = st.session_state.get("pending_analysis_name")
    dataset = st.session_state.get("pending_analysis_dataset", "unknown")
    source = st.session_state.get("pending_analysis_source", "unknown")
    pipeline_mode = st.session_state.get("pipeline_mode", "multi")
    openai_model = st.session_state.get("openai_model", "gpt-4o")
    
    if not analysis_name:
        return
    
    # Attempt to save (even if there are errors)
    if save_analysis(analysis_name, dataset, source, pipeline_mode, openai_model):
        st.session_state.analysis_saved = True
        st.session_state.saved_analysis_name = analysis_name
        st.toast(f"✅ Analysis « {analysis_name} » saved automatically", icon="💾")
        
        # Note: No need to clean up data folder anymore as it's part of the analysis

def render_top_bar(all_done: bool, is_view_mode: bool, mono_mode: bool = False, has_errors: bool = False):
    """Render the top bar with back button and action buttons.
    
    Args:
        all_done: Whether all agents have completed (done or error).
        is_view_mode: Whether viewing a saved analysis.
        mono_mode: Whether running in mono-agent mode.
        has_errors: Whether any agent has an error state.
    """
    analysis_name = st.session_state.get("loaded_analysis_name", "") if is_view_mode else st.session_state.get("pending_analysis_name", "")
    
    # Only show top bar when analysis is complete (done or error) or in view mode
    show_top_bar = all_done or is_view_mode
    
    if show_top_bar:
        # Single row: back button + badge + action buttons (right-aligned)
        col1, col2, col3 = st.columns([1, 2, 3])
        
        with col1:
            if st.button("← Back to home", key="back_to_landing_btn", type="secondary", use_container_width=True):
                # Reset relevant session state
                st.session_state.current_page = "landing"
                st.session_state.pop("crew_started", None)
                st.session_state.pop("analysis_saved", None)
                st.session_state.pop("pending_analysis_name", None)
                st.session_state.pop("is_view_mode", None)
                st.session_state.pop("loaded_analysis_name", None)
                st.session_state.pop("data_validated", None)
                st.session_state.pop("analysis_name", None)
                st.rerun()
            
            # View mode buttons below back button
            # Initialize json_view_mode if not exists
            if "json_view_mode" not in st.session_state:
                st.session_state.json_view_mode = False
            
            is_formatted = not st.session_state.json_view_mode
            is_json = st.session_state.json_view_mode
            
            # Two buttons for view mode selection
            btn_col1, btn_col2 = st.columns(2, gap="small")
            
            with btn_col1:
                if st.button(
                    "Formatted",
                    key="view_formatted_btn",
                    type="primary" if is_formatted else "secondary",
                    use_container_width=True
                ):
                    st.session_state.json_view_mode = False
                    st.rerun()
            
            with btn_col2:
                if st.button(
                    "JSON",
                    key="view_json_btn",
                    type="primary" if is_json else "secondary",
                    use_container_width=True
                ):
                    st.session_state.json_view_mode = True
                    st.rerun()
        
        with col2:
            if is_view_mode:
                # View mode badge centered
                st.markdown(f"""
                    <div style="display: flex; justify-content: center;">
                    <div style="display: inline-flex; align-items: center; gap: 0.6rem; padding: 0.5rem 1rem; background: linear-gradient(135deg, rgba(167, 139, 250, 0.15) 0%, rgba(139, 92, 246, 0.1) 100%); border: 1px solid rgba(167, 139, 250, 0.4); border-radius: 999px; box-shadow: 0 2px 10px rgba(167, 139, 250, 0.15);">
                    <span style="font-size: 1rem;">📂</span>
                    <span style="color: #c4b5fd; font-weight: 600; font-size: 0.85rem;">View Mode</span>
                    <span style="color: #a78bfa; font-size: 0.75rem; opacity: 0.7; display: flex; align-items: center; line-height: 1;">—</span>
                    <span style="color: #a78bfa; font-size: 0.8rem;">{analysis_name}</span>
                    </div>
                    </div>
                                    """, unsafe_allow_html=True
                )
            elif all_done and analysis_name:
                # Analysis complete badge centered
                st.markdown(f"""
                    <div style="display: flex; justify-content: center;">
                    <div style="display: inline-flex; align-items: center; gap: 0.6rem; padding: 0.5rem 1rem; background: linear-gradient(135deg, rgba(34, 197, 94, 0.15) 0%, rgba(22, 163, 74, 0.1) 100%); border: 1px solid rgba(34, 197, 94, 0.4); border-radius: 999px; box-shadow: 0 2px 10px rgba(34, 197, 94, 0.15);">
                    <span style="font-size: 1rem;">✅</span>
                    <span style="color: #86efac; font-weight: 600; font-size: 0.85rem;">Analysis Complete</span>
                    <span style="color: #4ade80; font-size: 0.75rem; opacity: 0.7; display: flex; align-items: center; line-height: 1;">—</span>
                    <span style="color: #4ade80; font-size: 0.8rem;">{analysis_name}</span>
                    </div>
                    </div>
                                    """, unsafe_allow_html=True
                )
        
        with col3:
            # Action buttons aligned to the right
            if mono_mode:
                # Mono mode: 2-3 buttons depending on errors
                if has_errors:
                    # With errors: only Download and Performance
                    btn_col1, btn_col2 = st.columns([1.5, 1.5], gap="small")
                    
                    with btn_col1:
                        _render_download_button(analysis_name, is_view_mode)
                    
                    with btn_col2:
                        if st.button("Show performance summary", key="perf_summary_btn", type="secondary", use_container_width=True):
                            st.session_state.current_page = "performance_view"
                            st.rerun()
                else:
                    # Without errors: Download, Performance, and Full Report
                    btn_col1, btn_col2, btn_col3 = st.columns([1.5, 1.5, 1.5], gap="small")
                    
                    with btn_col1:
                        _render_download_button(analysis_name, is_view_mode)
                    
                    with btn_col2:
                        if st.button("Show performance summary", key="perf_summary_btn", type="secondary", use_container_width=True):
                            st.session_state.current_page = "performance_view"
                            st.rerun()
                    
                    with btn_col3:
                        if st.button("View full report", key="full_report_btn", type="secondary", use_container_width=True):
                            st.session_state.current_page = "report_view"
                            st.rerun()
            else:
                # Multi-agent mode: 2-3 buttons depending on errors
                # Use tighter column spacing
                if has_errors:
                    # With errors: only Download and Performance
                    btn_col1, btn_col2 = st.columns([1.5, 1.5], gap="small")
                    
                    with btn_col1:
                        _render_download_button(analysis_name, is_view_mode)
                    
                    with btn_col2:
                        if st.button("Show performance summary", key="perf_summary_btn", type="secondary", use_container_width=True):
                            st.session_state.current_page = "performance_view"
                            st.rerun()
                else:
                    # Without errors: Download, Performance, and Full Report
                    btn_col1, btn_col2, btn_col3 = st.columns([1.5, 1.5, 1.5], gap="small")
                    
                    with btn_col1:
                        _render_download_button(analysis_name, is_view_mode)
                    
                    with btn_col2:
                        if st.button("Show performance summary", key="perf_summary_btn", type="secondary", use_container_width=True):
                            st.session_state.current_page = "performance_view"
                            st.rerun()
                    
                    with btn_col3:
                        if st.button("View full report", key="full_report_btn", type="secondary", use_container_width=True):
                            st.session_state.current_page = "report_view"
                            st.rerun()

def _render_download_button(analysis_name: str, is_view_mode: bool):
    """Render the download button for source data files.
    
    Args:
        analysis_name: Name of the analysis.
        is_view_mode: Whether viewing a saved analysis.
    """
    # Determine where to get the data from
    analysis_saved = st.session_state.get("analysis_saved", False)
    
    if is_view_mode or analysis_saved:
        # For view mode or saved analysis, get from saved analysis folder
        # Use sanitized folder name for saved analyses
        folder_name = sanitize_folder_name(analysis_name) if analysis_name else None
        zip_data = create_source_data_zip(analysis_name=folder_name) if folder_name else None
    else:
        # For ongoing analysis (not yet saved), get from current dataset
        dataset = st.session_state.get("pending_analysis_dataset")
        zip_data = create_source_data_zip(dataset=dataset)
    
    if zip_data:
        # Sanitize the filename
        safe_name = sanitize_folder_name(analysis_name) if analysis_name else "analysis"
        
        st.download_button(
            label="Download source data",
            data=zip_data,
            file_name=f"{safe_name}_data.zip",
            mime="application/zip",
            key="download_source_btn",
            type="secondary",
            use_container_width=True,
        )

def render_analysis_page():
    """Render the analysis page with agent navigation and results display."""
    
    # Initialize session state
    initialize_session_state()
    
    # Check if in view mode (loaded from saved analysis)
    is_view_mode = st.session_state.get("is_view_mode", False)
    
    # Check if in mono-agent mode
    mono_mode = st.session_state.get("pipeline_mode", "multi") == "mono"
    
    # Data loading
    agents_data = load_agents_data()
    
    # Check if all agents are done (done or error)
    all_done = all_agents_done(agents_data, mono_mode=mono_mode)
    has_errors_state = has_errors(agents_data, mono_mode=mono_mode)
    
    # Auto-save when all agents are done (even with errors, only for new analyses, not view mode)
    if all_done and not is_view_mode:
        auto_save_analysis()
    
    # Display error message if present (in red error box)
    if has_errors_state and "pipeline_error" in st.session_state:
        error_message = st.session_state.pipeline_error
        # Clean error message
        if "Task failed guardrail" in error_message:
            if "Last error:" in error_message:
                parts = error_message.split("Last error:", 1)
                if len(parts) > 1:
                    error_message = parts[1].strip()
            else:
                error_message = error_message.replace("Task failed guardrail 0 validation after 3 retries. ", "")
        
        st.error(f"⚠️ **Analysis incomplete:**\n\n{error_message}")
    
    # Top bar with back button (only when complete or view mode)
    render_top_bar(all_done, is_view_mode, mono_mode=mono_mode, has_errors=has_errors_state)
    
    # Initialize json_view_mode if not exists (for when top bar is not shown)
    if "json_view_mode" not in st.session_state:
        st.session_state.json_view_mode = False
    
    # Auto refresh only if not all agents are done AND not in view mode
    if not all_done and not is_view_mode:
        st_autorefresh(interval=1000, limit=None, key="auto_refresh")
    
    # Navigation between sections
    render_navigation_bar(agents_data, mono_mode=mono_mode)
    
    # Active content container
    active_section = st.session_state.active_section
    display_content(active_section, agents_data)