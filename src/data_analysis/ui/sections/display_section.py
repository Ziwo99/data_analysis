"""Section display and configuration."""


import json
import pickle
import streamlit as st
from data_analysis.ui.sections.raw_schema_section import display_raw_schema
from data_analysis.ui.sections.schema_section import display_schema_summary
from data_analysis.ui.sections.business_section import display_business_analysis
from data_analysis.ui.sections.query_section import display_queries_analysis
from data_analysis.ui.sections.query_analysis_section import display_query_analysis
from data_analysis.ui.sections.visualization_section import display_visualizations_analysis
from data_analysis.ui.sections.confidentiality_section import display_confidentiality_test
from data_analysis.system.utils.paths import (
    RAW_SCHEMA_METADATA_FILE,
    ENRICHED_METADATA_FILE,
    BUSINESS_ANALYSIS_FILE,
    QUERY_RESULTS_PICKLE_FILE,
    QUERY_ANALYSIS_FILE,
    VISUALIZATION_RESULTS_PICKLE_FILE,
    CONFIDENTIALITY_TEST_FILE,
    QUERIES_FILE,
    VISUALIZATIONS_FILE,
)


# ============================================================================
# Section Configuration
# ============================================================================

# Multi-Agent Configuration
AVAILABLE_WINDOWS = [
    "raw_schema",
    "schema_interpreter",
    "business_analyst",
    "query_builder",
    "query_analysis",
    "visualization_designer",
    "confidentiality_tester",
]

WINDOW_DISPLAY_NAMES = {
    "raw_schema": "Raw Data",
    "schema_interpreter": "Schema",
    "business_analyst": "Business Analysis",
    "query_builder": "Queries",
    "query_analysis": "Query Results",
    "visualization_designer": "Visualizations",
    "confidentiality_tester": "Confidentiality",
}

AGENT_DISPLAY_NAMES = {
    "raw_schema": "Extraction Metadata",
    "schema_interpreter": "Schema Interpreter",
    "business_analyst": "Business Analyst",
    "query_builder": "Query Builder",
    "query_analysis": "Query Analysis",
    "visualization_designer": "Visualization Designer",
    "confidentiality_tester": "Confidentiality Tester",
    "mono_agent": "Mono Agent",
}

# Mono-Agent Configuration
MONO_AVAILABLE_WINDOWS = [
    "raw_schema",
    "mono_agent",
]

MONO_WINDOW_DISPLAY_NAMES = {
    "raw_schema": "Raw Data",
    "mono_agent": "Analysis",
}

MONO_AGENT_DISPLAY_NAMES = {
    "raw_schema": "Extraction Metadata",
    "mono_agent": "Mono Agent",
}

# Attempts Configuration
MAX_ATTEMPTS = 4
"""Maximum attempts per agent (1 initial + 3 guardrail retries)."""


# ============================================================================
# Section Display Functions
# ============================================================================

def display_content(active_section: str, agents_data: dict):
    """Display the content of the active section based on agent state.
    
    Args:
        active_section: Name of the active section to display.
        agents_data: Dictionary containing agent data and states.
    """

    section = agents_data.get(active_section, None)

    if not section:
        st.error("No data for this section.")
        return

    state = section.get("state")

    # Switch according to the state
    if state in ["done", "error"]:
        # Check if JSON view mode is enabled
        json_view_mode = st.session_state.get("json_view_mode", False)
        if json_view_mode:
            _display_section_content_json(active_section)
        else:
            _display_section_content(active_section)

def _display_section_content(active_section: str):
    """Route to the appropriate display function based on active section.
    
    Args:
        active_section: Name of the section to display.
    """

    if active_section == "raw_schema":
        # Check if the raw schema metadata file exists
        if not RAW_SCHEMA_METADATA_FILE.exists():
            st.error(f"❌ JSON file does not exist: `{RAW_SCHEMA_METADATA_FILE}`")
            return
        
        # Load and display the raw schema
        try:
            with open(RAW_SCHEMA_METADATA_FILE, "r", encoding="utf-8") as f:
                json_data = json.load(f)
            display_raw_schema(json_data)
        except json.JSONDecodeError as e:
            st.error(f"❌ Error loading JSON: {e}")
        except Exception as e:
            st.error(f"❌ Error: {e}")
    
    elif active_section == "schema_interpreter":
        # Check if the schema summary file exists
        if not ENRICHED_METADATA_FILE.exists():
            st.error(f"❌ JSON file does not exist: `{ENRICHED_METADATA_FILE}`")
            return
        
        # Load and display the schema
        try:
            with open(ENRICHED_METADATA_FILE, "r", encoding="utf-8") as f:
                json_data = json.load(f)
            display_schema_summary(json_data)
        except json.JSONDecodeError as e:
            st.error(f"❌ Error loading JSON: {e}")
        except Exception as e:
            st.error(f"❌ Error: {e}")
    
    elif active_section == "business_analyst":
        # Check if the business analysis file exists
        if not BUSINESS_ANALYSIS_FILE.exists():
            st.error(f"❌ JSON file does not exist: `{BUSINESS_ANALYSIS_FILE}`")
            return
        
        # Load and display the business analysis
        try:
            with open(BUSINESS_ANALYSIS_FILE, "r", encoding="utf-8") as f:
                json_data = json.load(f)
            display_business_analysis(json_data)
        except json.JSONDecodeError as e:
            st.error(f"❌ Error loading JSON: {e}")
        except Exception as e:
            st.error(f"❌ Error: {e}")
    
    elif active_section == "query_builder":
        # Check if the query results pickle file exists
        if not QUERY_RESULTS_PICKLE_FILE.exists():
            st.error(f"❌ Pickle file does not exist: `{QUERY_RESULTS_PICKLE_FILE}`")
            return
        
        # Load and display the query results
        try:
            with open(QUERY_RESULTS_PICKLE_FILE, "rb") as f:
                pickle_data = pickle.load(f)
            display_queries_analysis(pickle_data)
        except pickle.UnpicklingError as e:
            st.error(f"❌ Error loading pickle file: {e}")
        except Exception as e:
            st.error(f"❌ Error: {e}")
    
    elif active_section == "query_analysis":
        # Check if the query analysis file exists
        if not QUERY_ANALYSIS_FILE.exists():
            st.error(f"❌ JSON file does not exist: `{QUERY_ANALYSIS_FILE}`")
            return
        
        # Load and display the query analysis
        try:
            with open(QUERY_ANALYSIS_FILE, "r", encoding="utf-8") as f:
                json_data = json.load(f)
            display_query_analysis(json_data)
        except json.JSONDecodeError as e:
            st.error(f"❌ Error loading JSON: {e}")
        except Exception as e:
            st.error(f"❌ Error: {e}")
    
    elif active_section == "visualization_designer":
        # Check if the visualization results pickle file exists
        if not VISUALIZATION_RESULTS_PICKLE_FILE.exists():
            st.error(f"❌ Pickle file does not exist: `{VISUALIZATION_RESULTS_PICKLE_FILE}`")
            return
        
        # Load and display the visualization results
        try:
            with open(VISUALIZATION_RESULTS_PICKLE_FILE, "rb") as f:
                pickle_data = pickle.load(f)
            display_visualizations_analysis(pickle_data)
        except pickle.UnpicklingError as e:
            st.error(f"❌ Error loading pickle file: {e}")
        except Exception as e:
            st.error(f"❌ Error: {e}")
    
    elif active_section == "confidentiality_tester":
        # Check if the confidentiality test file exists
        if not CONFIDENTIALITY_TEST_FILE.exists():
            st.error(f"❌ File does not exist: `{CONFIDENTIALITY_TEST_FILE}`")
            return
        
        # Load and display the confidentiality test results
        try:
            with open(CONFIDENTIALITY_TEST_FILE, "r", encoding="utf-8") as f:
                json_data = json.load(f)
            display_confidentiality_test(json_data)
        except json.JSONDecodeError as e:
            st.error(f"❌ Error loading JSON: {e}")
        except Exception as e:
            st.error(f"❌ Error: {e}")
    
    elif active_section == "mono_agent":
        # Mono-agent displays the same visualization results as visualization_designer
        if not VISUALIZATION_RESULTS_PICKLE_FILE.exists():
            st.error(f"❌ File does not exist: `{VISUALIZATION_RESULTS_PICKLE_FILE}`")
            return
        
        # Load and display the visualization results (same as visualization_designer)
        try:
            with open(VISUALIZATION_RESULTS_PICKLE_FILE, "rb") as f:
                pickle_data = pickle.load(f)
            display_visualizations_analysis(pickle_data)
        except pickle.UnpicklingError as e:
            st.error(f"❌ Error loading pickle file: {e}")
        except Exception as e:
            st.error(f"❌ Error: {e}")
    
    else:
        st.warning(f"⚠️ Unknown section: {active_section}")

def _display_section_content_json(active_section: str):
    """Display raw JSON content for a section (for project explanation).
    
    Args:
        active_section: Name of the section to display.
    """
    
    # Determine which file to load
    json_file = None
    if active_section == "raw_schema":
        json_file = RAW_SCHEMA_METADATA_FILE
    elif active_section == "schema_interpreter":
        json_file = ENRICHED_METADATA_FILE
    elif active_section == "business_analyst":
        json_file = BUSINESS_ANALYSIS_FILE
    elif active_section == "query_builder":
        json_file = QUERIES_FILE
    elif active_section == "query_analysis":
        json_file = QUERY_ANALYSIS_FILE
    elif active_section == "visualization_designer":
        json_file = VISUALIZATIONS_FILE
    elif active_section == "confidentiality_tester":
        json_file = CONFIDENTIALITY_TEST_FILE
    elif active_section == "mono_agent":
        json_file = VISUALIZATIONS_FILE
    else:
        st.warning(f"⚠️ Unknown section: {active_section}")
        return
    
    if not json_file or not json_file.exists():
        st.error(f"❌ JSON file does not exist: `{json_file}`")
        return
    
    try:
        with open(json_file, "r", encoding="utf-8") as f:
            json_data = json.load(f)
        
        # Format JSON with proper indentation
        json_str = json.dumps(json_data, indent=2, ensure_ascii=False)
        
        # Display with custom styling
        _display_formatted_json(json_str)
        
    except json.JSONDecodeError as e:
        st.error(f"❌ Error parsing JSON: {e}")
    except Exception as e:
        st.error(f"❌ Error loading JSON: {e}")

def _display_formatted_json(json_str: str):
    """Display JSON in a simple, clean format.
    
    Args:
        json_str: JSON string to display.
    """
    # Display JSON using st.code for simple, clean output
    st.code(json_str, language="json")

