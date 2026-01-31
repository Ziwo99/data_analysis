"""Display modules for the different sections of the user interface."""


from .raw_schema_section import display_raw_schema
from .schema_section import display_schema_summary
from .business_section import display_business_analysis
from .query_section import display_queries_analysis
from .query_analysis_section import display_query_analysis
from .visualization_section import display_visualizations_analysis
from .confidentiality_section import display_confidentiality_test
from .display_section import (
    AGENT_DISPLAY_NAMES,
    AVAILABLE_WINDOWS,
    MAX_ATTEMPTS,
    MONO_AGENT_DISPLAY_NAMES,
    MONO_AVAILABLE_WINDOWS,
    MONO_WINDOW_DISPLAY_NAMES,
    WINDOW_DISPLAY_NAMES,
    display_content,
)


__all__ = [
    # Section displays
    "display_raw_schema",
    "display_schema_summary",
    "display_business_analysis",
    "display_queries_analysis",
    "display_query_analysis",
    "display_visualizations_analysis",
    "display_confidentiality_test",
    "display_content",
    # Section configuration
    "AVAILABLE_WINDOWS",
    "WINDOW_DISPLAY_NAMES",
    "AGENT_DISPLAY_NAMES",
    "MONO_AVAILABLE_WINDOWS",
    "MONO_WINDOW_DISPLAY_NAMES",
    "MONO_AGENT_DISPLAY_NAMES",
    "MAX_ATTEMPTS",
]