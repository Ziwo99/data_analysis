"""Display section for visualization results with charts and code."""


import streamlit as st
import pandas as pd


def display_visualizations_analysis(data: dict):
    """Display visualizations with DataFrame, code, and chart tabs for each sub-analysis.
    
    Args:
        data: Dictionary containing the visualization analysis results.
    """

    # Get the analyses from the data
    analyses = data.get("analyses", [])

    # Check if there are any analyses
    if not analyses:
        st.info("No visualization analysis available.")
        return

    # === Main tabs : one tab for each analysis ===
    tab_labels = [f"{analysis.get('id', 'N/A')} - {analysis.get('title', 'No title')}" for analysis in analyses]
    main_tabs = st.tabs(tab_labels)

    # Display each analysis in its tab
    for i, analysis in enumerate(analyses):
        with main_tabs[i]:
            analysis_id = analysis.get("id", "N/A")
            title = analysis.get("title", "No title")
            context = analysis.get("context", "")
            tables = analysis.get("tables", [])
            sub_analyses = analysis.get("sub_analyses", [])

            # --------------------------------------------------------------------
            # ANALYSIS HEADER
            # --------------------------------------------------------------------
            st.subheader(f"Analysis {analysis_id}: {title}")

            if context:
                st.markdown(f"**Context :** {context}")

            if tables:
                tables_str = ", ".join(tables)
                st.markdown(f"**Tables used :** `{tables_str}`")

            # --------------------------------------------------------------------
            # SUB-ANALYSES IN COLLAPSES
            # --------------------------------------------------------------------
            if not sub_analyses:
                st.info("No sub-analysis available.")
            else:
                for sub_analysis in sub_analyses:
                    sub_id = sub_analysis.get("id", "N/A")
                    sub_title = sub_analysis.get("title", "No title")
                    why = sub_analysis.get("why", "")
                    answers = sub_analysis.get("answers", [])
                    tables_columns = sub_analysis.get("tables_columns", [])
                    code_lines = sub_analysis.get("code_lines", [])
                    query_success = sub_analysis.get("query_success", False)
                    query_error = sub_analysis.get("query_error", None)
                    result_dataframe = sub_analysis.get("result_dataframe", None)
                    visualization_code = sub_analysis.get("visualization_code", [])
                    visualization_success = sub_analysis.get("visualization_success", False)
                    visualization_error = sub_analysis.get("visualization_error", None)
                    result_plot = sub_analysis.get("result_plot", None)

                    # Use an expander for each sub-analysis
                    with st.expander(f"{sub_id} - {sub_title}", expanded=False):
                        # --------------------------------------------------------------------
                        # BASIC INFORMATION (why, answers, tables_columns)
                        # --------------------------------------------------------------------
                        if tables_columns:
                            columns_str = ", ".join(tables_columns)
                            st.markdown("##### Columns used")
                            st.markdown(f"`{columns_str}`")

                        if why:
                            st.markdown("##### Why")
                            st.markdown(why)

                        if answers:
                            st.markdown("##### Expected answers")
                            for answer in answers:
                                st.markdown(f"• {answer}")

                        # --------------------------------------------------------------------
                        # FOUR TABS : VISUALIZATION + VIZ CODE + DATAFRAME + QUERY CODE
                        # --------------------------------------------------------------------
                        if code_lines or result_dataframe is not None or query_error or visualization_code or result_plot is not None or visualization_error:
                            tab_visualization, tab_viz_code, tab_dataframe, tab_code = st.tabs(["Visualization", "Visualization code", "Dataframe", "Query code"])

                            # TAB 1 - Visualization
                            with tab_visualization:
                                # Check for image path (new format) or result_plot (legacy format)
                                visualization_image_path = sub_analysis.get("visualization_image_path", None)
                                
                                if visualization_success and (visualization_image_path or result_plot is not None):
                                    try:
                                        # Display the visualization aligned left with reduced width
                                        col_chart, col_space = st.columns([0.7, 1.3])
                                        with col_chart:
                                            if visualization_image_path:
                                                # New format: display PNG image
                                                from pathlib import Path
                                                image_path = Path(visualization_image_path)
                                                if image_path.exists():
                                                    st.image(str(image_path), use_container_width=True)
                                                else:
                                                    st.error(f"Visualization image not found: {image_path}")
                                            elif result_plot is not None:
                                                # Legacy format: display matplotlib figure
                                                st.pyplot(result_plot, use_container_width=True)
                                        
                                        # Display visualization type if available
                                        visualization_type = sub_analysis.get("visualization_type", None)
                                        if visualization_type:
                                            st.caption(f"Visualization type: {visualization_type}")
                                        
                                        # Display justification if available
                                        justification = sub_analysis.get("justification", None)
                                        if justification:
                                            st.markdown("##### Justification")
                                            st.markdown(justification)
                                    except Exception as e:
                                        st.error(f"Error displaying visualization: {e}")
                                elif visualization_error:
                                    st.error(f"Error during the visualization execution:\n\n`{visualization_error}`")
                                else:
                                    st.info("No visualization available.")

                            # TAB 2 - Visualization Code
                            with tab_viz_code:
                                if visualization_code:
                                    viz_code_str = "\n".join(visualization_code)
                                    st.code(viz_code_str, language="python")
                                else:
                                    st.info("No visualization code available.")

                            # TAB 3 - Result DataFrame
                            with tab_dataframe:
                                if query_success and result_dataframe is not None:
                                    # Convert columns to string to avoid PyArrow errors with mixed types
                                    df_display = result_dataframe.copy()
                                    for col in df_display.columns:
                                        if df_display[col].dtype == 'object':
                                            df_display[col] = df_display[col].astype(str)
                                    # Display the DataFrame
                                    st.dataframe(df_display, use_container_width=True)
                                    
                                    # Display additional information if available
                                    result_shape = sub_analysis.get("result_shape", None)
                                    if result_shape:
                                        st.caption(f"Shape: {result_shape[0]} rows × {result_shape[1]} columns")
                                elif query_error:
                                    st.error(f"Error during the query execution:\n\n`{query_error}`")
                                else:
                                    st.info("No result available.")

                            # TAB 4 - Query Code
                            with tab_code:
                                if code_lines:
                                    code_str = "\n".join(code_lines)
                                    st.code(code_str, language="python")
                                else:
                                    st.info("No code available.")