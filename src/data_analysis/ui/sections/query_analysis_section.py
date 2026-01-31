"""Display section for query analysis results (data sent to visualization agent)."""


import streamlit as st
import pandas as pd


def display_query_analysis(data: dict):
    """Display the query analysis results sent to the visualization agent.
    
    Args:
        data: Dictionary containing the analyzed query results.
    """

    analyses = data.get("analyses", [])
    
    if not analyses:
        st.info("No query analysis data available.")
        return

    # Create tabs for each analysis group
    analysis_tabs = st.tabs([f"{a.get('id', 'N/A')} - {a.get('title', 'No title')}" for a in analyses])

    for i, analysis in enumerate(analyses):
        with analysis_tabs[i]:
            st.markdown(f"### {analysis.get('title', 'Analysis')}")
            
            queries = analysis.get("queries", [])
            
            if not queries:
                st.info("No queries in this analysis.")
                continue
            
            # Create sub-tabs for each query
            query_tabs = st.tabs([f"{q.get('id', 'N/A')} - {q.get('title', 'No title')}" for q in queries])
            
            for j, query in enumerate(queries):
                with query_tabs[j]:
                    _display_query_details(query)


def _display_query_details(query: dict):
    """Display details for a single query analysis.
    
    Args:
        query: Dictionary containing a single query's analysis data.
    """
    
    query_id = query.get("id", "N/A")
    query_title = query.get("title", "N/A")
    query_type = query.get("type", "N/A")
    
    st.markdown(f"**ID:** `{query_id}`")
    st.markdown(f"**Type:** `{query_type}`")
    
    # Check for error
    if "error" in query:
        st.error(f"Error: {query['error']}")
        return
    
    # Display analysis if available
    analysis = query.get("analysis", {})
    
    if not analysis:
        st.warning("No analysis data available for this query.")
        return
    
    # Summary info
    row_count = analysis.get("row_count", "N/A")
    column_count = analysis.get("column_count", "N/A")
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Rows", row_count)
    with col2:
        st.metric("Columns", column_count)
    
    # Column details
    columns = analysis.get("columns", {})
    
    if columns:
        st.markdown("#### Column Details")
        
        col_data = []
        for col_name, col_info in columns.items():
            row = {
                "Column": col_name,
                "Type": col_info.get("type", "N/A"),
                "Nullable": col_info.get("nullable", "N/A"),
                "Null Count": col_info.get("null_count", "N/A"),
                "Unique Count": col_info.get("unique_count", "N/A"),
            }
            
            # Add numeric stats if available
            if col_info.get("min") is not None:
                row["Min"] = round(col_info["min"], 2) if isinstance(col_info["min"], float) else col_info["min"]
            else:
                row["Min"] = "-"
            
            if col_info.get("max") is not None:
                row["Max"] = round(col_info["max"], 2) if isinstance(col_info["max"], float) else col_info["max"]
            else:
                row["Max"] = "-"
            
            if col_info.get("mean") is not None:
                row["Mean"] = round(col_info["mean"], 2)
            else:
                row["Mean"] = "-"
            
            if col_info.get("std") is not None:
                row["Std"] = round(col_info["std"], 2)
            else:
                row["Std"] = "-"
            
            # Add string stats if available
            if col_info.get("avg_length") is not None:
                row["Avg Length"] = round(col_info["avg_length"], 1)
            
            if col_info.get("max_length") is not None:
                row["Max Length"] = col_info["max_length"]
            
            col_data.append(row)
        
        df = pd.DataFrame(col_data).astype(str)
        st.dataframe(df, use_container_width=True, hide_index=True)