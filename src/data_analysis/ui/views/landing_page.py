"""Landing page - entry point for the application."""


from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple
import pandas as pd
import streamlit as st
from data_analysis.system.utils.paths import TEST_DATA_DIR, OUTPUT_DATA_DIR
import shutil
from data_analysis.system.utils import (
    get_saved_analyses,
    validate_analysis_name,
    load_analysis,
    delete_analysis,
    get_analysis_metadata,
    save_uploaded_files,
)


# =============================================================================
# DATA LOADING FUNCTIONS
# =============================================================================

def get_available_csv_folders() -> List[str]:
    """Get list of available CSV data folders.
    
    Returns:
        Sorted list of folder names, excluding the 'uploads' folder.
    """
    if not TEST_DATA_DIR.exists():
        return []
    
    folders = [
        d.name for d in TEST_DATA_DIR.iterdir() 
        if d.is_dir() and not d.name.startswith('.')
    ]
    return sorted(folders)

def get_csv_files_info(folder_name: str) -> List[Dict]:
    """Get information about CSV files in a folder.
    
    Args:
        folder_name: Name of the folder within TEST_DATA_DIR.
    
    Returns:
        List of dicts with file info (name, columns, rows, path).
    """
    folder_path = TEST_DATA_DIR / folder_name
    if not folder_path.exists():
        return []
    
    files_info = []
    for csv_file in sorted(folder_path.glob("*.csv")):
        try:
            df = pd.read_csv(csv_file, nrows=0)  # Just headers
            row_count = sum(1 for _ in open(csv_file)) - 1  # Count lines minus header
            files_info.append({
                "name": csv_file.stem,
                "columns": len(df.columns),
                "rows": row_count,
                "path": csv_file
            })
        except Exception:
            files_info.append({
                "name": csv_file.stem,
                "columns": 0,
                "rows": 0,
                "path": csv_file
            })
    
    return files_info

def get_uploaded_files_info(uploaded_files) -> List[Dict]:
    """Get information about uploaded files.
    
    Args:
        uploaded_files: List of Streamlit UploadedFile objects.
    
    Returns:
        List of dicts with file info (name, columns, rows, df).
    """
    if not uploaded_files:
        return []
    
    files_info = []
    for uploaded_file in uploaded_files:
        try:
            # Convert Excel to CSV in memory, then read as CSV
            if uploaded_file.name.endswith(('.xlsx', '.xls')):
                # Read Excel and convert to CSV format in memory
                df_excel = pd.read_excel(uploaded_file)
                uploaded_file.seek(0)  # Reset file pointer
                # Use the dataframe directly (as if it came from CSV)
                df = df_excel
            else:  # CSV
                df = pd.read_csv(uploaded_file)
                uploaded_file.seek(0)  # Reset file pointer
            
            files_info.append({
                "name": uploaded_file.name.rsplit('.', 1)[0],
                "columns": len(df.columns),
                "rows": len(df),
                "file": uploaded_file,
                "df": df
            })
        except Exception as e:
            files_info.append({
                "name": uploaded_file.name.rsplit('.', 1)[0],
                "columns": 0,
                "rows": 0,
                "file": uploaded_file,
                "df": None,
                "error": str(e)
            })
    
    return files_info

def get_table_preview(file_path: Path, n_rows: int = 5) -> pd.DataFrame:
    """Get a preview of a CSV file.
    
    Args:
        file_path: Path to the CSV file.
        n_rows: Number of rows to preview.
    
    Returns:
        DataFrame with the first n_rows of the file.
    """
    try:
        return pd.read_csv(file_path, nrows=n_rows)
    except Exception:
        return pd.DataFrame()

def get_metadata_shared_info() -> List[Tuple[str, bool]]:
    """Get list of metadata types and whether they are shared with agents.
    
    Returns:
        List of tuples (description, is_shared).
    """
    return [
        ("Table & column names", True),
        ("Data types", True),
        ("Relationships & foreign keys", True),
        ("Row counts", True),
        ("Min / Max / Aggregates", True),
        ("Null counts & unique values", True),
        ("Raw data values", False),
        ("Personal or sensitive data", False),
    ]

# =============================================================================
# AGENT DEFINITIONS
# =============================================================================

AGENTS = [
    {
        "title": "Schema Interpreter",
        "icon": "",
        "color": "#38bdf8",  # cyan
        "description": "Interprets dataset metadata to summarize tables, fields, types and relationships."
    },
    {
        "title": "Business Analyst",
        "icon": "",
        "color": "#a78bfa",  # purple
        "description": "Builds a structured analysis grid from metadata with axes and sub-analyses."
    },
    {
        "title": "Query Builder",
        "icon": "",
        "color": "#fbbf24",  # amber
        "description": "Converts the analysis grid into query specifications with joins, filters and groupings."
    },
    {
        "title": "Visualization Designer",
        "icon": "",
        "color": "#34d399",  # emerald
        "description": "Creates meaningful and informative visualizations from computed results."
    },
    {
        "title": "Confidentiality Tester",
        "icon": "",
        "color": "#f87171",  # red
        "description": "Validates that agents only access metadata and never expose actual data values."
    },
]

# Mono-agent definition
MONO_AGENT = {
    "title": "Full-Stack Analyst",
    "icon": "",
    "color": "#38bdf8",  # purple
    "description": "Single agent that performs the full pipeline in one pass: interprets dataset metadata, defines analysis axes and sub-analyses, converts them into executable query specifications and creates meaningful dashboards and visualizations from the computed results."
}

# =============================================================================
# RENDER FUNCTIONS
# =============================================================================

def render_mode_selection():
    """Render the mode selection tabs (New Analysis vs Load Saved)."""
    saved_analyses = get_saved_analyses()
    has_saved = len(saved_analyses) > 0
    
    # Initialize mode in session state
    if "landing_mode" not in st.session_state:
        st.session_state.landing_mode = "new"
    
    st.markdown("""
        <div style="text-align: center; margin-bottom: 0rem;">
        <p style="color: #94a3b8; font-size: 1.1rem; margin-bottom: 0rem;">Choose an option</p>
        </div>
            """, unsafe_allow_html=True
    )
    
    # Two columns for mode selection
    col1, col2 = st.columns(2)
    
    is_new_mode = st.session_state.landing_mode == "new"
    is_load_mode = st.session_state.landing_mode == "load"
    
    with col1:
        border_color = "rgba(56, 189, 248, 0.7)" if is_new_mode else "rgba(71, 85, 105, 0.3)"
        bg_opacity = "0.15" if is_new_mode else "0.05"
        
        # Add dynamic styling for active state
        st.markdown(f"""
        <style>
        [data-testid="column"]:first-of-type button[data-testid="stBaseButton-{'primary' if is_new_mode else 'secondary'}"] {{
            background: linear-gradient(145deg, rgba(30, 41, 59, 0.5) 0%, rgba(56, 189, 248, {bg_opacity}) 100%) !important;
            border: 2px solid {border_color} !important;
        }}
        </style>
        <script>
        setTimeout(function() {{
            const btn = document.querySelector('.st-key-select_new_mode button');
            if (btn) {{
                btn.addEventListener('mouseenter', function() {{
                    this.style.borderColor = 'rgba(56, 189, 248, 0.8)';
                    this.style.filter = 'none';
                    this.style.color = '#f1f5f9';
                    const textElements = this.querySelectorAll('*');
                    textElements.forEach(el => el.style.color = '#f1f5f9');
                }});
                btn.addEventListener('mouseleave', function() {{
                    this.style.borderColor = '';
                    this.style.filter = '';
                    this.style.color = '';
                    const textElements = this.querySelectorAll('*');
                    textElements.forEach(el => el.style.color = '');
                }});
                // Disable all click effects
                btn.addEventListener('mousedown', function(e) {{
                    this.style.transform = 'none';
                    this.style.boxShadow = 'none';
                    this.style.filter = 'none';
                    this.style.outline = 'none';
                }});
                btn.addEventListener('mouseup', function() {{
                    this.style.transform = 'none';
                    this.style.boxShadow = 'none';
                    this.style.filter = 'none';
                    this.style.outline = 'none';
                }});
                btn.addEventListener('click', function() {{
                    this.style.transform = 'none';
                    this.style.boxShadow = 'none';
                    this.style.filter = 'none';
                    this.style.outline = 'none';
                }});
                btn.addEventListener('focus', function() {{
                    this.style.outline = 'none';
                    this.style.transform = 'none';
                    this.style.boxShadow = 'none';
                }});
                btn.addEventListener('blur', function() {{
                    this.style.outline = 'none';
                }});
            }}
        }}, 100);
        </script>
        """, unsafe_allow_html=True)
        
        if st.button(
            "\n\n**New Analysis**\n\nStart a new analysis on your data",
            key="select_new_mode",
            use_container_width=True,
            type="primary" if is_new_mode else "secondary"
        ):
            st.session_state.landing_mode = "new"
            # Reset load-related state
            st.session_state.pop("selected_saved_analysis", None)
            st.rerun()
    
    with col2:
        border_color = "rgba(167, 139, 250, 0.7)" if is_load_mode else "rgba(71, 85, 105, 0.3)"
        bg_opacity = "0.15" if is_load_mode else "0.05"
        disabled_opacity = "0.5" if not has_saved else "1"
        
        # Add dynamic styling for active state
        st.markdown(f"""
        <style>
        [data-testid="column"]:nth-of-type(2) button[data-testid="stBaseButton-{'primary' if is_load_mode else 'secondary'}"] {{
            background: linear-gradient(145deg, rgba(30, 41, 59, 0.5) 0%, rgba(167, 139, 250, {bg_opacity}) 100%) !important;
            border: 2px solid {border_color} !important;
            opacity: {disabled_opacity} !important;
        }}
        </style>
        <script>
        setTimeout(function() {{
            const btn = document.querySelector('.st-key-select_load_mode button');
            if (btn && !btn.disabled) {{
                btn.addEventListener('mouseenter', function() {{
                    this.style.borderColor = 'rgba(167, 139, 250, 0.8)';
                    this.style.filter = 'none';
                    this.style.color = '#f1f5f9';
                    const textElements = this.querySelectorAll('*');
                    textElements.forEach(el => el.style.color = '#f1f5f9');
                }});
                btn.addEventListener('mouseleave', function() {{
                    this.style.borderColor = '';
                    this.style.filter = '';
                    this.style.color = '';
                    const textElements = this.querySelectorAll('*');
                    textElements.forEach(el => el.style.color = '');
                }});
                // Disable all click effects
                btn.addEventListener('mousedown', function(e) {{
                    this.style.transform = 'none';
                    this.style.boxShadow = 'none';
                    this.style.filter = 'none';
                    this.style.outline = 'none';
                }});
                btn.addEventListener('mouseup', function() {{
                    this.style.transform = 'none';
                    this.style.boxShadow = 'none';
                    this.style.filter = 'none';
                    this.style.outline = 'none';
                }});
                btn.addEventListener('click', function() {{
                    this.style.transform = 'none';
                    this.style.boxShadow = 'none';
                    this.style.filter = 'none';
                    this.style.outline = 'none';
                }});
                btn.addEventListener('focus', function() {{
                    this.style.outline = 'none';
                    this.style.transform = 'none';
                    this.style.boxShadow = 'none';
                }});
                btn.addEventListener('blur', function() {{
                    this.style.outline = 'none';
                }});
            }}
        }}, 100);
        </script>
        """, unsafe_allow_html=True)
        
        if st.button(
            f"\n\n**Load Analysis**\n\nLoad and consult previously saved analyses",
            key="select_load_mode",
            use_container_width=True,
            type="primary" if is_load_mode else "secondary",
            disabled=not has_saved
        ):
            st.session_state.landing_mode = "load"
            st.rerun()
    
    st.markdown('<div style="height: 2rem;"></div>', unsafe_allow_html=True)


def render_saved_analyses():
    """Render the saved analyses selection section."""
    saved_analyses = get_saved_analyses()
    
    if not saved_analyses:
        st.info("No saved analyses")
        return
    
    # Use only names for selectbox
    analysis_names = [a["name"] for a in saved_analyses]
    
    # Create two columns: title on left, selectbox on right
    col_title, col_select = st.columns([1.5, 2])
    
    with col_title:
        st.markdown(f"""
            <div style="font-size: 1.1rem; font-weight: 600; color: #f1f5f9; margin: 0; display: flex; align-items: center; height: 100%; padding-top: 0.75rem;">📂 Saved Analyses ({len(saved_analyses)})</div>
                """, unsafe_allow_html=True
        )
    
    with col_select:
        # Selectbox for saved analyses (names only)
        selected_name = st.selectbox(
            "Select an analysis",
            options=analysis_names,
            key="saved_analysis_select",
            label_visibility="collapsed"
        )
    
    # Find selected analysis
    selected_analysis = next((a for a in saved_analyses if a["name"] == selected_name), saved_analyses[0])
    
    # Store selected analysis in session state
    st.session_state.selected_saved_analysis = selected_name
    
    # Format date
    try:
        date_str = datetime.fromisoformat(selected_analysis["date"]).strftime("%d/%m/%Y %H:%M")
    except:
        date_str = selected_analysis.get("date", "N/A")
    
    # Get pipeline mode and OpenAI model from metadata file if available
    from data_analysis.system.utils import get_analysis_metadata
    full_metadata = get_analysis_metadata(selected_name)
    pipeline_mode = full_metadata.get("pipeline_mode", "multi") if full_metadata else "multi"
    pipeline_mode_display = "Multi-Agent" if pipeline_mode == "multi" else "Mono-Agent"
    openai_model = full_metadata.get("openai_model", "gpt-4o") if full_metadata else "gpt-4o"
    
    # Display metadata in full width below - improved styling
    st.markdown(f"""
        <div style="background: linear-gradient(145deg, rgba(15, 23, 42, 0.7) 0%, rgba(30, 41, 59, 0.5) 100%); border: 1px solid rgba(71, 85, 105, 0.4); border-radius: 12px; padding: 0.75rem 1.5rem; margin-top: 0.rem; margin-bottom: 0.5rem;">
        <div style="display: flex; flex-direction: row; gap: 2.5rem; flex-wrap: wrap; align-items: center; justify-content: flex-start;">
        <div style="display: flex; align-items: center;">
        <span style="color: #94a3b8; font-size: 0.875rem; font-weight: 500;">Dataset:</span>
        <span style="color: #e2e8f0; font-size: 0.95rem; margin-left: 0.75rem; font-weight: 400;">{selected_analysis.get('dataset', 'N/A')}</span>
        </div>
        <div style="display: flex; align-items: center;">
        <span style="color: #94a3b8; font-size: 0.875rem; font-weight: 500;">Source:</span>
        <span style="color: #e2e8f0; font-size: 0.95rem; margin-left: 0.75rem; font-weight: 400;">{selected_analysis.get('source', 'N/A')}</span>
        </div>
        <div style="display: flex; align-items: center;">
        <span style="color: #94a3b8; font-size: 0.875rem; font-weight: 500;">Date:</span>
        <span style="color: #e2e8f0; font-size: 0.95rem; margin-left: 0.75rem; font-weight: 400;">{date_str}</span>
        </div>
        <div style="display: flex; align-items: center;">
        <span style="color: #94a3b8; font-size: 0.875rem; font-weight: 500;">Pipeline mode:</span>
        <span style="color: #e2e8f0; font-size: 0.95rem; margin-left: 0.75rem; font-weight: 400;">{pipeline_mode_display}</span>
        </div>
        <div style="display: flex; align-items: center;">
        <span style="color: #94a3b8; font-size: 0.875rem; font-weight: 500;">OpenAI Model:</span>
        <span style="color: #e2e8f0; font-size: 0.95rem; margin-left: 0.75rem; font-weight: 400;">{openai_model}</span>
        </div>
        </div>
        </div>
            """, unsafe_allow_html=True
    )
    
    # Action buttons - side by side in same container, spaced with CSS
    st.markdown("""
        <div id="saved-analysis-buttons-container" style="display: flex; align-items: center; gap: 0.75rem; margin-top: 1rem;">
    """, unsafe_allow_html=True)
    
    if st.button("Load Analysis", key="load_saved_btn", type="primary", use_container_width=False):
        # Load the analysis
        success, pipeline_mode = load_analysis(selected_name)
        if success:
            st.session_state.is_view_mode = True
            st.session_state.loaded_analysis_name = selected_name
            st.session_state.pipeline_mode = pipeline_mode
            st.session_state.active_section = "raw_schema"
            st.session_state.current_page = "analysis"
            st.rerun()
        else:
            st.error("Error loading analysis")
    
    if st.button("Delete", key="delete_saved_btn", type="secondary", use_container_width=False):
        st.session_state.confirm_delete = selected_name
        st.rerun()
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Confirmation dialog for delete
    if st.session_state.get("confirm_delete") == selected_name:
        st.warning(f"⚠️ Are you sure you want to delete the analysis « {selected_name} »?")
        col_yes, col_no = st.columns(2)
        with col_yes:
            if st.button("✓ Yes, delete", key="confirm_delete_yes", type="primary", use_container_width=True):
                if delete_analysis(selected_name):
                    st.session_state.pop("confirm_delete", None)
                    st.session_state.pop("selected_saved_analysis", None)
                    st.success("Analysis deleted")
                    st.rerun()
                else:
                    st.error("Error during deletion")
        with col_no:
            if st.button("✗ Cancel", key="confirm_delete_no", type="secondary", use_container_width=True):
                st.session_state.pop("confirm_delete", None)
                st.rerun()


def render_hero():
    """Render the hero section with inline styles."""
    st.markdown("""
        <div style="text-align: center; margin-bottom: 0rem; padding: 0rem 1rem 2rem 1rem;">
        <h1 style="font-size: 2.8rem; font-weight: 700; background: linear-gradient(135deg, #38bdf8 0%, #22c55e 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text; margin: 0 0 0rem 0; letter-spacing: -0.03em;">Confidential AI Data Analysis</h1>
<p style="font-size: 1.15rem; color: #94a3b8; line-height: 1.7; max-width: 700px; margin: 0 auto 1.5rem auto;">Automated data analysis powered by a team of specialized AI agents.<br><span style="color: #64748b;">Raw data never leaves your infrastructure.</span></p>
<span style="display: inline-flex; align-items: center; gap: 0.5rem; padding: 0.7rem 1.4rem; border-radius: 999px; background: linear-gradient(135deg, rgba(56, 189, 248, 0.12) 0%, rgba(34, 197, 94, 0.08) 100%); color: #38bdf8; font-size: 0.9rem; font-weight: 500; border: 1px solid rgba(56, 189, 248, 0.25); box-shadow: 0 4px 15px rgba(56, 189, 248, 0.1);">🔒 Metadata-only · On-prem execution · Privacy by design</span>
        </div>
                    """, unsafe_allow_html=True
    )
    
    # Settings section below badge, centered
    render_settings()

def render_settings():
    """Render the settings section with pipeline mode selection in an expander."""
    # Initialize pipeline mode in session state
    if "pipeline_mode" not in st.session_state:
        st.session_state.pipeline_mode = "multi"
    
    # Initialize OpenAI API key and model in session state
    if "openai_api_key" not in st.session_state:
        st.session_state.openai_api_key = ""
    if "openai_model" not in st.session_state:
        st.session_state.openai_model = "gpt-4o"
    
    # Clear any pipeline error when arriving on landing page (errors are shown on analysis page only)
    if "pipeline_error" in st.session_state:
        st.session_state.pipeline_error = None
    
    # Center the expander below the badge using a container
    st.markdown("""
    <div style="display: flex; justify-content: center; width: 100%; margin: 1.5rem 0;">
</div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        with st.expander("⚙️ Settings", expanded=False):
            # OpenAI API Configuration Section
            st.markdown("### OpenAI Configuration")
            
            # API Key input - normal text field
            api_key = st.text_input(
                "OpenAI API Key",
                value=st.session_state.openai_api_key,
                key="openai_api_key_input",
                help="Enter your OpenAI API key. This will be used for all AI agents.",
                label_visibility="visible"
            )
            # Update session state from widget value
            if "openai_api_key_input" in st.session_state:
                st.session_state.openai_api_key = st.session_state.openai_api_key_input
            
            # Model selection - (platform.openai.com/docs/models)
            openai_models = [
                "gpt-4o",
                "gpt-5.2",
                "gpt-5-mini",
                "gpt-5-nano",
                "gpt-5.2-pro",
                "gpt-5",
                "gpt-4.1",
                "gpt-4.1-mini",
                "gpt-4.1-nano",
                "gpt-4o-mini",
                "gpt-4-turbo",
                "gpt-4",
                "gpt-3.5-turbo",
            ]
            
            # Initialize the selectbox key if it doesn't exist
            if "openai_model_select" not in st.session_state:
                # Use current model if valid, otherwise default to first
                current_model = st.session_state.openai_model
                if current_model in openai_models:
                    st.session_state.openai_model_select = current_model
                else:
                    st.session_state.openai_model_select = openai_models[0]
                    st.session_state.openai_model = openai_models[0]
            
            # Use selectbox with key - Streamlit manages the state
            selected_model = st.selectbox(
                "OpenAI Model",
                options=openai_models,
                key="openai_model_select",
                help="Select the OpenAI model to use for analysis."
            )
            
            # Sync session state with widget value
            st.session_state.openai_model = st.session_state.openai_model_select
            
            # Divider
            st.markdown("---")
            
            # Pipeline Mode Selection Section
            st.markdown("### Pipeline Mode")
            
            # Two columns for mode selection
            mode_col1, mode_col2 = st.columns(2)
            
            is_multi = st.session_state.pipeline_mode == "multi"
            is_mono = st.session_state.pipeline_mode == "mono"
            
            with mode_col1:
                if st.button(
                    "\n**Multi-Agent**\n\n4 specialized agents working in sequence for detailed analysis",
                    key="select_multi_mode",
                    use_container_width=True,
                    type="primary" if is_multi else "secondary"
                ):
                    st.session_state.pipeline_mode = "multi"
                    st.rerun()
            
            with mode_col2:
                if st.button(
                    "\n**Mono-Agent**\n\nSingle agent for faster results in one LLM call",
                    key="select_mono_mode",
                    use_container_width=True,
                    type="primary" if is_mono else "secondary"
                ):
                    st.session_state.pipeline_mode = "mono"
                    st.rerun()

def render_agents():
    """Render the agents cards using Streamlit columns for reliability."""
    
    # Check pipeline mode
    is_mono = st.session_state.get("pipeline_mode", "multi") == "mono"
    
    if is_mono:
        # Mono-agent mode: show single large card centered
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col2:
            agent = MONO_AGENT
            color = agent['color']
            st.markdown(f"""
                <div style="background: linear-gradient(145deg, rgba(30, 41, 59, 0.8) 0%, rgba(15, 23, 42, 0.95) 100%); border-radius: 16px; padding: 1.5rem; border: 1px solid {color}40; box-shadow: 0 4px 20px rgba(0,0,0,0.3); position: relative; overflow: hidden; text-align: center; min-height: 180px;">
                <div style="position: absolute; top: 0; left: 0; right: 0; height: 3px; background: linear-gradient(90deg, transparent, {color}, transparent); opacity: 0.7;"></div>
                <div style="font-size: 2rem; margin-bottom: 0.8rem;">{agent['icon']}</div>
                <div style="font-size: 1.1rem; font-weight: 600; color: #f1f5f9; margin-bottom: 0.6rem;">{agent['title'].replace(' ', '<br>')}</div>
                <div style="font-size: 0.88rem; color: #94a3b8; line-height: 1.55;">{agent['description']}</div>
                </div>
                            """, unsafe_allow_html=True
            )
    else:
        # Multi-agent mode: show 5 agent cards
        cols = st.columns(5)
        
        for idx, agent in enumerate(AGENTS):
            with cols[idx]:
                color = agent['color']
                st.markdown(f"""
<div style="background: linear-gradient(145deg, rgba(30, 41, 59, 0.8) 0%, rgba(15, 23, 42, 0.95) 100%); border-radius: 16px; padding: 1.5rem; border: 1px solid {color}40; box-shadow: 0 4px 20px rgba(0,0,0,0.3); position: relative; overflow: hidden; min-height: 180px;">
<div style="position: absolute; top: 0; left: 0; right: 0; height: 3px; background: linear-gradient(90deg, transparent, {color}, transparent); opacity: 0.7;"></div>
<div style="font-size: 2rem; margin-bottom: 0.8rem;">{agent['icon']}</div>
<div style="font-size: 1.1rem; font-weight: 600; color: #f1f5f9; margin-bottom: 0.6rem;">{agent['title'].replace(' ', '<br>')}</div>
<div style="font-size: 0.88rem; color: #94a3b8; line-height: 1.55;">{agent['description']}</div>
</div>
                                        """, unsafe_allow_html=True
                    )
    
    # Vertical spacing after agents section
    st.markdown('<div style="height: 2.5rem;"></div>', unsafe_allow_html=True)

def render_data_source():
    """Render the data source selection section."""
    folders = get_available_csv_folders()
    
    # Get current selection from session state
    current_folder = st.session_state.get(
        "selected_csv_folder", 
        folders[0] if folders else None
    )
    
    # Initialize uploaded files state
    if "uploaded_files" not in st.session_state:
        st.session_state.uploaded_files = None
    
    # 3 columns: Upload | OR | Existing
    col1, col_or, col2 = st.columns([5, 1, 5])
    
    # Use session state to track uploads for border color (will be updated after file_uploader)
    # Check current file_uploader value via session state key
    uploaded_files_key = "file_uploader"
    is_validated = st.session_state.get("data_validated", False)
    
    with col1:
        # Green border when files are uploaded, normal otherwise
        # We check session state which gets updated on rerun
        has_uploads = st.session_state.get("use_uploaded_files", False)
        border_color_upload = "rgba(34, 197, 94, 0.6)" if has_uploads else "rgba(71, 85, 105, 0.3)"
        opacity_upload = "0.5" if is_validated else "1"
        
        st.markdown(f"""
<div style="background: linear-gradient(145deg, rgba(30, 41, 59, 0.5) 0%, rgba(15, 23, 42, 0.85) 100%); border: 2px solid {border_color_upload}; border-radius: 16px; padding: 1rem; opacity: {opacity_upload};">
<div style="text-align: center; margin-bottom: 0.5rem;">
<div style="font-size: 2rem; margin-bottom: 0.3rem;">📁</div>
<div style="font-size: 1.1rem; font-weight: 600; color: #f1f5f9; margin-bottom: 0.2rem;">Upload a dataset</div>
<div style="font-size: 0.85rem; color: #64748b;">Drag & drop CSV or Excel files</div>
</div>
</div>
                    """, unsafe_allow_html=True
        )
        
        uploaded_files = st.file_uploader(
            "Upload CSV or Excel files",
            type=["csv", "xlsx", "xls"],
            accept_multiple_files=True,
            key=uploaded_files_key,
            label_visibility="collapsed",
            disabled=is_validated
        )
        
        # Update session state based on current upload state (only if not validated)
        if not is_validated:
            current_has_uploads = uploaded_files is not None and len(uploaded_files) > 0
            prev_uploads = st.session_state.get("uploaded_files")
            
            if current_has_uploads:
                if prev_uploads is None or len(prev_uploads) != len(uploaded_files):
                    st.session_state.data_validated = False
                st.session_state.uploaded_files = uploaded_files
                st.session_state.use_uploaded_files = True
                st.success(f"✓ {len(uploaded_files)} file(s) selected")
            else:
                if prev_uploads is not None:
                    st.session_state.data_validated = False
                st.session_state.uploaded_files = None
                st.session_state.use_uploaded_files = False
            
            # Rerun if state changed to update border colors
            if current_has_uploads != has_uploads:
                st.rerun()
        elif has_uploads:
            st.success(f"✓ {len(st.session_state.uploaded_files)} file(s) selected")
    
    with col_or:
        # Big OR separator
        st.markdown("""
<div style="display: flex; flex-direction: column; align-items: center; justify-content: center; height: 100%;">
<div style="width: 2px; height: 40px; background: linear-gradient(180deg, transparent, rgba(71, 85, 105, 0.5), rgba(71, 85, 105, 0.5));"></div>
<div style="font-size: 1rem; font-weight: 700; color: #64748b; padding: 0.5rem 0; text-transform: uppercase; letter-spacing: 0.1em;">OR</div>
<div style="width: 2px; height: 40px; background: linear-gradient(180deg, rgba(71, 85, 105, 0.5), rgba(71, 85, 105, 0.5), transparent);"></div>
</div>
                    """, unsafe_allow_html=True
        )
    
    with col2:
        # Green border when NO uploads (existing dataset is the active choice), normal otherwise
        # Use session state for consistency
        has_uploads_state = st.session_state.get("use_uploaded_files", False)
        border_color_existing = "rgba(34, 197, 94, 0.6)" if not has_uploads_state and folders else "rgba(71, 85, 105, 0.3)"
        # Disable if validated OR if uploads are selected
        opacity_existing = "0.5" if is_validated or has_uploads_state else "1"
        
        if folders:
            st.markdown(f"""
<div style="background: linear-gradient(145deg, rgba(30, 41, 59, 0.5) 0%, rgba(15, 23, 42, 0.85) 100%); border: 2px solid {border_color_existing}; border-radius: 16px; padding: 1rem; opacity: {opacity_existing};">
<div style="text-align: center; margin-bottom: 0.5rem;">
<div style="font-size: 2rem; margin-bottom: 0.3rem;">🗃️</div>
<div style="font-size: 1.1rem; font-weight: 600; color: #f1f5f9; margin-bottom: 0.2rem;">Use an existing dataset</div>
<div style="font-size: 0.85rem; color: #64748b;">Select from available datasets</div>
</div>
</div>
                            """, unsafe_allow_html=True
            )
            
            selected = st.selectbox(
                "Select a dataset folder",
                options=folders,
                index=folders.index(current_folder) if current_folder in folders else 0,
                key="csv_folder_select",
                label_visibility="collapsed",
                disabled=has_uploads_state or is_validated
            )
            
            if not is_validated and selected != st.session_state.get("selected_csv_folder"):
                st.session_state.selected_csv_folder = selected
                st.session_state.data_validated = False  # Reset validation on change
        else:
            st.warning("No test datasets found in test_data/")
    
    # Validation button section
    st.markdown('<div style="height: 1rem;"></div>', unsafe_allow_html=True)
    
    # Check if we have something to validate
    has_uploads = st.session_state.get("use_uploaded_files", False)
    has_existing = not has_uploads and folders
    can_validate = has_uploads or has_existing
    is_validated = st.session_state.get("data_validated", False)
    
    if can_validate:
        if is_validated:
            # Show validated state badge + change button on same line
            col_btn1, col_btn2, col_btn3, col_btn4 = st.columns([2.5, 1.2, 1.2, 2.5])
            with col_btn2:
                st.markdown("""
<div style="display: flex; align-items: center; justify-content: center; padding: 0.55rem 1rem; background: rgba(34, 197, 94, 0.15); border: 1px solid rgba(34, 197, 94, 0.4); border-radius: 8px;">
<span style="color: #22c55e; font-weight: 600; font-size: 0.9rem;">✓ Dataset validated</span>
</div>
                                    """, unsafe_allow_html=True
                )
            
            with col_btn3:
                if st.button("Change selection", key="change_selection_btn", type="secondary", use_container_width=True):
                    st.session_state.data_validated = False
                    st.rerun()
        else:
            # Show validate button centered
            col_v1, col_v2, col_v3 = st.columns([3, 1.6, 3])
            with col_v2:
                if st.button("Validate dataset", key="validate_dataset_btn", type="primary", use_container_width=True):
                    st.session_state.data_validated = True
                    # Store validated data info
                    if has_uploads:
                        st.session_state.validated_files_info = get_uploaded_files_info(st.session_state.uploaded_files)
                        st.session_state.validated_source = "uploaded"
                    else:
                        st.session_state.validated_files_info = get_csv_files_info(st.session_state.get("selected_csv_folder", "test"))
                        st.session_state.validated_source = "existing"
                    st.rerun()
    
    # Vertical spacing after data source section
    st.markdown('<div style="height: 1.5rem;"></div>', unsafe_allow_html=True)

def render_preview_panels():
    """Render the data overview and metadata panels."""
    is_validated = st.session_state.get("data_validated", False)
    validated_source = st.session_state.get("validated_source", None)
    files_info = st.session_state.get("validated_files_info", [])
    metadata_info = get_metadata_shared_info()
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
<div style="background: linear-gradient(145deg, rgba(30, 41, 59, 0.5) 0%, rgba(15, 23, 42, 0.85) 100%); border: 1px solid rgba(71, 85, 105, 0.3); border-radius: 10px; padding: 0.8rem 1rem; margin-bottom: 0.5rem;">
<div style="font-size: 1.8rem; font-weight: 600; color: #f1f5f9; margin: 0;">Dataset overview</div>
</div>
                    """, unsafe_allow_html=True
        )
        
        if not is_validated:
            # Show prompt to validate
            st.markdown("""
<div style="padding: 2rem 1rem; text-align: center; background: rgba(15, 23, 42, 0.4); border-radius: 10px; border: 1px dashed rgba(71, 85, 105, 0.5);">
<p style="color: #64748b; font-size: 0.95rem; margin: 0;">Select a data source above and click <strong style="color: #38bdf8;">Validate dataset</strong> to preview</p>
</div>
                            """, unsafe_allow_html=True
            )
        elif files_info:
            # Label for table selector
            st.markdown('<p style="color: #94a3b8; font-size: 0.9rem; margin-bottom: 0.3rem;">Choose a table to preview</p>', unsafe_allow_html=True)
            
            # Table preview selector with rows/cols info
            def format_table_option(file_info):
                rows = file_info.get('rows', 0)
                cols = file_info.get('columns', 0)
                rows_display = f"{rows:,}" if isinstance(rows, int) else str(rows)
                return f"{file_info['name']} ({rows_display} rows · {cols} cols)"
            
            table_options = [format_table_option(f) for f in files_info]
            table_names = [f["name"] for f in files_info]
            
            selected_option = st.selectbox(
                "Preview table",
                options=table_options,
                key="preview_table_select",
                label_visibility="collapsed"
            )
            
            # Get selected table name from option
            selected_idx = table_options.index(selected_option) if selected_option in table_options else 0
            
            # Show preview
            selected_info = files_info[selected_idx] if files_info else None
            if selected_info:
                # Get preview - either from stored df (uploaded) or from file path (existing)
                if "df" in selected_info and selected_info["df"] is not None:
                    preview_df = selected_info["df"].head(5)
                elif "path" in selected_info:
                    preview_df = get_table_preview(selected_info["path"])
                else:
                    preview_df = pd.DataFrame()
                
                if not preview_df.empty:
                    # Calculate height based on rows: header (~35px) + rows (~35px each)
                    num_rows = len(preview_df)
                    fixed_height = 35 + (num_rows * 35) + 10  # header + rows + padding
                    st.dataframe(
                        preview_df,
                        use_container_width=True,
                        hide_index=True,
                        height=fixed_height
                    )
        else:
            st.markdown('<p style="color: #64748b; font-size: 0.9rem;">No tables found</p>', unsafe_allow_html=True)
    
    with col2:
        # Build the metadata list HTML
        metadata_html = ""
        for info_text, is_shared in metadata_info:
            if is_shared:
                icon = '<span style="color: #22c55e; font-weight: 600;">✓</span>'
            else:
                icon = '<span style="color: #ef4444; font-weight: 600;">✗</span>'
            
            metadata_html += f'<div style="padding: 0.5rem 0; font-size: 0.95rem; color: #cbd5e1; display: flex; align-items: center; gap: 0.6rem;">{icon} {info_text}</div>'
        
        st.markdown(f"""
<div style="background: linear-gradient(145deg, rgba(30, 41, 59, 0.5) 0%, rgba(15, 23, 42, 0.85) 100%); border: 1px solid rgba(71, 85, 105, 0.3); border-radius: 16px; padding: 0.8rem;">
<div style="font-size: 1.15rem; font-weight: 600; color: #f1f5f9; margin-bottom: 1rem;">Information shared with agents</div>
{metadata_html}
</div>
                    """, unsafe_allow_html=True
        )


def render_analysis_name_input():
    """Render the analysis name input field with validation."""
    is_validated = st.session_state.get("data_validated", False)
    
    if not is_validated:
        return False  # Name input only shown after data validation
    
    st.markdown("""
        <div style="background: linear-gradient(145deg, rgba(30, 41, 59, 0.5) 0%, rgba(15, 23, 42, 0.85) 100%); border: 1px solid rgba(56, 189, 248, 0.3); border-radius: 16px; padding: 1rem 1rem 0.75rem 1rem; margin: 0.5rem 0 0 0;">
        <div style="font-size: 1.30rem; font-weight: 600; color: #f1f5f9; margin-bottom: 0.15rem;">Analysis Name</div>
        <div style="font-size: 1rem; color: #64748b; margin-bottom: 0.5rem;">Give your analysis a unique name to find it easily</div>
        </div>
            """, unsafe_allow_html=True
    )
    
    # Initialize widget state if it doesn't exist
    # When using a key, Streamlit manages the value automatically
    # We sync with our custom session state key for consistency
    if "analysis_name_input" not in st.session_state:
        # Initialize from our custom key if it exists, otherwise empty string
        initial_value = st.session_state.get("analysis_name", "")
        st.session_state.analysis_name_input = initial_value
    else:
        # Sync our custom key with the widget's state
        st.session_state.analysis_name = st.session_state.analysis_name_input
    
    # Text input for analysis name
    # Don't use value parameter when key is provided - let Streamlit manage it
    analysis_name = st.text_input(
        "Analysis Name",
        placeholder="Ex: Sales Analysis Q4 2024",
        key="analysis_name_input",
        label_visibility="collapsed",
        max_chars=50
    )
    
    # Always sync widget value with our custom session state key
    st.session_state.analysis_name = st.session_state.analysis_name_input
    
    # Validate name (session state already synced above) — show message right under input
    validation = validate_analysis_name(analysis_name)
    
    if analysis_name:
        if validation["valid"]:
            st.markdown("""
                <div style="display: inline-flex; align-items: center; gap: 0.4rem; padding: 0.35rem 0.65rem; margin-top: 0.25rem; background: rgba(34, 197, 94, 0.12); border: 1px solid rgba(34, 197, 94, 0.35); border-radius: 8px;">
                <span style="color: #22c55e; font-size: 0.8rem;">✓</span>
                <span style="color: #22c55e; font-size: 0.85rem; font-weight: 500;">Name available</span>
                </div>
            """, unsafe_allow_html=True)
        else:
            # Do not show "An analysis with this name already exists" — only "Name not available"
            err = validation["error"]
            show_detail = err and err != "An analysis with this name already exists"
            detail_html = f' <span style="color: #f87171; font-size: 0.8rem;">— {err}</span>' if show_detail else ""
            st.markdown(f"""
                <div style="display: inline-flex; align-items: center; gap: 0.4rem; padding: 0.35rem 0.65rem; margin-top: 0.25rem; background: rgba(239, 68, 68, 0.12); border: 1px solid rgba(239, 68, 68, 0.35); border-radius: 8px;">
                <span style="color: #ef4444; font-size: 0.8rem;">✗</span>
                <span style="color: #ef4444; font-size: 0.85rem; font-weight: 500;">Name not available</span>{detail_html}
                </div>
            """, unsafe_allow_html=True)
    
    # JavaScript to force blue border and remove red on focus
    st.markdown("""
        <script>
        function forceBlueBorder() {
            const input = document.querySelector('[data-testid="stTextInput"] input');
            if (input) {
                if (document.activeElement === input) {
                    input.style.setProperty('border-color', 'rgba(56, 189, 248, 1)', 'important');
                    input.style.setProperty('box-shadow', '0 0 0 4px rgba(56, 189, 248, 0.4)', 'important');
                    input.style.setProperty('outline', 'none', 'important');
                }
                input.addEventListener('focus', function() {
                    this.style.setProperty('border-color', 'rgba(56, 189, 248, 1)', 'important');
                    this.style.setProperty('box-shadow', '0 0 0 4px rgba(56, 189, 248, 0.4)', 'important');
                    this.style.setProperty('outline', 'none', 'important');
                });
                input.addEventListener('blur', function() {
                    this.style.setProperty('border-color', 'rgba(56, 189, 248, 0.3)', 'important');
                });
            }
        }
        setTimeout(forceBlueBorder, 100);
        setInterval(forceBlueBorder, 200);
        </script>
    """, unsafe_allow_html=True)
    
    return validation["valid"]


def render_cta():
    """Render the call-to-action button."""
    is_validated = st.session_state.get("data_validated", False)
    
    # Only show button if dataset is validated
    if not is_validated:
        return
    
    st.markdown("""
    <div style="text-align: center; padding: 2rem 0 3rem 0;">
    </div>
    """, unsafe_allow_html=True)
    
    # Check if analysis name is valid
    analysis_name = st.session_state.get("analysis_name", "").strip()
    name_validation = validate_analysis_name(analysis_name)
    
    # Check if OpenAI API key is provided
    api_key = st.session_state.get("openai_api_key", "").strip()
    has_api_key = bool(api_key)
    
    can_launch = name_validation["valid"] and has_api_key
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        # Show disabled reason if needed
        if not name_validation["valid"]:
            st.markdown("""
                <div style="text-align: center; margin-bottom: 0.5rem;">
                <span style="color: #fbbf24; font-size: 1.1rem;">⚠️ Please enter a valid analysis name</span>
                </div>
                            """, unsafe_allow_html=True
                )
        elif not has_api_key:
            st.markdown("""
                <div style="text-align: center; margin-bottom: 0.5rem;">
                <span style="color: #fbbf24; font-size: 1.1rem;">⚠️ Please enter your OpenAI API key in Settings</span>
                </div>
                            """, unsafe_allow_html=True
                )
        
        if st.button(
            "Launch Analysis",
            type="primary",
            use_container_width=True,
            key="launch_analysis_btn",
            disabled=not can_launch
        ):
            # Configure data source based on selection
            use_uploaded = st.session_state.get("use_uploaded_files", False)
            
            if use_uploaded:
                # Save uploaded files directly to current_analysis/data/
                uploaded_files = st.session_state.get("uploaded_files", [])
                if uploaded_files:
                    save_uploaded_files(uploaded_files)
                    dataset_name = "uploads"
            else:
                # Copy files from test_data/[folder]/ to current_analysis/data/
                selected_folder = st.session_state.get("selected_csv_folder", "test")
                source_folder = TEST_DATA_DIR / selected_folder
                if source_folder.exists():
                    # Clear and copy CSV files
                    if OUTPUT_DATA_DIR.exists():
                        shutil.rmtree(OUTPUT_DATA_DIR)
                    OUTPUT_DATA_DIR.mkdir(parents=True, exist_ok=True)
                    for csv_file in source_folder.glob("*.csv"):
                        shutil.copy2(csv_file, OUTPUT_DATA_DIR / csv_file.name)
                    dataset_name = selected_folder
                else:
                    dataset_name = "unknown"
            
            # Store analysis name and dataset info for saving later
            st.session_state.pending_analysis_name = analysis_name
            st.session_state.pending_analysis_dataset = dataset_name
            st.session_state.pending_analysis_source = "uploaded" if use_uploaded else "existing"
            st.session_state.is_view_mode = False
            st.session_state.active_section = "raw_schema"
            
            st.session_state.current_page = "analysis"
            st.rerun()

# =============================================================================
# MAIN RENDER FUNCTION
# =============================================================================

def render_landing_page():
    """Render the complete landing page with data source selection."""
    
    # Apply dark theme and global overrides for landing page
    st.markdown("""
    <style>
    /* ========== LANDING PAGE GLOBAL STYLES ========== */
    
    /* Dark background */
    .stApp, [data-testid="stAppViewContainer"], .main, [data-testid="stMain"] {
        background: radial-gradient(ellipse at top, #0f172a 0%, #020617 50%, #000 100%) !important;
    }
    
    /* Hide sidebar */
    [data-testid="stSidebar"] {
        display: none !important;
    }
        
        /* Hide Streamlit header menu */
        [data-testid="stHeader"] {
            display: none !important;
        }
        
        /* Mode selection button styling - make cards clickable */
        .mode-selection-button {
            background: linear-gradient(145deg, rgba(30, 41, 59, 0.5) 0%, rgba(56, 189, 248, 0.05) 100%) !important;
            border: 2px solid rgba(71, 85, 105, 0.3) !important;
            border-radius: 16px !important;
            padding: 1.2rem !important;
            height: auto !important;
            min-height: 100px !important;
            width: 100% !important;
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
            flex-direction: column !important;
            text-align: center !important;
            transition: all 0.3s ease !important;
        }
        
        .mode-selection-button:hover:not(:disabled) {
            transform: translateY(-2px) !important;
            box-shadow: 0 8px 25px rgba(56, 189, 248, 0.3) !important;
        }
        
        .mode-selection-button > div {
            display: flex !important;
            flex-direction: column !important;
            align-items: center !important;
            gap: 0.3rem !important;
    }
    
    /* CTA Button styling */
    button[data-testid="stBaseButton-primary"] {
        background: linear-gradient(135deg, #38bdf8 0%, #22c55e 100%) !important;
        color: #020617 !important;
        font-weight: 600 !important;
        font-size: 0.95rem !important;
        padding: 0.5rem 1.5rem !important;
        border: none !important;
        border-radius: 8px !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        box-shadow: 0 4px 20px rgba(56, 189, 248, 0.3) !important;
    }
    
    button[data-testid="stBaseButton-primary"]:hover {
        filter: brightness(1.1) !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 30px rgba(56, 189, 248, 0.4) !important;
    }
        
        /* OVERRIDE: Force mode selection primary buttons to have same height as secondary - MAXIMUM SPECIFICITY */
        [data-testid="column"]:first-of-type button[data-testid="stBaseButton-primary"],
        [data-testid="column"]:nth-of-type(2) button[data-testid="stBaseButton-primary"],
        .st-key-select_new_mode button[data-testid="stBaseButton-primary"],
        .st-key-select_load_mode button[data-testid="stBaseButton-primary"],
        .st-key-select_new_mode button[data-testid="stBaseButton-primary"]:not(:hover):not(:active):not(:focus),
        .st-key-select_load_mode button[data-testid="stBaseButton-primary"]:not(:hover):not(:active):not(:focus) {
            height: 100px !important;
            min-height: 100px !important;
            max-height: 100px !important;
            padding: 1.2rem !important;
            box-sizing: border-box !important;
        }
        
        /* Selected button style - colored border, white text, and neon glow */
        .st-key-select_new_mode button[data-testid="stBaseButton-primary"]:not(:hover):not(:active):not(:focus),
        .st-key-select_new_mode button[data-testid="stBaseButton-primary"]:hover:not(:disabled) {
            border-color: rgba(56, 189, 248, 0.8) !important;
            color: #f1f5f9 !important;
            box-shadow: 0 0 20px rgba(56, 189, 248, 0.5), 0 0 40px rgba(56, 189, 248, 0.3) !important;
        }
        
        .st-key-select_new_mode button[data-testid="stBaseButton-primary"]:not(:hover):not(:active):not(:focus) *,
        .st-key-select_new_mode button[data-testid="stBaseButton-primary"]:hover:not(:disabled) * {
            color: #f1f5f9 !important;
        }
        
        .st-key-select_load_mode button[data-testid="stBaseButton-primary"]:not(:hover):not(:active):not(:focus),
        .st-key-select_load_mode button[data-testid="stBaseButton-primary"]:hover:not(:disabled) {
            border-color: rgba(167, 139, 250, 0.8) !important;
            color: #f1f5f9 !important;
            box-shadow: 0 0 20px rgba(167, 139, 250, 0.5), 0 0 40px rgba(167, 139, 250, 0.3) !important;
        }
        
        .st-key-select_load_mode button[data-testid="stBaseButton-primary"]:not(:hover):not(:active):not(:focus) *,
        .st-key-select_load_mode button[data-testid="stBaseButton-primary"]:hover:not(:disabled) * {
            color: #f1f5f9 !important;
        }
        
        /* Mode selection buttons - make entire cards clickable - FORCE SAME HEIGHT */
        [data-testid="column"]:first-of-type button[data-testid^="stBaseButton"],
        [data-testid="column"]:nth-of-type(2) button[data-testid^="stBaseButton"],
        [data-testid="column"]:first-of-type button[data-testid="stBaseButton-primary"],
        [data-testid="column"]:first-of-type button[data-testid="stBaseButton-secondary"],
        [data-testid="column"]:nth-of-type(2) button[data-testid="stBaseButton-primary"],
        [data-testid="column"]:nth-of-type(2) button[data-testid="stBaseButton-secondary"],
        .st-key-select_new_mode button[data-testid="stBaseButton-primary"],
        .st-key-select_new_mode button[data-testid="stBaseButton-secondary"],
        .st-key-select_load_mode button[data-testid="stBaseButton-primary"],
        .st-key-select_load_mode button[data-testid="stBaseButton-secondary"] {
            background: linear-gradient(145deg, rgba(30, 41, 59, 0.5) 0%, rgba(56, 189, 248, 0.05) 100%) !important;
            border: 2px solid rgba(71, 85, 105, 0.3) !important;
            border-radius: 16px !important;
            padding: 1.2rem !important;
            height: 100px !important;
            min-height: 100px !important;
            max-height: 100px !important;
            width: 100% !important;
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
            flex-direction: column !important;
            text-align: center !important;
            transition: all 0.3s ease !important;
            box-sizing: border-box !important;
        }
        
        /* Hover effect for New Analysis button - simple border color change - KEEP HEIGHT - KEEP NEON GLOW - NO TRANSFORM */
        .st-key-select_new_mode button[data-testid="stBaseButton-primary"]:hover:not(:disabled) {
            border-color: rgba(56, 189, 248, 0.8) !important;
            filter: none !important;
            color: #f1f5f9 !important;
            height: 100px !important;
            min-height: 100px !important;
            max-height: 100px !important;
            box-shadow: 0 0 20px rgba(56, 189, 248, 0.5), 0 0 40px rgba(56, 189, 248, 0.3) !important;
            transform: none !important;
        }
        
        .st-key-select_new_mode button[data-testid="stBaseButton-secondary"]:hover:not(:disabled) {
            border-color: rgba(56, 189, 248, 0.8) !important;
            filter: none !important;
            color: #f1f5f9 !important;
            height: 100px !important;
            min-height: 100px !important;
            max-height: 100px !important;
            box-shadow: none !important;
            transform: none !important;
        }
        
        /* Hover effect for Load Analysis button - simple border color change - KEEP HEIGHT - KEEP NEON GLOW - NO TRANSFORM */
        .st-key-select_load_mode button[data-testid="stBaseButton-primary"]:hover:not(:disabled) {
            border-color: rgba(167, 139, 250, 0.8) !important;
            filter: none !important;
            color: #f1f5f9 !important;
            height: 100px !important;
            min-height: 100px !important;
            max-height: 100px !important;
            box-shadow: 0 0 20px rgba(167, 139, 250, 0.5), 0 0 40px rgba(167, 139, 250, 0.3) !important;
            transform: none !important;
        }
        
        .st-key-select_load_mode button[data-testid="stBaseButton-secondary"]:hover:not(:disabled) {
            border-color: rgba(167, 139, 250, 0.8) !important;
            filter: none !important;
            color: #f1f5f9 !important;
            height: 100px !important;
            min-height: 100px !important;
            max-height: 100px !important;
            box-shadow: none !important;
            transform: none !important;
        }
        
        /* Ensure text stays white on hover */
        .st-key-select_new_mode button[data-testid="stBaseButton-primary"]:hover:not(:disabled) *,
        .st-key-select_new_mode button[data-testid="stBaseButton-secondary"]:hover:not(:disabled) *,
        .st-key-select_load_mode button[data-testid="stBaseButton-primary"]:hover:not(:disabled) *,
        .st-key-select_load_mode button[data-testid="stBaseButton-secondary"]:hover:not(:disabled) * {
            color: #f1f5f9 !important;
        }
        
        /* Disable ALL click effects - active, focus, focus-visible states - KEEP HEIGHT */
        .st-key-select_new_mode button[data-testid="stBaseButton-primary"]:active,
        .st-key-select_new_mode button[data-testid="stBaseButton-primary"]:focus,
        .st-key-select_new_mode button[data-testid="stBaseButton-primary"]:focus-visible,
        .st-key-select_new_mode button[data-testid="stBaseButton-primary"]:focus-within,
        .st-key-select_new_mode button[data-testid="stBaseButton-secondary"]:active,
        .st-key-select_new_mode button[data-testid="stBaseButton-secondary"]:focus,
        .st-key-select_new_mode button[data-testid="stBaseButton-secondary"]:focus-visible,
        .st-key-select_new_mode button[data-testid="stBaseButton-secondary"]:focus-within,
        .st-key-select_load_mode button[data-testid="stBaseButton-primary"]:active,
        .st-key-select_load_mode button[data-testid="stBaseButton-primary"]:focus,
        .st-key-select_load_mode button[data-testid="stBaseButton-primary"]:focus-visible,
        .st-key-select_load_mode button[data-testid="stBaseButton-primary"]:focus-within,
        .st-key-select_load_mode button[data-testid="stBaseButton-secondary"]:active,
        .st-key-select_load_mode button[data-testid="stBaseButton-secondary"]:focus,
        .st-key-select_load_mode button[data-testid="stBaseButton-secondary"]:focus-visible,
        .st-key-select_load_mode button[data-testid="stBaseButton-secondary"]:focus-within {
            transform: none !important;
            box-shadow: none !important;
            filter: none !important;
            outline: none !important;
            border-color: inherit !important;
            background: inherit !important;
            height: 100px !important;
            min-height: 100px !important;
            max-height: 100px !important;
        }
        
        /* Disable click effects on text elements */
        .st-key-select_new_mode button[data-testid="stBaseButton-primary"]:active *,
        .st-key-select_new_mode button[data-testid="stBaseButton-primary"]:focus *,
        .st-key-select_new_mode button[data-testid="stBaseButton-secondary"]:active *,
        .st-key-select_new_mode button[data-testid="stBaseButton-secondary"]:focus *,
        .st-key-select_load_mode button[data-testid="stBaseButton-primary"]:active *,
        .st-key-select_load_mode button[data-testid="stBaseButton-primary"]:focus *,
        .st-key-select_load_mode button[data-testid="stBaseButton-secondary"]:active *,
        .st-key-select_load_mode button[data-testid="stBaseButton-secondary"]:focus * {
            color: inherit !important;
        }
        
        [data-testid="column"]:first-of-type button[data-testid^="stBaseButton"] > div,
        [data-testid="column"]:nth-of-type(2) button[data-testid^="stBaseButton"] > div {
            display: flex !important;
            flex-direction: column !important;
            align-items: center !important;
            gap: 0.3rem !important;
        }
        
        /* Pipeline mode selection buttons - make entire cards clickable */
        .st-key-select_multi_mode button[data-testid^="stBaseButton"],
        .st-key-select_mono_mode button[data-testid^="stBaseButton"] {
            background: linear-gradient(145deg, rgba(30, 41, 59, 0.5) 0%, rgba(56, 189, 248, 0.05) 100%) !important;
            border: 2px solid rgba(71, 85, 105, 0.3) !important;
            border-radius: 12px !important;
            padding: 1rem !important;
            height: auto !important;
            min-height: 120px !important;
            width: 100% !important;
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
            flex-direction: column !important;
            text-align: center !important;
            transition: all 0.3s ease !important;
            box-sizing: border-box !important;
        }
        
        .st-key-select_multi_mode button[data-testid^="stBaseButton"] > div,
        .st-key-select_mono_mode button[data-testid^="stBaseButton"] > div {
            display: flex !important;
            flex-direction: column !important;
            align-items: center !important;
            gap: 0.3rem !important;
        }
        
        /* Selected pipeline mode button style - blue border, white text, and neon glow */
        .st-key-select_multi_mode button[data-testid="stBaseButton-primary"]:not(:hover):not(:active):not(:focus),
        .st-key-select_multi_mode button[data-testid="stBaseButton-primary"]:hover:not(:disabled),
        .st-key-select_mono_mode button[data-testid="stBaseButton-primary"]:not(:hover):not(:active):not(:focus),
        .st-key-select_mono_mode button[data-testid="stBaseButton-primary"]:hover:not(:disabled) {
            border-color: rgba(56, 189, 248, 0.7) !important;
            color: #f1f5f9 !important;
            box-shadow: 0 0 20px rgba(56, 189, 248, 0.4), 0 0 40px rgba(56, 189, 248, 0.2) !important;
        }
        
        .st-key-select_multi_mode button[data-testid="stBaseButton-primary"]:not(:hover):not(:active):not(:focus) *,
        .st-key-select_multi_mode button[data-testid="stBaseButton-primary"]:hover:not(:disabled) *,
        .st-key-select_mono_mode button[data-testid="stBaseButton-primary"]:not(:hover):not(:active):not(:focus) *,
        .st-key-select_mono_mode button[data-testid="stBaseButton-primary"]:hover:not(:disabled) * {
            color: #f1f5f9 !important;
        }
        
        /* Hover effect for pipeline mode buttons - simple border color change - NO TRANSFORM */
        .st-key-select_multi_mode button[data-testid="stBaseButton-primary"]:hover:not(:disabled),
        .st-key-select_mono_mode button[data-testid="stBaseButton-primary"]:hover:not(:disabled) {
            border-color: rgba(56, 189, 248, 0.7) !important;
            filter: none !important;
            color: #f1f5f9 !important;
            box-shadow: 0 0 20px rgba(56, 189, 248, 0.4), 0 0 40px rgba(56, 189, 248, 0.2) !important;
            transform: none !important;
        }
        
        .st-key-select_multi_mode button[data-testid="stBaseButton-secondary"]:hover:not(:disabled),
        .st-key-select_mono_mode button[data-testid="stBaseButton-secondary"]:hover:not(:disabled) {
            border-color: rgba(56, 189, 248, 0.7) !important;
            filter: none !important;
            color: #f1f5f9 !important;
            box-shadow: none !important;
            transform: none !important;
        }
        
        /* Disable ALL click effects for pipeline mode buttons */
        .st-key-select_multi_mode button[data-testid^="stBaseButton"]:active,
        .st-key-select_multi_mode button[data-testid^="stBaseButton"]:focus,
        .st-key-select_multi_mode button[data-testid^="stBaseButton"]:focus-visible,
        .st-key-select_multi_mode button[data-testid^="stBaseButton"]:focus-within,
        .st-key-select_mono_mode button[data-testid^="stBaseButton"]:active,
        .st-key-select_mono_mode button[data-testid^="stBaseButton"]:focus,
        .st-key-select_mono_mode button[data-testid^="stBaseButton"]:focus-visible,
        .st-key-select_mono_mode button[data-testid^="stBaseButton"]:focus-within {
            transform: none !important;
            box-shadow: inherit !important;
            filter: none !important;
            outline: none !important;
    }
    
    /* File uploader dark styling */
    [data-testid="stFileUploader"] {
        background: transparent !important;
        padding: 0 !important;
        margin-top: 0.5rem !important;
    }
    
    [data-testid="stFileUploader"] label {
        color: #94a3b8 !important;
    }
    
    [data-testid="stFileUploader"] section {
        background: rgba(15, 23, 42, 0.5) !important;
        border: 2px dashed rgba(56, 189, 248, 0.35) !important;
        border-radius: 10px !important;
        padding: 1rem 0.8rem !important;
    }
    
    [data-testid="stFileUploader"] section:hover {
        border-color: rgba(56, 189, 248, 0.35) !important;
        background: rgba(15, 23, 42, 0.5) !important;
    }
    
    /* Remove all hover, active, and focus effects from file uploader button */
    [data-testid="stFileUploader"] button:hover,
    [data-testid="stFileUploader"] button:active,
    [data-testid="stFileUploader"] button:focus {
        transform: none !important;
        box-shadow: inherit !important;
        filter: none !important;
        background: linear-gradient(135deg, #38bdf8 0%, #22c55e 100%) !important;
        color: #020617 !important;
    }
    
    [data-testid="stFileUploader"] section > div {
        color: #94a3b8 !important;
    }
    
    [data-testid="stFileUploader"] button {
        background: linear-gradient(135deg, #38bdf8 0%, #22c55e 100%) !important;
        color: #020617 !important;
        font-weight: 600 !important;
        border-radius: 8px !important;
        font-size: 0.9rem !important;
    }
    
    /* Remove all hover, active, and focus effects from file uploader button */
    [data-testid="stFileUploader"] button:hover,
    [data-testid="stFileUploader"] button:active,
    [data-testid="stFileUploader"] button:focus,
    [data-testid="stFileUploader"] button:focus-visible,
    [data-testid="stFileUploader"] button:focus-within {
        transform: none !important;
        box-shadow: inherit !important;
        filter: none !important;
        outline: none !important;
        border: none !important;
        background: linear-gradient(135deg, #38bdf8 0%, #22c55e 100%) !important;
        color: #020617 !important;
    }
    
    /* Validate dataset button - bold text */
    .st-key-validate_dataset_btn button,
    .st-key-validate_dataset_btn button *,
    .st-key-validate_dataset_btn button p,
    .st-key-validate_dataset_btn button div {
        font-weight: 600 !important;
        font-size: 0.95rem !important;
    }
    
    /* Launch Analysis button - bold text */
    .st-key-launch_analysis_btn button,
    .st-key-launch_analysis_btn button *,
    .st-key-launch_analysis_btn button p,
    .st-key-launch_analysis_btn button div {
        font-weight: 600 !important;
        font-size: 2.2rem !important;
    }
    
    /* Selectbox dark styling - inside card */
    [data-testid="stSelectbox"] {
        background: transparent !important;
        padding: 0 !important;
        margin-top: 0.5rem !important;
    }
    
    [data-testid="stSelectbox"] > div > div {
        background-color: rgba(15, 23, 42, 0.8) !important;
        border-color: rgba(56, 189, 248, 0.3) !important;
        color: #e2e8f0 !important;
        border-radius: 8px !important;
    }
    
    /* Ensure selectbox dropdown arrow is visible */
    [data-testid="stSelectbox"] svg,
    [data-testid="stSelectbox"] svg path {
        display: block !important;
        visibility: visible !important;
        color: #94a3b8 !important;
        fill: #94a3b8 !important;
    }
    
    [data-testid="stSelectbox"] label {
        color: #f1f5f9 !important;
    }
    
    /* Text input label - white color */
    [data-testid="stTextInput"] label {
        color: #f1f5f9 !important;
    }
    
    /* Tooltip styling - make consistent across all inputs */
    /* Target help icons in labels - make them more visible */
    label svg,
    [data-testid="stTooltipIcon"],
    [data-testid="stTooltipIcon"] svg,
    [data-testid="stTooltipIcon"] svg path,
    [data-testid="stTextInput"] label svg,
    [data-testid="stSelectbox"] label svg {
        color: #64748b !important;
        fill: #64748b !important;
        opacity: 1 !important;
    }
    
    label svg:hover,
    [data-testid="stTooltipIcon"]:hover,
    [data-testid="stTooltipIcon"]:hover svg,
    [data-testid="stTooltipIcon"]:hover svg path,
    [data-testid="stTextInput"] label svg:hover,
    [data-testid="stSelectbox"] label svg:hover {
        color: #38bdf8 !important;
        fill: #38bdf8 !important;
        opacity: 1 !important;
    }
    
    /* Tooltip popup styling - dark theme */
    [data-testid="stTooltip"],
    .stTooltip,
    [data-baseweb="tooltip"],
    [role="tooltip"] {
        background-color: rgba(15, 23, 42, 0.95) !important;
        border: 1px solid rgba(56, 189, 248, 0.3) !important;
        color: #e2e8f0 !important;
        backdrop-filter: blur(10px) !important;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.5) !important;
    }
    
    [data-testid="stTooltip"] *,
    .stTooltip *,
    [data-baseweb="tooltip"] *,
    [role="tooltip"] * {
        color: #e2e8f0 !important;
    }
        
        /* Text input dark styling */
        [data-testid="stTextInput"] {
            background: transparent !important;
        }
        
        [data-testid="stTextInput"] > div > div > input {
            background-color: rgba(15, 23, 42, 0.8) !important;
            border: 1px solid rgba(56, 189, 248, 0.3) !important;
            color: #e2e8f0 !important;
            border-radius: 8px !important;
            padding: 0.6rem 1rem !important;
        }
        
        /* Force blue color only - remove any red from all states - MAXIMUM SPECIFICITY */
        [data-testid="stTextInput"] > div > div > input,
        [data-testid="stTextInput"] > div > div > input:hover,
        [data-testid="stTextInput"] > div > div > input:active,
        [data-testid="stTextInput"] input,
        [data-testid="stTextInput"] input:hover,
        [data-testid="stTextInput"] input:active {
            border-color: rgba(56, 189, 248, 0.3) !important;
            border-top-color: rgba(56, 189, 248, 0.3) !important;
            border-right-color: rgba(56, 189, 248, 0.3) !important;
            border-bottom-color: rgba(56, 189, 248, 0.3) !important;
            border-left-color: rgba(56, 189, 248, 0.3) !important;
        }
        
        /* Blue border when focused - override any red - MAXIMUM SPECIFICITY */
        [data-testid="stTextInput"] > div > div > input:focus,
        [data-testid="stTextInput"] > div > div > input:focus-visible,
        [data-testid="stTextInput"] > div > div > input:focus-within,
        [data-testid="stTextInput"] input:focus,
        [data-testid="stTextInput"] input:focus-visible,
        [data-testid="stTextInput"] input:focus-within {
            border: 2px solid rgba(56, 189, 248, 1) !important;
            border-color: rgba(56, 189, 248, 1) !important;
            border-top-color: rgba(56, 189, 248, 1) !important;
            border-right-color: rgba(56, 189, 248, 1) !important;
            border-bottom-color: rgba(56, 189, 248, 1) !important;
            border-left-color: rgba(56, 189, 248, 1) !important;
            box-shadow: 0 0 0 4px rgba(56, 189, 248, 0.4) !important;
            outline: none !important;
        }
        
        /* Remove red from any parent wrapper elements */
        [data-testid="stTextInput"] > div,
        [data-testid="stTextInput"] > div > div,
        [data-testid="stTextInput"] > div:focus,
        [data-testid="stTextInput"] > div:focus-within,
        [data-testid="stTextInput"] > div > div:focus,
        [data-testid="stTextInput"] > div > div:focus-within {
            border-color: transparent !important;
            outline: none !important;
        }
        
        [data-testid="stTextInput"] > div > div > input::placeholder {
            color: #64748b !important;
    }
    
    /* Dataframe dark styling */
    [data-testid="stDataFrame"] {
        background: rgba(15, 23, 42, 0.8) !important;
        border-radius: 10px !important;
        overflow: hidden !important;
    }
    
    [data-testid="stDataFrame"] > div {
        background: transparent !important;
    }
    
    /* Hide resize handle on dataframe */
    [data-testid="stDataFrame"] [data-testid="stDataFrameResizable"] {
        resize: none !important;
    }
    
    [data-testid="stDataFrame"] iframe {
        resize: none !important;
    }
    
    /* Hide the resize grip */
    [data-testid="stElementToolbar"] {
        display: none !important;
    }
    
    /* Remove default padding */
    .block-container {
        padding-top: 1rem !important;
        max-width: 1200px !important;
    }
    
    /* Hide link icons (chain links) next to titles */
    h1 a,
    h2 a,
    h3 a,
    h4 a,
    h5 a,
    h6 a,
    h1 a svg,
    h2 a svg,
    h3 a svg,
    h4 a svg,
    h5 a svg,
    h6 a svg,
    [data-testid="stMarkdownContainer"] h1 a,
    [data-testid="stMarkdownContainer"] h2 a,
    [data-testid="stMarkdownContainer"] h3 a,
    [data-testid="stMarkdownContainer"] h4 a,
    [data-testid="stMarkdownContainer"] h5 a,
    [data-testid="stMarkdownContainer"] h6 a,
    [data-testid="stMarkdownContainer"] h1 a svg,
    [data-testid="stMarkdownContainer"] h2 a svg,
    [data-testid="stMarkdownContainer"] h3 a svg,
    [data-testid="stMarkdownContainer"] h4 a svg,
    [data-testid="stMarkdownContainer"] h5 a svg,
    [data-testid="stMarkdownContainer"] h6 a svg {
        display: none !important;
        visibility: hidden !important;
    }
    
    /* Position expander centered below badge with fixed width */
    [data-testid="stExpander"] {
        width: 400px !important;
        min-width: 400px !important;
        max-width: 400px !important;
        margin-left: auto !important;
        margin-right: auto !important;
        display: block !important;
        background: rgba(15, 23, 42, 0.95) !important;
        backdrop-filter: blur(10px) !important;
    }
    
    /* Center the column containing the expander - target middle column */
    [data-testid="column"]:nth-of-type(2) {
        display: flex !important;
        justify-content: center !important;
        align-items: flex-start !important;
    }
    
    [data-testid="column"]:nth-of-type(2) > div {
        width: 100% !important;
        max-width: 400px !important;
        display: flex !important;
        justify-content: center !important;
    }
    
    /* Expander text - simple gray color, no hover effects, larger font */
    [data-testid="stExpander"] > div:first-child,
    [data-testid="stExpander"] > div:first-child *,
    [data-testid="stExpander"] summary,
    [data-testid="stExpander"] summary * {
        color: #94a3b8 !important;
        font-size: 1.3rem !important;
        font-weight: 600 !important;
    }
    
    /* Hide chevron SVG in expander header only, not in content */
    [data-testid="stExpander"] > div:first-child svg,
    [data-testid="stExpander"] > div:first-child svg *,
    [data-testid="stExpander"] > div:first-child svg path {
        display: none !important;
    }
    
    /* But keep selectbox arrows visible - they are in expander content */
    [data-testid="stExpander"] [data-testid="stSelectbox"] svg,
    [data-testid="stExpander"] [data-testid="stSelectbox"] svg *,
    [data-testid="stExpander"] [data-testid="stSelectbox"] svg path {
        display: block !important;
        visibility: visible !important;
    }
    
    /* Saved analyses action buttons container - flexbox with gap */
    #saved-analysis-buttons-container {
        display: flex !important;
        align-items: center !important;
        gap: 0.75rem !important;
        margin-top: 1rem !important;
    }
    
    /* Saved analyses action buttons - bold text, reduced width */
    .st-key-load_saved_btn,
    .st-key-delete_saved_btn {
        display: inline-block !important;
        margin: 0 !important;
    }
    
    .st-key-load_saved_btn button,
    .st-key-delete_saved_btn button {
        font-weight: 600 !important;
        max-width: 180px !important;
        width: 180px !important;
        margin: 0 !important;
    }
    
    .st-key-load_saved_btn button *,
    .st-key-delete_saved_btn button *,
    .st-key-load_saved_btn button p,
    .st-key-delete_saved_btn button p,
    .st-key-load_saved_btn button div,
    .st-key-delete_saved_btn button div {
        font-weight: 600 !important;
    }
    
    </style>
        """, unsafe_allow_html=True
    )
    
    # Main container with max-width
    st.markdown("""
    <div style="max-width: 1200px; margin: 0 auto; padding: 0 1rem;">
    </div>
        """, unsafe_allow_html=True
    )
    
    # Render sections
    render_hero()
    render_agents()
    
    # Mode selection (new analysis vs load saved)
    render_mode_selection()
    
    # Conditional rendering based on mode
    if st.session_state.get("landing_mode", "new") == "new":
        # New analysis flow
        render_data_source()
        render_preview_panels()
        render_analysis_name_input()
        render_cta()
    else:
        # Load saved analysis flow
        render_saved_analyses()