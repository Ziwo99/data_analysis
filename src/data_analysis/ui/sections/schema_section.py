"""Display section for interpreted schema summary."""


import streamlit as st
import pandas as pd


def display_schema_summary(data: dict):
    """Display the interpreted schema summary with business context.
    
    Args:
        data: Dictionary containing the interpreted schema with domain info.
    """

    # === Main tabs : 3 tabs ===
    main_tabs = st.tabs(["Global view", "Tables", "Relations"])

    # --------------------------------------------------------------------
    # TAB 1 - Global view
    # --------------------------------------------------------------------
    with main_tabs[0]:
        st.subheader("General information about the database")

        st.markdown(f"**Source type :** `{data.get('source_type', 'N/A')}`")
        st.markdown(f"**Number of tables :** `{data.get('number_of_tables', 'N/A')}`")
        
        # Business interpretation (if available)
        database_domain = data.get("database_domain")
        database_description = data.get("database_description")
        
        if database_domain:
            st.markdown(f"**Domain :** `{database_domain}`")
        
        if database_description:
            st.markdown(f"**Description :** {database_description}")

        # Summary table of the tables
        tables = data.get("tables", {})
        st.markdown("### Overview of the tables")
        summary_rows = [
            {
                "Table": name,
                "Rows": str(info.get("row_count", "N/A")),
                "Primary key": info.get("primary_key", "N/A"),
                "Foreign keys": ", ".join(info.get("foreign_keys", [])) if info.get("foreign_keys") else "None",
                "Number of columns": str(len(info.get("columns", {}))),
            }
            for name, info in tables.items()
        ]
        st.dataframe(pd.DataFrame(summary_rows), use_container_width=True, hide_index=True)

    # --------------------------------------------------------------------
    # TAB 2 - Tables
    # --------------------------------------------------------------------
    with main_tabs[1]:
        if not tables:
            st.info("No table found in the schema.")
            return

        # Create a horizontal tab for each table
        table_tabs = st.tabs([f"{t}" for t in tables.keys()])

        for i, (table_name, table_info) in enumerate(tables.items()):
            with table_tabs[i]:
                row_count = table_info.get("row_count", "N/A")
                st.markdown(f"### {table_name}")
                st.markdown(f"**{row_count} rows**")
                
                # Table interpretation (if available)
                table_role = table_info.get("role")
                table_description = table_info.get("description")
                
                if table_role:
                    st.markdown(f"**Role :** {table_role}")
                
                if table_description:
                    st.markdown(f"**Description :** {table_description}")

                primary_key_data = table_info.get("primary_key")
                if isinstance(primary_key_data, list):
                    primary_keys = {str(pk) for pk in primary_key_data}
                elif primary_key_data:
                    primary_keys = {str(primary_key_data)}
                else:
                    primary_keys = set()

                foreign_keys_raw = table_info.get("foreign_keys", [])
                foreign_keys = {str(fk) for fk in foreign_keys_raw}
                foreign_keys |= {fk.split(".")[-1] for fk in foreign_keys_raw if isinstance(fk, str) and "." in fk}

                # === Table of columns ===
                columns = table_info.get("columns", {})
                col_data = [
                    {
                        "Column": name,
                        "Description": c.get("semantic_description", "-"),
                        "Type": c.get("type", "N/A"),
                        "Nullable": c.get("nullable"),
                        "Unique": c.get("unique"),
                        "PK": name in primary_keys,
                        "FK": name in foreign_keys,
                        "# Unique": str(c.get("unique_count")),
                        "# Null": str(c.get("null_count")),
                        "Min": str(c.get("min")) if c.get("min") is not None else "-",
                        "Max": str(c.get("max")) if c.get("max") is not None else "-",
                        "Mean": str(round(c["mean"], 2) if isinstance(c.get("mean"), (int, float)) else "-"),
                        "Std": str(round(c["std"], 2) if isinstance(c.get("std"), (int, float)) else "-"),
                    }
                    for name, c in columns.items()
                ]
                st.dataframe(pd.DataFrame(col_data), use_container_width=True, hide_index=True)

    # --------------------------------------------------------------------
    # TAB 3 - Relations
    # --------------------------------------------------------------------
    with main_tabs[2]:
        st.subheader("Relations between the tables")

        relationships = data.get("relationships", [])
        if relationships:
            rel_data = [
                {
                    "From table": r["from_table"],
                    "From column": r["from_column"],
                    "To table": r["to_table"],
                    "To column": r["to_column"],
                }
                for r in relationships
            ]
            st.dataframe(pd.DataFrame(rel_data), use_container_width=True, hide_index=True)
        else:
            st.info("No relation detected.")