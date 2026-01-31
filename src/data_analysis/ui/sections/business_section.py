"""Display section for business analysis results."""


import streamlit as st


def display_business_analysis(data: dict):
    """Display business analyses with tabs for each analysis and expanders for sub-analyses.
    
    Args:
        data: Dictionary containing the business analysis data.
    """

    # Get the analyses from the data
    analyses = data.get("analyses", [])

    # Check if there are any analyses
    if not analyses:
        st.info("No business analysis available.")
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

                    # Use an expander for each sub-analysis
                    with st.expander(f"{sub_id} - {sub_title}", expanded=False):
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