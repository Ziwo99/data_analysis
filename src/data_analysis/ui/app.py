"""Main Streamlit application entry point."""


import json
import threading
import traceback
import streamlit as st
from data_analysis import run, run_mono
from data_analysis.system.utils import update_analysis_status, mark_following_agents_as_error
from data_analysis.system.utils.paths import ERROR_FILE, OUTPUT_AGENT_DIR
from data_analysis.ui.components import reset_analysis_status
from data_analysis.ui.theme import apply_theme_css
from data_analysis.ui.views import (
    render_analysis_page,
    render_landing_page,
    render_performance_view,
    render_report_view,
)


# ============================================================================
# Page Configuration
# ============================================================================

st.set_page_config(
    page_title="Data Analysis",
    page_icon="📊",
    layout="wide"
)

if "current_page" not in st.session_state:
    st.session_state.current_page = "landing"

# ============================================================================
# CrewAI Background Execution
# ============================================================================

def start_crew():
    """Start multi-agent CrewAI pipeline in background thread."""
    if "crew_started" not in st.session_state:
        st.session_state.crew_started = True

        reset_analysis_status()

        # Save analysis name to a temporary file for main.py to read
        analysis_name = st.session_state.get("pending_analysis_name", "")
        if analysis_name:
            from data_analysis.system.utils.paths import CURRENT_ANALYSIS_DIR
            CURRENT_ANALYSIS_DIR.mkdir(parents=True, exist_ok=True)
            temp_name_file = CURRENT_ANALYSIS_DIR / ".analysis_name.txt"
            with open(temp_name_file, "w", encoding="utf-8") as f:
                f.write(analysis_name)

        # Get OpenAI API key and model from session state
        api_key = st.session_state.get("openai_api_key", "")
        model = st.session_state.get("openai_model", "gpt-4o")

        def background_run():
            try:
                # Set environment variables for OpenAI before running
                import os
                if api_key:
                    os.environ["OPENAI_API_KEY"] = api_key
                if model:
                    os.environ["OPENAI_MODEL_NAME"] = model
                run()
            except Exception as e:
                # Save error to file for UI to detect
                OUTPUT_AGENT_DIR.mkdir(parents=True, exist_ok=True)
                
                # Format error message for better user experience
                error_str = str(e)
                error_message = error_str
                is_api_error = False
                
                # Detect OpenAI API errors and format them clearly
                if "openai" in error_str.lower() or "api key" in error_str.lower() or "connection error" in error_str.lower() or "401" in error_str or "invalid_api_key" in error_str.lower():
                    is_api_error = True
                    if "connection error" in error_str.lower() or "failed to connect" in error_str.lower():
                        error_message = "❌ OpenAI API connection error\n\nYour OpenAI API key is invalid or expired. Please check your API key in Settings and try again."
                    elif "invalid" in error_str.lower() or "unauthorized" in error_str.lower() or "401" in error_str or "invalid_api_key" in error_str.lower():
                        error_message = "❌ Invalid OpenAI API key\n\nThe API key you provided is not valid. Please check your API key in Settings and try again."
                    else:
                        error_message = f"❌ OpenAI API error\n\n{error_str}\n\nPlease check your API key in Settings."
                
                error_data = {
                    "error": error_message,
                    "traceback": traceback.format_exc(),
                    "agent": "unknown",  # Will be determined from error message
                    "is_api_error": is_api_error  # Flag to indicate API error for redirect
                }
                # Try to extract agent name from error message
                failed_agent = "unknown"
                if "visualization" in error_str.lower() or "VISUALIZATION ERROR" in error_str:
                    failed_agent = "visualization_designer"
                elif "query" in error_str.lower() or "QUERY ERROR" in error_str:
                    failed_agent = "query_builder"
                elif "business" in error_str.lower():
                    failed_agent = "business_analyst"
                elif "schema" in error_str.lower():
                    failed_agent = "schema_interpreter"
                elif "confidentiality" in error_str.lower():
                    failed_agent = "confidentiality_tester"
                
                error_data["agent"] = failed_agent
                
                # Mark failed agent and following agents/scripts as error
                if failed_agent != "unknown":
                    update_analysis_status(failed_agent, "error")
                    mark_following_agents_as_error(failed_agent, mono_mode=False)
                
                with open(ERROR_FILE, "w", encoding="utf-8") as f:
                    json.dump(error_data, f, indent=2, ensure_ascii=False)

        threading.Thread(target=background_run, daemon=True).start()

def start_mono_crew():
    """Start mono-agent CrewAI pipeline in background thread."""
    if "crew_started" not in st.session_state:
        st.session_state.crew_started = True

        reset_analysis_status(mono_mode=True)

        # Save analysis name to a temporary file for mono_main.py to read
        analysis_name = st.session_state.get("pending_analysis_name", "")
        if analysis_name:
            from data_analysis.system.utils.paths import CURRENT_ANALYSIS_DIR
            CURRENT_ANALYSIS_DIR.mkdir(parents=True, exist_ok=True)
            temp_name_file = CURRENT_ANALYSIS_DIR / ".analysis_name.txt"
            with open(temp_name_file, "w", encoding="utf-8") as f:
                f.write(analysis_name)

        # Get OpenAI API key and model from session state
        api_key = st.session_state.get("openai_api_key", "")
        model = st.session_state.get("openai_model", "gpt-4o")

        def background_run():
            try:
                # Set environment variables for OpenAI before running
                import os
                if api_key:
                    os.environ["OPENAI_API_KEY"] = api_key
                if model:
                    os.environ["OPENAI_MODEL_NAME"] = model
                run_mono()
            except Exception as e:
                # Save error to file for UI to detect
                OUTPUT_AGENT_DIR.mkdir(parents=True, exist_ok=True)
                
                # Format error message for better user experience
                error_str = str(e)
                error_message = error_str
                is_api_error = False
                
                # Detect OpenAI API errors and format them clearly
                if "openai" in error_str.lower() or "api key" in error_str.lower() or "connection error" in error_str.lower() or "401" in error_str or "invalid_api_key" in error_str.lower():
                    is_api_error = True
                    if "connection error" in error_str.lower() or "failed to connect" in error_str.lower():
                        error_message = "❌ OpenAI API connection error\n\nYour OpenAI API key is invalid or expired. Please check your API key in Settings and try again."
                    elif "invalid" in error_str.lower() or "unauthorized" in error_str.lower() or "401" in error_str or "invalid_api_key" in error_str.lower():
                        error_message = "❌ Invalid OpenAI API key\n\nThe API key you provided is not valid. Please check your API key in Settings and try again."
                    else:
                        error_message = f"❌ OpenAI API error\n\n{error_str}\n\nPlease check your API key in Settings."
                
                error_data = {
                    "error": error_message,
                    "traceback": traceback.format_exc(),
                    "agent": "mono_agent",
                    "is_api_error": is_api_error  # Flag to indicate API error for redirect
                }
                # Mark failed agent and following agents/scripts as error
                update_analysis_status("mono_agent", "error")
                mark_following_agents_as_error("mono_agent", mono_mode=True)
                
                with open(ERROR_FILE, "w", encoding="utf-8") as f:
                    json.dump(error_data, f, indent=2, ensure_ascii=False)

        threading.Thread(target=background_run, daemon=True).start()

# ============================================================================
# Page Routing
# ============================================================================

if st.session_state.current_page == "landing":
    render_landing_page()

elif st.session_state.current_page == "analysis":
    apply_theme_css()

    # Check for pipeline errors
    if ERROR_FILE.exists():
        try:
            with open(ERROR_FILE, "r", encoding="utf-8") as f:
                error_data = json.load(f)
            
            # If it's an API error, redirect to landing page
            if error_data.get("is_api_error", False):
                st.session_state.pipeline_error = error_data.get("error", "An error occurred during the analysis.")
                st.session_state.current_page = "landing"
                # Reset crew started flag so user can retry
                st.session_state.crew_started = False
                # Delete error file to prevent showing it again
                ERROR_FILE.unlink(missing_ok=True)
                st.rerun()
            else:
                # Store error in session state for display (but don't redirect for non-API errors)
                st.session_state.pipeline_error = error_data.get("error", "An error occurred during the analysis.")
                # Don't delete the error file - keep it permanently
        except Exception:
            # If we can't read the error file, just continue
            pass

    is_view_mode = st.session_state.get("is_view_mode", False)
    if not is_view_mode:
        pipeline_mode = st.session_state.get("pipeline_mode", "multi")
        if pipeline_mode == "mono":
            start_mono_crew()
        else:
            start_crew()

    render_analysis_page()

elif st.session_state.current_page == "performance_view":
    apply_theme_css()
    render_performance_view()

elif st.session_state.current_page == "report_view":
    apply_theme_css()
    render_report_view()