"""Complete report view - displays analysis results and visualizations without code."""


import json
import pickle
import streamlit as st
from data_analysis.system.utils.paths import (
    VISUALIZATION_RESULTS_PICKLE_FILE,
    BUSINESS_ANALYSIS_FILE,
    resolve_visualization_image_path,
)


def render_report_view():
    """Render the complete report view with visualizations (no code displayed)."""
    
    # Get analysis name for display
    is_view_mode = st.session_state.get("is_view_mode", False)
    analysis_name = st.session_state.get("loaded_analysis_name", "") if is_view_mode else st.session_state.get("pending_analysis_name", "")
    
    # Header with back button
    col1, col2, col3 = st.columns([1, 2, 2])
    
    with col1:
        if st.button("← Back to analysis", key="back_to_analysis_from_report", type="secondary", use_container_width=True):
            st.session_state.current_page = "analysis"
            st.rerun()
    
    with col2:
        st.markdown(f'<div style="display: flex; justify-content: center;"><div style="display: inline-flex; align-items: center; gap: 0.6rem; padding: 0.5rem 1rem; background: linear-gradient(135deg, rgba(251, 191, 36, 0.15) 0%, rgba(245, 158, 11, 0.1) 100%); border: 1px solid rgba(251, 191, 36, 0.4); border-radius: 999px; box-shadow: 0 2px 10px rgba(251, 191, 36, 0.15);"><span style="font-size: 1rem;">📋</span><span style="color: #fde047; font-weight: 600; font-size: 0.85rem;">Complete Report</span><span style="color: #fbbf24; font-size: 0.75rem; opacity: 0.7; display: flex; align-items: center; line-height: 1;">—</span><span style="color: #fbbf24; font-size: 0.8rem;">{analysis_name}</span></div></div>', unsafe_allow_html=True)
    
    st.markdown('<div style="height: 1.5rem;"></div>', unsafe_allow_html=True)
    
    # Title
    st.markdown("## Analysis Report")
    
    # Load visualization data (contains both data and visualizations)
    viz_data = None
    if VISUALIZATION_RESULTS_PICKLE_FILE.exists():
        try:
            with open(VISUALIZATION_RESULTS_PICKLE_FILE, "rb") as f:
                viz_data = pickle.load(f)
        except Exception:
            viz_data = None
    
    # Load business analysis data for additional context
    business_data = None
    if BUSINESS_ANALYSIS_FILE.exists():
        try:
            with open(BUSINESS_ANALYSIS_FILE, "r", encoding="utf-8") as f:
                business_data = json.load(f)
        except Exception:
            business_data = None
    
    # Display analyses
    if viz_data and viz_data.get("analyses"):
        analyses = viz_data.get("analyses", [])
        
        for analysis in analyses:
            analysis_id = analysis.get("id", "N/A")
            title = analysis.get("title", "Untitled")
            context = analysis.get("context", "")
            tables = analysis.get("tables", [])
            sub_analyses = analysis.get("sub_analyses", [])
            
            # Analysis header - styled section title
            st.markdown(f'<div style="background: linear-gradient(90deg, rgba(59, 130, 246, 0.2) 0%, transparent 100%); padding: 0.75rem 1rem; border-left: 4px solid #3b82f6; border-radius: 0 8px 8px 0; margin: 1.5rem 0 1rem 0;"><h3 style="margin: 0; color: #93c5fd; font-size: 1.3rem;">{analysis_id}. {title}</h3></div>', unsafe_allow_html=True)
            
            if context:
                st.markdown(f"**Context:** {context}")
            
            if tables:
                tables_str = ", ".join(tables)
                st.markdown(f"**Tables used:** `{tables_str}`")
            
            st.markdown('<div style="height: 0.5rem;"></div>', unsafe_allow_html=True)
            
            # Sub-analyses
            if sub_analyses:
                for sub_analysis in sub_analyses:
                    sub_id = sub_analysis.get("id", "N/A")
                    sub_title = sub_analysis.get("title", "Untitled")
                    why = sub_analysis.get("why", "")
                    answers = sub_analysis.get("answers", [])
                    tables_columns = sub_analysis.get("tables_columns", [])
                    visualization_type = sub_analysis.get("visualization_type", "")
                    justification = sub_analysis.get("justification", "")
                    visualization_success = sub_analysis.get("visualization_success", False)
                    result_plot = sub_analysis.get("result_plot")
                    visualization_image_path = sub_analysis.get("visualization_image_path", None)
                    result_dataframe = sub_analysis.get("result_dataframe")
                    
                    # Sub-analysis section - smaller styling
                    with st.container():
                        st.markdown(f"##### {sub_id}. {sub_title}")
                        
                        # Columns used
                        if tables_columns:
                            columns_str = ", ".join(tables_columns)
                            st.markdown(f"**Columns analyzed:** `{columns_str}`")
                        
                        # Why this analysis
                        if why:
                            st.markdown(f"**Objective:** {why}")
                        
                        # Expected answers / insights
                        if answers:
                            st.markdown("**Expected results:**")
                            for answer in answers:
                                st.markdown(f"- {answer}")
                        
                        # Visualization (smaller size)
                        if visualization_success and (visualization_image_path or result_plot is not None):
                            st.markdown('<div style="height: 0.5rem;"></div>', unsafe_allow_html=True)
                            
                            try:
                                # Display the visualization with reduced size
                                col_chart, col_space = st.columns([1, 2])
                                with col_chart:
                                    if visualization_image_path:
                                        # New format: display PNG image (path resolved for portability after clone)
                                        image_path = resolve_visualization_image_path(visualization_image_path)
                                        if image_path is not None:
                                            st.image(str(image_path), use_container_width=True)
                                        else:
                                            st.error(f"Visualization image not found: {visualization_image_path}")
                                    elif result_plot is not None:
                                        # Legacy format: display matplotlib figure
                                        st.pyplot(result_plot, use_container_width=True)
                                
                                # Visualization type info
                                if visualization_type:
                                    st.caption(f"Visualization type: {visualization_type}")
                                
                                # Justification
                                if justification:
                                    st.markdown(f"**Justification:** {justification}")
                                    
                            except Exception as e:
                                st.warning(f"Unable to display visualization: {e}")
                        
                        # Data summary if no visualization but we have data
                        elif result_dataframe is not None:
                            result_shape = sub_analysis.get("result_shape")
                            if result_shape:
                                st.info(f"Data extracted: {result_shape[0]} rows × {result_shape[1]} columns")
                        
                        st.markdown("---")
            
            st.markdown('<div style="height: 1rem;"></div>', unsafe_allow_html=True)
    
    elif business_data and business_data.get("analyses"):
        # Fallback to business analysis if visualization data not available
        analyses = business_data.get("analyses", [])
        
        for analysis in analyses:
            analysis_id = analysis.get("id", "N/A")
            title = analysis.get("title", "Untitled")
            context = analysis.get("context", "")
            tables = analysis.get("tables", [])
            sub_analyses = analysis.get("sub_analyses", [])
            
            # Analysis header - styled section title
            st.markdown(f'<div style="background: linear-gradient(90deg, rgba(59, 130, 246, 0.2) 0%, transparent 100%); padding: 0.75rem 1rem; border-left: 4px solid #3b82f6; border-radius: 0 8px 8px 0; margin: 1.5rem 0 1rem 0;"><h3 style="margin: 0; color: #93c5fd; font-size: 1.3rem;">{analysis_id}. {title}</h3></div>', unsafe_allow_html=True)
            
            if context:
                st.markdown(f"**Context:** {context}")
            
            if tables:
                tables_str = ", ".join(tables)
                st.markdown(f"**Tables used:** `{tables_str}`")
            
            if sub_analyses:
                for sub_analysis in sub_analyses:
                    sub_id = sub_analysis.get("id", "N/A")
                    sub_title = sub_analysis.get("title", "Untitled")
                    why = sub_analysis.get("why", "")
                    answers = sub_analysis.get("answers", [])
                    
                    st.markdown(f"##### {sub_id}. {sub_title}")
                    
                    if why:
                        st.markdown(f"**Objective:** {why}")
                    
                    if answers:
                        st.markdown("**Expected results:**")
                        for answer in answers:
                            st.markdown(f"- {answer}")
                    
                    st.markdown("---")
            
            st.markdown('<div style="height: 1rem;"></div>', unsafe_allow_html=True)
    
    else:
        st.info("No analysis data available.")
    

    
    # Bottom back button (same style and position as top)
    col1, col2, col3 = st.columns([1, 2, 2])
    with col1:
        if st.button("← Back to analysis", key="back_to_analysis_from_report_bottom", type="secondary", use_container_width=True):
            st.session_state.current_page = "analysis"
            st.rerun()
    
        st.markdown('<div style="height: 1rem;"></div>', unsafe_allow_html=True)