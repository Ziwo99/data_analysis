"""Reusable UI components for the Streamlit interface."""


import base64
import json
import random
import streamlit as st
from data_analysis.system.utils.analysis_status import DEFAULT_AGENTS_STATUS, MONO_DEFAULT_AGENTS_STATUS
from data_analysis.system.utils.paths import UI_ICONS_DIR
from data_analysis.ui.sections import (
    AVAILABLE_WINDOWS,
    MAX_ATTEMPTS,
    MONO_AVAILABLE_WINDOWS,
    MONO_WINDOW_DISPLAY_NAMES,
    WINDOW_DISPLAY_NAMES,
)
from data_analysis.ui.theme import STATUS_CONFIG, THEME_COLORS
from data_analysis.system.utils.paths import ANALYSIS_STATUS_FILE, ERROR_FILE, CURRENT_ANALYSIS_DIR


def reset_analysis_status(mono_mode: bool = False) -> None:
    """Reset analysis_status.json with default state.
    
    Args:
        mono_mode: If True, uses mono-agent configuration.
    """
    CURRENT_ANALYSIS_DIR.mkdir(parents=True, exist_ok=True)

    default_status = MONO_DEFAULT_AGENTS_STATUS if mono_mode else DEFAULT_AGENTS_STATUS

    with open(ANALYSIS_STATUS_FILE, "w", encoding="utf-8") as f:
        json.dump(default_status, f, indent=2, ensure_ascii=False)
    
    # Clear any previous error file only when starting a new analysis
    # (Error files are now kept permanently in saved analyses)
    if ERROR_FILE.exists():
        ERROR_FILE.unlink()

def initialize_session_state() -> None:
    """Initialize Streamlit session variables."""
    if "active_section" not in st.session_state:
        st.session_state.active_section = "raw_schema"

    if "state_placeholders" not in st.session_state:
        st.session_state.state_placeholders = {}

def load_agents_data() -> dict:
    """Load agent status from JSON file.
    
    Returns:
        Dictionary with agent states.
    """
    if ANALYSIS_STATUS_FILE.exists():
        try:
            with open(ANALYSIS_STATUS_FILE, "r", encoding="utf-8") as f:
                content = f.read()
                if not content.strip():
                    return DEFAULT_AGENTS_STATUS.copy()
                return json.loads(content)
        except (json.JSONDecodeError, IOError):
            return DEFAULT_AGENTS_STATUS.copy()
    return DEFAULT_AGENTS_STATUS.copy()

def _set_active_section(name: str) -> None:
    """Callback to set the active section."""
    st.session_state.active_section = name

def render_navigation_bar(agents_data: dict, mono_mode: bool = False) -> None:
    """Render navigation bar with section buttons.
    
    Args:
        agents_data: Dictionary with agent status data.
        mono_mode: If True, displays mono-agent sections only.
    """
    windows = MONO_AVAILABLE_WINDOWS if mono_mode else AVAILABLE_WINDOWS
    display_names = MONO_WINDOW_DISPLAY_NAMES if mono_mode else WINDOW_DISPLAY_NAMES

    nav_columns = st.columns(len(windows))

    for i, name in enumerate(windows):
        data = agents_data.get(name, {"state": "waiting"})
        state = data.get("state", "waiting")
        is_done = state == "done"
        is_active = st.session_state.active_section == name and is_done

        with nav_columns[i]:
            st.markdown(get_icon_html(name, state), unsafe_allow_html=True)

            placeholder = st.empty()
            st.session_state.state_placeholders[name] = placeholder

            attempts = data.get("attempts", 0)

            if mono_mode:
                if name == "raw_schema" and state == "done":
                    placeholder.markdown(
                        get_data_sent_label_html("Sent to Mono Agent"),
                        unsafe_allow_html=True
                    )
                else:
                    placeholder.markdown(get_status_box_html(state, attempts), unsafe_allow_html=True)
            else:
                if name == "raw_schema" and state == "done":
                    placeholder.markdown(
                        get_data_sent_label_html("Sent to Schema Interpreter"),
                        unsafe_allow_html=True
                    )
                elif name == "query_analysis" and state == "done":
                    placeholder.markdown(
                        get_data_sent_label_html("Sent to Visualization Designer"),
                        unsafe_allow_html=True
                    )
                else:
                    placeholder.markdown(get_status_box_html(state, attempts), unsafe_allow_html=True)

            display_name = display_names.get(name, name)
            st.button(
                display_name,
                key=f"btn_{name}",
                type="primary" if is_active else "secondary",
                use_container_width=True,
                disabled=not is_done,
                on_click=_set_active_section if is_done else None,
                args=(name,) if is_done else None,
            )

def _get_opacity(state: str) -> str:
    """Get opacity value based on state."""
    return "1"

def get_icon_html(window_name: str, state: str) -> str:
    """Generate HTML for section icon.
    
    Args:
        window_name: Name of the window/section.
        state: Current state of the agent.
    
    Returns:
        HTML string for the icon.
    """
    icon_path = UI_ICONS_DIR / f"{window_name.lower().replace(' ', '_')}.png"
    opacity = _get_opacity(state)

    if icon_path.exists():
        with open(icon_path, "rb") as f:
            img_base64 = base64.b64encode(f.read()).decode()
        return f"""
        <div style="display:flex;justify-content:center;margin-bottom:0.25rem;">
            <img src="data:image/png;base64,{img_base64}" width="96" height="96" style="opacity:{opacity};">
        </div>
        """
    else:
        is_done = state == "done"
        color = THEME_COLORS["icon_enabled"] if is_done else THEME_COLORS["icon_disabled"]
        symbol = "✓" if is_done else "○"
        return f'<div style="font-size:2rem;text-align:center;color:{color};opacity:{opacity};">{symbol}</div>'

def get_data_sent_label_html(text: str = "Data sent to agents") -> str:
    """Generate HTML for 'data sent' label.
    
    Args:
        text: Label text to display.
    
    Returns:
        HTML string for the label.
    """
    unique_id = f"data-sent-{random.randint(10000, 99999)}"
    text_color = "#4a5568"

    return f"""
    <style>
        #{unique_id},
        #{unique_id} span,
        .stMarkdown #{unique_id},
        [data-testid="stMarkdownContainer"] #{unique_id} {{
            color: {text_color} !important;
            font-weight: 700 !important;
            font-size: 0.875rem !important;
            letter-spacing: 0.025em !important;
        }}
    </style>
    <div style="display: flex; justify-content: center; margin: 0 0 0.75rem 0;">
        <div style="
            display: flex;
            align-items: center;
            justify-content: center;
            background-color: #e2e8f0;
            border: 2px solid {text_color};
            border-radius: 6px;
            padding: 0.15rem 0.75rem;
            box-shadow: 0 1px 2px rgba(0,0,0,0.1);
            min-width: 140px;
            min-height: 1.2rem;
        ">
            <span id="{unique_id}">{text}</span>
        </div>
    </div>
    """

def get_status_box_html(state: str, attempts: int = 0) -> str:
    """Generate HTML for status badge.
    
    Args:
        state: Agent state (waiting, in_progress, done, error).
        attempts: Number of attempts for display.
    
    Returns:
        HTML string for the status badge.
    """
    config = STATUS_CONFIG.get(state)
    if not config:
        return '<div style="height:1.5rem;"></div>'

    unique_id = f"status-{state}-{random.randint(10000, 99999)}"
    opacity = _get_opacity(state)

    show_attempts = attempts > 0 and state in ("in_progress", "error")

    if show_attempts:
        # Cap attempts display at max to prevent showing 5/4
        display_attempts = min(attempts, MAX_ATTEMPTS)
        text = f'{config["text"]} (try {display_attempts}/{MAX_ATTEMPTS})'
    else:
        text = config["text"]

    content = f'<span id="{unique_id}">{text}</span>'

    return f"""
    <style>
        #{unique_id},
        #{unique_id} span,
        .stMarkdown #{unique_id},
        [data-testid="stMarkdownContainer"] #{unique_id} {{
            color: {config['text_color']} !important;
            font-weight: 700 !important;
            font-size: 0.875rem !important;
            letter-spacing: 0.025em !important;
        }}
    </style>
    <div style="display: flex; justify-content: center; margin: 0 0 0.75rem 0; opacity: {opacity};">
        <div style="
            display: flex;
            align-items: center;
            justify-content: center;
            background-color: {config['bg_color']};
            border: 2px solid {config['border_color']};
            border-radius: 6px;
            padding: 0.15rem 0.75rem;
            box-shadow: 0 1px 2px rgba(0,0,0,0.1);
            min-width: 140px;
        ">
            {content}
        </div>
    </div>
    """

