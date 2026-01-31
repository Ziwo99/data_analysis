"""User interface module for Streamlit application."""


from data_analysis.system.utils.analysis_status import DEFAULT_AGENTS_STATUS
from .components import (
    get_icon_html,
    get_status_box_html,
    initialize_session_state,
    load_agents_data,
    render_navigation_bar,
    reset_analysis_status,
)
from .sections import (
    AVAILABLE_WINDOWS,
    WINDOW_DISPLAY_NAMES,
)
from .theme import STATUS_CONFIG
from .sections import (
    display_content,
    display_schema_summary,
)
from .theme import (
    THEME_COLORS,
    apply_theme_css,
)
from .views import (
    render_analysis_page,
    render_landing_page,
)


__all__ = [
    # Configuration
    "AVAILABLE_WINDOWS",
    "WINDOW_DISPLAY_NAMES",
    "STATUS_CONFIG",
    "DEFAULT_AGENTS_STATUS",
    # Theme
    "THEME_COLORS",
    "apply_theme_css",
    # Components
    "render_navigation_bar",
    "initialize_session_state",
    "load_agents_data",
    "get_icon_html",
    "get_status_box_html",
    "reset_analysis_status",
    # Sections
    "display_schema_summary",
    "display_content",
    # Views
    "render_landing_page",
    "render_analysis_page",
]