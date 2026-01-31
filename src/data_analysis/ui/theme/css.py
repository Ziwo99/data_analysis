"""CSS injection for Streamlit theme styling."""


import streamlit as st
from data_analysis.ui.theme.colors import THEME_COLORS


def apply_theme_css() -> None:
    """Inject CSS styles based on theme colors."""
    st.markdown(f"""
    <style>
    /* ================================================================
       LAYOUT & BACKGROUND
       ================================================================ */
    html, body, .stApp, [data-testid="stAppViewContainer"], [data-testid="stMain"] {{
        background: radial-gradient(ellipse at top, #0f172a 0%, #020617 50%, #000 100%) !important;
    }}
    [data-testid="stSidebar"] {{
        background: linear-gradient(180deg, #0f172a 0%, #020617 100%) !important;
        border-right: 1px solid {THEME_COLORS["button_border"]} !important;
    }}
    [data-testid="stHeader"] {{
        display: none !important;
    }}
    [data-testid="stMainBlockContainer"] {{
        padding: 1rem 2rem !important;
    }}
    .block-container {{
        padding: 1rem 2rem !important;
    }}

    /* ================================================================
       TYPOGRAPHY
       ================================================================ */
    h1, h2, h3, h4, h5, h6 {{
        color: {THEME_COLORS["title"]} !important;
    }}
    h3 {{
        margin-top: 0rem !important;
        margin-bottom: 0rem !important;
    }}
    p:not([data-testid="stCodeBlock"] p):not(pre p):not(code p):not(div.stButton p):not([data-baseweb="tab"] p):not([data-testid="stExpander"] p),
    span:not([data-testid="stCodeBlock"] span):not(pre span):not(code span):not([class*="token"]):not([class*="hljs"]):not(div.stButton span):not([data-baseweb="tab"] span):not([data-testid="stExpander"] span),
    li:not([data-testid="stCodeBlock"] li):not(pre li):not(div.stButton li):not([data-baseweb="tab"] li):not([data-testid="stExpander"] li),
    label:not(div.stButton label):not([data-baseweb="tab"] label):not([data-testid="stExpander"] label) {{
        color: {THEME_COLORS["text_primary"]} !important;
    }}

    /* ================================================================
       BUTTONS
       ================================================================ */
    button[kind="primary"],
    button[data-testid="stBaseButton-primary"] {{
        background: linear-gradient(135deg, #38bdf8 0%, #22c55e 100%) !important;
        color: #020617 !important;
        border: none !important;
        font-weight: 600 !important;
        border-radius: 10px !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 15px rgba(56, 189, 248, 0.25) !important;
    }}
    button[kind="primary"]:hover:not(:disabled),
    button[data-testid="stBaseButton-primary"]:hover:not(:disabled) {{
        filter: brightness(1.1) !important;
        transform: translateY(-1px) !important;
        box-shadow: 0 6px 20px rgba(56, 189, 248, 0.35) !important;
    }}
    button[kind="secondary"],
    button[data-testid="stBaseButton-secondary"] {{
        background: {THEME_COLORS["button_secondary_bg"]} !important;
        color: {THEME_COLORS["button_secondary_text"]} !important;
        border: 1px solid {THEME_COLORS["button_secondary_border"]} !important;
        border-radius: 10px !important;
        transition: all 0.3s ease !important;
    }}
    button[kind="secondary"]:hover:not(:disabled),
    button[data-testid="stBaseButton-secondary"]:hover:not(:disabled) {{
        background: {THEME_COLORS["button_hover_bg"]} !important;
        border-color: {THEME_COLORS["button_hover_border"]} !important;
        color: {THEME_COLORS["button_hover_text"]} !important;
    }}
    div.stButton > button:disabled,
    button[data-testid="stBaseButton-primary"]:disabled,
    button[data-testid="stBaseButton-secondary"]:disabled,
    button[kind="primary"]:disabled,
    button[kind="secondary"]:disabled {{
        background: {THEME_COLORS["button_disabled_bg"]} !important;
        border-color: {THEME_COLORS["button_disabled_border"]} !important;
        color: {THEME_COLORS["button_disabled_text"]} !important;
        cursor: not-allowed !important;
        opacity: {THEME_COLORS["button_disabled_opacity"]} !important;
        box-shadow: none !important;
    }}

    /* ================================================================
       TABS
       ================================================================ */
    [data-baseweb="tab-list"] {{
        display: flex !important;
        justify-content: flex-start !important;
        align-items: flex-end !important;
        gap: 1.2rem !important;
        margin-top: 0rem !important;
        margin-bottom: 0rem !important;
        margin-left: 1.5rem !important;
    }}
    [data-testid="stTabs"] {{
        margin-top: 0rem !important;
        margin-bottom: 0rem !important;
    }}
    [data-baseweb="tab"] {{
        position: relative !important;
        font-size: 1.1rem !important;
        font-weight: 600 !important;
        color: {THEME_COLORS["tab_text_default"]} !important;
        background-color: transparent !important;
        border: none !important;
        border-radius: 0 !important;
        padding: 0.6rem 0 !important;
        margin: 0 !important;
        transition: color 0.2s ease-in-out, border-color 0.2s ease-in-out !important;
        box-shadow: none !important;
    }}
    [data-baseweb="tab"] p,
    [data-baseweb="tab"] span,
    [data-baseweb="tab"] * {{
        font-size: 1.2rem !important;
        margin: 0 !important;
        color: inherit !important;
    }}
    [data-baseweb="tab"][aria-selected="true"] {{
        color: {THEME_COLORS["tab_text_active"]} !important;
        border-bottom: {THEME_COLORS["tab_selector_width"]} solid {THEME_COLORS["tab_selector_color"]} !important;
    }}
    [data-baseweb="tab"][aria-selected="false"] {{
        color: {THEME_COLORS["tab_text_inactive"]} !important;
    }}
    [data-baseweb="tab"]:hover {{
        color: {THEME_COLORS["tab_text_active"]} !important;
    }}
    [data-baseweb="tab"]:active {{
        color: {THEME_COLORS["tab_text_active"]} !important;
        border-bottom: {THEME_COLORS["tab_selector_width"]} solid {THEME_COLORS["tab_selector_color"]} !important;
        transition: none !important;
    }}
    [data-baseweb="tab-border"] {{
        display: none !important;
    }}
    [data-baseweb="tab-highlight"] {{
        display: none !important;
    }}
    [data-baseweb="tab-panel"] {{
        background-color: {THEME_COLORS["tab_panel_bg"]} !important;
        border: {THEME_COLORS["tab_panel_border_width"]} solid {THEME_COLORS["tab_panel_border"]} !important;
        border-radius: {THEME_COLORS["tab_panel_border_radius"]} !important;
        padding: 10px 20px !important;
        margin-top: 0px !important;
        margin-bottom: 40px !important;
        box-shadow: 0 6px 20px {THEME_COLORS["tab_shadow"]} !important;
    }}
    [data-baseweb="tab-panel"] p,
    [data-baseweb="tab-panel"] span,
    [data-baseweb="tab-panel"] li {{
        color: {THEME_COLORS["text_primary"]} !important;
    }}
    
    /* ================================================================
       CONTENT TEXT SIZE (excluding tabs and expanders)
       ================================================================ */
    
    /* Increase font size for content in tab panels (but not tabs themselves) */
    [data-baseweb="tab-panel"] p:not([data-baseweb="tab"] p),
    [data-baseweb="tab-panel"] span:not([data-baseweb="tab"] span):not([data-baseweb="tab"] *),
    [data-baseweb="tab-panel"] li:not([data-baseweb="tab"] li) {{
        font-size: 1.15rem !important;
        line-height: 1.75 !important;
    }}
    
    /* Increase font size for main content (excluding tabs and expanders) */
    p:not([data-baseweb="tab"] p):not([data-testid="stExpander"] p):not([data-baseweb="tab-panel"] [data-baseweb="tab"] p),
    span:not([data-baseweb="tab"] span):not([data-testid="stExpander"] span):not([data-baseweb="tab-panel"] [data-baseweb="tab"] span):not([class*="token"]):not([class*="hljs"]),
    li:not([data-baseweb="tab"] li):not([data-testid="stExpander"] li):not([data-baseweb="tab-panel"] [data-baseweb="tab"] li) {{
        font-size: 1.15rem !important;
        line-height: 1.75 !important;
    }}
    
    /* Override for markdown containers in content (not in tabs/expanders) */
    [data-testid="stMarkdownContainer"]:not([data-baseweb="tab"] *):not([data-testid="stExpander"] *) p,
    [data-testid="stMarkdownContainer"]:not([data-baseweb="tab"] *):not([data-testid="stExpander"] *) span:not([data-baseweb="tab"] span),
    [data-testid="stMarkdownContainer"]:not([data-baseweb="tab"] *):not([data-testid="stExpander"] *) li {{
        font-size: 1.15rem !important;
        line-height: 1.75 !important;
    }}

    /* ================================================================
       TABS (SECONDARY/NESTED)
       ================================================================ */
    [data-baseweb="tab-panel"] [data-baseweb="tab-list"] {{
        margin-left: 1.5rem !important;
        gap: 0.8rem !important;
    }}
    [data-baseweb="tab-panel"] [data-baseweb="tab"] {{
        font-size: 0.95rem !important;
        font-weight: 500 !important;
        color: {THEME_COLORS["tab_secondary_text_default"]} !important;
        padding: 0.4rem 0.8rem !important;
        border-bottom: {THEME_COLORS["tab_secondary_selector_width"]} solid transparent !important;
    }}
    [data-baseweb="tab-panel"] [data-baseweb="tab"] p,
    [data-baseweb="tab-panel"] [data-baseweb="tab"] span,
    [data-baseweb="tab-panel"] [data-baseweb="tab"] * {{
        font-size: 0.95rem !important;
        color: inherit !important;
    }}
    [data-baseweb="tab-panel"] [data-baseweb="tab"][aria-selected="true"] {{
        color: {THEME_COLORS["tab_secondary_text_active"]} !important;
        border-bottom: {THEME_COLORS["tab_secondary_selector_width"]} solid {THEME_COLORS["tab_secondary_selector_color"]} !important;
    }}
    [data-baseweb="tab-panel"] [data-baseweb="tab"][aria-selected="false"] {{
        color: {THEME_COLORS["tab_secondary_text_inactive"]} !important;
    }}
    [data-baseweb="tab-panel"] [data-baseweb="tab"]:hover {{
        color: {THEME_COLORS["tab_secondary_text_active"]} !important;
    }}
    [data-baseweb="tab-panel"] [data-baseweb="tab"]:active {{
        color: {THEME_COLORS["tab_secondary_text_active"]} !important;
        border-bottom: {THEME_COLORS["tab_secondary_selector_width"]} solid {THEME_COLORS["tab_secondary_selector_color"]} !important;
        transition: none !important;
    }}
    [data-baseweb="tab-panel"] [data-baseweb="tab-panel"] {{
        background-color: {THEME_COLORS["tab_secondary_panel_bg"]} !important;
        border: {THEME_COLORS["tab_secondary_panel_border_width"]} solid {THEME_COLORS["tab_secondary_panel_border"]} !important;
        border-radius: {THEME_COLORS["tab_secondary_panel_border_radius"]} !important;
        padding: 15px 20px !important;
        margin-top: 10px !important;
        margin-bottom: 20px !important;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05) !important;
    }}

    /* ================================================================
       EXPANDERS
       ================================================================ */
    [data-testid="stExpander"] {{
        background: {THEME_COLORS["expander_bg"]} !important;
        border: 1px solid rgba(148, 163, 184, 0.3) !important;
        border-radius: 12px !important;
        margin-bottom: 1rem !important;
        box-shadow: 0 4px 15px {THEME_COLORS["expander_shadow"]} !important;
        overflow: hidden !important;
    }}
    [data-testid="stExpander"] > div {{
        background: transparent !important;
    }}
    [data-testid="stExpander"] > div:first-child {{
        background: linear-gradient(145deg, rgba(71, 85, 105, 0.9) 0%, rgba(51, 65, 85, 0.95) 100%) !important;
        border-bottom: 1px solid rgba(148, 163, 184, 0.2) !important;
        padding: 0.75rem 1rem !important;
        font-weight: 600 !important;
        color: {THEME_COLORS["expander_header_text"]} !important;
    }}
    [data-testid="stExpander"] > div:first-child *,
    [data-testid="stExpander"] > div:first-child p,
    [data-testid="stExpander"] > div:first-child span {{
        color: {THEME_COLORS["expander_header_text"]} !important;
    }}
    [data-testid="stExpander"] > div:first-child:hover {{
        background: linear-gradient(145deg, rgba(100, 116, 139, 0.9) 0%, rgba(71, 85, 105, 0.95) 100%) !important;
    }}
    [data-testid="stExpander"] summary,
    [data-testid="stExpander"] summary *,
    [data-testid="stExpander"] summary p,
    [data-testid="stExpander"] summary span,
    [data-testid="stExpander"] summary div,
    [data-testid="stExpander"] summary [data-testid="stMarkdownContainer"],
    [data-testid="stExpander"] summary [data-testid="stMarkdownContainer"] p,
    [data-testid="stExpander"] summary [data-testid="stMarkdownContainer"] * {{
        font-size: 1.1rem !important;
        font-weight: 600 !important;
        line-height: 1.5 !important;
    }}
    [data-testid="stExpander"] > div:last-child {{
        padding: 1rem 1.25rem !important;
        background: {THEME_COLORS["expander_content_bg"]} !important;
        color: {THEME_COLORS["expander_content_text"]} !important;
    }}
    [data-testid="stExpander"] > div:last-child *,
    [data-testid="stExpander"] > div:last-child p,
    [data-testid="stExpander"] > div:last-child span {{
        color: {THEME_COLORS["expander_content_text"]} !important;
    }}
    [data-testid="stExpander"] svg {{
        color: #38bdf8 !important;
        width: 1.2rem !important;
        height: 1.2rem !important;
    }}

    /* ================================================================
       CODE BLOCKS
       ================================================================ */
    [data-testid="stCode"],
    [data-testid="stCodeBlock"] {{
        background-color: {THEME_COLORS["code_bg"]} !important;
        border-radius: 8px !important;
        padding: 1rem !important;
        margin: 0.5rem 0 !important;
    }}
    [data-testid="stCode"] pre,
    [data-testid="stCodeBlock"] pre,
    pre {{
        background-color: {THEME_COLORS["code_bg"]} !important;
        border-radius: 8px !important;
        padding: 1rem !important;
        margin: 0.5rem 0 !important;
    }}
    [data-testid="stCode"] *,
    [data-testid="stCodeBlock"] *,
    [data-testid="stCode"] pre *,
    [data-testid="stCode"] code *,
    [data-testid="stCodeBlock"] pre *,
    [data-testid="stCodeBlock"] code *,
    pre *,
    pre code * {{
        color: {THEME_COLORS["code_text"]} !important;
    }}
    [data-testid="stCode"] code > span:not([class*="token"]),
    [data-testid="stCodeBlock"] code > span:not([class*="token"]),
    pre code > span:not([class*="token"]) {{
        color: {THEME_COLORS["code_text"]} !important;
    }}
    [data-testid="stCode"] .token.comment,
    [data-testid="stCodeBlock"] .token.comment,
    pre .token.comment {{
        color: {THEME_COLORS["code_comment"]} !important;
    }}
    [data-testid="stCode"] .token.string,
    [data-testid="stCodeBlock"] .token.string,
    pre .token.string {{
        color: {THEME_COLORS["code_string"]} !important;
    }}
    [data-testid="stCode"] .token.keyword,
    [data-testid="stCodeBlock"] .token.keyword,
    pre .token.keyword {{
        color: {THEME_COLORS["code_keyword"]} !important;
    }}
    [data-testid="stCode"] .token.function,
    [data-testid="stCodeBlock"] .token.function,
    pre .token.function {{
        color: {THEME_COLORS["code_function"]} !important;
    }}
    [data-testid="stCode"] .token.number,
    [data-testid="stCodeBlock"] .token.number,
    pre .token.number {{
        color: {THEME_COLORS["code_number"]} !important;
    }}

    /* ================================================================
       DATAFRAMES & TABLES
       ================================================================ */
    [data-testid="stDataFrame"] {{
        background: rgba(15, 23, 42, 0.8) !important;
        border-radius: 12px !important;
        overflow: hidden !important;
        border: 1px solid rgba(56, 189, 248, 0.15) !important;
    }}
    [data-testid="stDataFrame"] > div {{
        background: transparent !important;
    }}

    /* ================================================================
       SELECTBOX
       ================================================================ */
    [data-testid="stSelectbox"] > div > div {{
        background-color: rgba(15, 23, 42, 0.8) !important;
        border-color: rgba(56, 189, 248, 0.3) !important;
        color: #e2e8f0 !important;
        border-radius: 8px !important;
    }}
    [data-testid="stSelectbox"] label {{
        color: #94a3b8 !important;
    }}

    /* ================================================================
       METRICS & INFO
       ================================================================ */
    [data-testid="stMetric"] {{
        background: linear-gradient(145deg, rgba(30, 41, 59, 0.6) 0%, rgba(15, 23, 42, 0.8) 100%) !important;
        border: 1px solid rgba(56, 189, 248, 0.2) !important;
        border-radius: 12px !important;
        padding: 1rem !important;
    }}
    [data-testid="stMetric"] label {{
        color: #94a3b8 !important;
    }}
    [data-testid="stMetric"] [data-testid="stMetricValue"] {{
        color: #38bdf8 !important;
    }}
    [data-testid="stAlert"] {{
        background: rgba(30, 41, 59, 0.8) !important;
        border-radius: 10px !important;
    }}
    [data-testid="stMarkdownContainer"] {{
        color: #e2e8f0 !important;
    }}
    hr {{
        border-color: rgba(71, 85, 105, 0.3) !important;
    }}
    </style>
    """, unsafe_allow_html=True)