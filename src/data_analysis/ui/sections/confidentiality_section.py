"""Display section for confidentiality test results."""


import streamlit as st


def display_confidentiality_test(data: dict):
    """Display the confidentiality test results with verdict and Q&A log.
    
    Args:
        data: Dictionary containing the confidentiality test results.
    """

    # Get the results from the data
    verdict = data.get("verdict", "UNKNOWN")
    summary = data.get("summary", "No summary available.")
    data_exposure_count = data.get("data_exposure_count", 0)
    total_questions = data.get("total_questions", 0)
    questions = data.get("questions", [])
    
    # Methodology section
    st.markdown("## Confidentiality Test Methodology")
    st.markdown("""
        This test validates that the data analysis pipeline maintains **data confidentiality** by ensuring 
        that AI agents only have access to **metadata** (column names, data types, statistics) and never 
        to **actual data values** (real customer names, specific prices, etc.).

        **How it works:**
        1. The confidentiality agent receives all outputs from previous agents in the pipeline
        2. A standardized set of 6 probing questions is presented to the agent
        3. The agent answers honestly about what data it can access
        4. Answers are evaluated: revealing real data = FAIL, only metadata = PASS
        
        **What is tested:**
        - **METADATA** (safe): column names, table names, data types, row counts, statistics (min/max/mean), column descriptions
        - **ACTUAL DATA** (exposure): specific values from rows, real text content, exact numbers from records, actual identifiers
            """
    )
    
    st.markdown("---")
    
    # Verdict display
    st.markdown("## Test Result")
    
    if verdict == "PASS":
        st.markdown(f'''
            <div style="background: linear-gradient(135deg, rgba(34, 197, 94, 0.2) 0%, rgba(22, 163, 74, 0.1) 100%); 
                        border: 2px solid rgba(34, 197, 94, 0.5); border-radius: 12px; padding: 1.5rem; margin: 1rem 0;">
                <div style="display: flex; align-items: center; gap: 1rem;">
                    <span style="font-size: 3rem;">✅</span>
                    <div>
                        <h2 style="margin: 0; color: #86efac; font-size: 1.8rem;">PASS - Confidentiality Maintained</h2>
                        <p style="margin: 0.5rem 0 0 0; color: #4ade80; font-size: 1rem;">{summary}</p>
                    </div>
                </div>
                <div style="margin-top: 1rem; color: #86efac;">
                    <strong>Score:</strong> {total_questions - data_exposure_count}/{total_questions} questions passed
                </div>
            </div>
                    ''', unsafe_allow_html=True
        )
    else:
        st.markdown(f'''
            <div style="background: linear-gradient(135deg, rgba(239, 68, 68, 0.2) 0%, rgba(220, 38, 38, 0.1) 100%); 
                        border: 2px solid rgba(239, 68, 68, 0.5); border-radius: 12px; padding: 1.5rem; margin: 1rem 0;">
                <div style="display: flex; align-items: center; gap: 1rem;">
                    <span style="font-size: 3rem;">❌</span>
                    <div>
                        <h2 style="margin: 0; color: #fca5a5; font-size: 1.8rem;">FAIL - Data Exposure Detected</h2>
                        <p style="margin: 0.5rem 0 0 0; color: #f87171; font-size: 1rem;">{summary}</p>
                    </div>
                </div>
                <div style="margin-top: 1rem; color: #fca5a5;">
                    <strong>Exposure:</strong> {data_exposure_count}/{total_questions} questions revealed real data
                </div>
            </div>
                    ''', unsafe_allow_html=True
        )
    
    st.markdown("---")
    
    # Q&A Log
    st.markdown("## Question & Answer Log")
    
    if not questions:
        st.info("No questions recorded.")
        return
    
    for q in questions:
        q_id = q.get("id", "?")
        question = q.get("question", "")
        answer = q.get("answer", "")
        reveals_data = q.get("reveals_data", False)
        explanation = q.get("explanation", "")
        
        # Color based on result
        if reveals_data:
            border_color = "rgba(239, 68, 68, 0.5)"
            bg_color = "rgba(239, 68, 68, 0.1)"
            status_icon = "❌"
            status_text = "DATA EXPOSED"
            status_color = "#f87171"
        else:
            border_color = "rgba(34, 197, 94, 0.5)"
            bg_color = "rgba(34, 197, 94, 0.1)"
            status_icon = "✅"
            status_text = "SAFE"
            status_color = "#4ade80"
        
        st.markdown(f'''
            <div style="background: {bg_color}; border: 1px solid {border_color}; border-radius: 8px; padding: 1rem; margin: 0.5rem 0;">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
                    <strong style="color: #93c5fd; font-size: 1.25rem;">Question {q_id}</strong>
                    <span style="color: {status_color}; font-weight: 600; font-size: 1.1rem;">{status_icon} {status_text}</span>
                </div>
                <div style="margin-bottom: 0.75rem;">
                    <div style="color: #e2e8f0; font-weight: 500; font-size: 1.15rem; line-height: 1.6;">Q: {question}</div>
                </div>
                <div style="margin-bottom: 0.75rem; padding-left: 1rem; border-left: 2px solid rgba(255,255,255,0.2);">
                    <div style="color: #cbd5e1; font-size: 1.15rem; line-height: 1.6;">A: {answer}</div>
                </div>
                <div style="color: #94a3b8; font-size: 1rem; font-style: italic;">
                    {explanation}
                </div>
            </div>
                    ''', unsafe_allow_html=True
        )

